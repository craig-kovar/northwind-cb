# Northwind Data Model on Couchbase

This repository documents migrating the Northwind data model from an RDBMS system to Couchbase.

This process is implemented in two different phases to highlight the flexibility and design decisions of NoSQL and Couchbase in particular.

## Table of content

* [Data Model](#data-model)
* [Migrating Stored Procedures](#migrating-stored-procedures)
  - [CustOrderHist Lift and Shift](#custorderhist-lift-and-shift-approach)
  - [CustOrderHist Denormalized](#custorderhist-denormalized)
* [Appendix](#appendix)


## Data model

### RDBMS Data model

This is the RDBMS data model that was used for this exercise.

![RDBMS Data Model](./docs/images/RDBMS_Model.png)

### Couchbase Phase 1 - Lift and Shift

With this approach we kept the data model consistent with the RDBMS model and set up the following scopes and collections to map to the existing schema and tables.

![CB Phase 1](./docs/images/CB-Phase-1.png)


### Couchbase Phase 2 - Denormalize the Data

In this approach we take advantage of the document structure of Couchbase.  In this example we denormalize the data into the following document types:

- Reference Data
- Employee Data
- Order Data
- Customer Data

The **Reference Data** is comprised of the Product information with the following example document

![Sample Product JSON Document](./docs/images/Product_JSON.png)

The **Employee Data** is the denormalized data of Employee, Territories, and Region from the SQL Server model.  A sample document for employee is shown below

![Sample Employee JSON Document](./docs/images/Employee_JSON.png)

The **Customer Data** includes the customer information as well as top level items for each order and line item.  The top level JSON document is structured as shown below

![Sample Customer Top Level JSON Document](./docs/images/Customer_Top_JSON.png)

The orders array contains top level order information for the customer as shown in the below image

![Customer Orders Array](./docs/images/Customer_Orders_JSON.png)

And finally the **Orders Data** this is the largest document which contains full information for not just the Order,  but the products for each line item,  the employee involved in the order,  the shipping company, etc...

An example of the top level document is shown below

![Order Top Level Document](./docs/images/Order_Top_JSON.png)

The _employee_ object is the same Employee data that was previously documented.  The _shipper_ object is shown below

![Order Shipper Json](./docs/images/Order_Shipper_JSON.png)

And finally the LineItems which contain all the product information for each line item in this order.  An example of this is shown below

![Order Line Items Json](./docs/images/Order_Line_JSON.png)

## Migrating Stored Procedures

In this section we discuss existing stored procedures in SQL Server and how they are translated to Couchbase as both a Lift and Shift as well as a denormalized document model.

### Stored Procedure - CustOrderHistory

In this stored procedure we get all the products and the total number that a customer has ordered.

The stored procedure is originally defined as follows:

![CustOrderHistory](./docs/images/sp_custorderhist.png)

This results in the following results for CustomerID = "ALFKI"

![CustOrderHistory Results](./docs/images/sp_custorderhist_results.png)

#### CustOrderHist Lift and Shift approach

The first step to lift and shift is to write this query using **SQL++**.  The query would now look like the following:

![CustOrderHistory Couchbase Lift and Shift](./docs/images/sp_cb_custordhist_lift.png)

We also created the following indexes to support our queries.  ***As a side note this could be further optimized using USE KEYS but this is the most RDBMS approach***

* CREATE INDEX `idx_customer_custid` ON `Northwind`.`LiftAndShift`.`Customers`(`CustomerID`)
* CREATE INDEX `idx_orders_custid` ON `Northwind`.`LiftAndShift`.`Orders`(`CustomerID`)
* CREATE INDEX `idx_orders_orderid` ON `Northwind`.`LiftAndShift`.`Orders`(`OrderID`)
* CREATE INDEX `idx_ordersdetails_orderid` ON `Northwind`.`LiftAndShift`.`OrderDetails`(`OrderID`)
* CREATE INDEX `idx_ordersdetails_prodid` ON `Northwind`.`LiftAndShift`.`OrderDetails`(`ProductID`)
* CREATE INDEX `idx_products_prodid` ON `Northwind`.`LiftAndShift`.`Products`(`ProductID`,`ProductName`)

With this updated query we can now define a User Defined Function as shown below

![User Defined Function CustomerOrderHistory](./docs/images/udf-cb-custorderhist.png)

This function can than be run as follows

![Customer Order History User Defined Function Results](./docs/images/udf-custorderhist-results.png)

***Alternatively we can make this a named prepared statement as follows***

![Named Prepared CustOrderHist](./docs/images/np-custorder-hist.png)

Which can then be executed as follows (We need to set the named parameter customerId to the value we want to pass in either the SDK, Statement, or UI).  In this case we set it in the UI to "ALFKI"

![Named Prepared CustOrderHist Results](./docs/images/np-custorderhist-results.png)


#### CustOrderHist Denormalized

As we noted in the [Data Model](#data-model) section above; with this approach we included all the top level order information with our customer document.  This allows us to re-write this stored procedure with out doing any joins.  The query can be re-written as follows in SQL++

![CustOrderHist with denormalized model](./docs/images/cb-denorm-custorderhist.png)

Additionally we can then convert this statement to a named **prepared statement** or a **User Defined Function (UDF)** exactly the same way we did this with the LiftAndShift approach. Either way this query gives us the same results as shown below, and with improved performance going from ~10 ms to ~3 ms in our shared test environment

![Denormalized CustOrderHistory Results](./docs/images/cb-denorm-coh-results.png)


## Appendix

### Customer Order History Statements
> CREATE FUNCTION CustOrderHistory(customerId) { (SELECT p.ProductName,
       SUM(od.Quantity) AS Total
FROM Northwind.LiftAndShift.Customers c
    JOIN Northwind.LiftAndShift.Orders o ON (c.CustomerID = o.CustomerID)
    JOIN Northwind.LiftAndShift.OrderDetails od ON (od.OrderID = o.OrderID)
    JOIN Northwind.LiftAndShift.Products p ON (od.ProductID = p.ProductID)
WHERE c.CustomerID = customerId
GROUP BY p.ProductName
ORDER BY p.ProductName) }

> SELECT p.ProductName,
       SUM(od.Quantity) AS Total
FROM Northwind.LiftAndShift.Customers c
    JOIN Northwind.LiftAndShift.Orders o ON (c.CustomerID = o.CustomerID)
    JOIN Northwind.LiftAndShift.OrderDetails od ON (od.OrderID = o.OrderID)
    JOIN Northwind.LiftAndShift.Products p ON (od.ProductID = p.ProductID)
WHERE c.CustomerID = $CustomerID
GROUP BY p.ProductName
ORDER BY p.ProductName ASC /* Order by ProductName to match order from RDBMS */

> prepare myCustOrderHist as
SELECT p.ProductName,
       SUM(od.Quantity) AS Total
FROM Northwind.LiftAndShift.Customers c
    JOIN Northwind.LiftAndShift.Orders o ON (c.CustomerID = o.CustomerID)
    JOIN Northwind.LiftAndShift.OrderDetails od ON (od.OrderID = o.OrderID)
    JOIN Northwind.LiftAndShift.Products p ON (od.ProductID = p.ProductID)
WHERE c.CustomerID = $CustomerID
GROUP BY p.ProductName
ORDER BY p.ProductName

> SELECT myproducts.ProductName,
       SUM(myproducts.Quantity) AS Total
FROM Northwind.Denormalized.Customers c USE KEYS ["ALFKI"]
       UNNEST Orders myorders
       UNNEST myorders.Products myproducts
GROUP BY myproducts.ProductName
ORDER BY myproducts.ProductName ASC
