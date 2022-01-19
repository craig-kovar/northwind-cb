# Northwind Data Model on Couchbase

This repository documents migrating the Northwind data model from an RDBMS system to Couchbase.

This process is implemented in two different phases to highlight the flexibility and design decisions of NoSQL and Couchbase in particular.

## Table of content

* [Data Model](#data-model)
* [Migrating Stored Procedures](#migrating-stored-procedures)


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
