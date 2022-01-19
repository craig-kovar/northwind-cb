import _ctypes
import json
import re
import argparse


class OneDictPerLine(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        if not isinstance(self.value, list):
            return repr(self.value)
        else:  # Sort the representation of any dicts in the list.
            reps = ('{{{}}}'.format(', '.join(
                ('{!r}: {}'.format(k, v) for k, v in sorted(v.items()))
            )) if isinstance(v, dict)
                    else
                    repr(v) for v in self.value)
            return '[' + ',\n'.join(reps) + ']'


def di(obj_id):
    """ Reverse of id() function. """
    # from https://stackoverflow.com/a/15012814/355230
    return _ctypes.PyObj_FromPtr(obj_id)


class MyEncoder(json.JSONEncoder):
    FORMAT_SPEC = "@@{}@@"
    regex = re.compile(FORMAT_SPEC.format(r"(\d+)"))

    def default(self, obj):
        return (self.FORMAT_SPEC.format(id(obj)) if isinstance(obj, OneDictPerLine)
                else super(MyEncoder, self).default(obj))

    def encode(self, obj):
        format_spec = self.FORMAT_SPEC  # Local var to expedite access.
        json_repr = super(MyEncoder, self).encode(obj)  # Default JSON repr.

        # Replace any marked-up object ids in the JSON repr with the value
        # returned from the repr() of the corresponding Python object.
        for match in self.regex.finditer(json_repr):
            id = int(match.group(1))
            # Replace marked-up id with actual Python object repr().
            json_repr = json_repr.replace(
                '"{}"'.format(format_spec.format(id)), repr(di(id)))

        return json_repr


# Define methods to load the data
def load_categories():
    try:
        ret_categories = {}
        f = open(args.path + "/categories.csv", "r", encoding='utf8')
        # Skip the header line
        next(f)
        for line in f:
            tmp_dict = {}
            line = line.strip()
            tokens = line.split(";")
            tmp_dict["CategoryID"] = tokens[0]
            tmp_dict["CategoryName"] = tokens[1]
            tmp_dict["Description"] = tokens[2]
            tmp_dict["Picture"] = tokens[3]

            ret_categories[tokens[0]] = tmp_dict
    except:
        print("Unable to process categories")
    finally:
        f.close()

    return ret_categories


def load_products():
    try:
        ret_values = {}
        f = open(args.path + "/products.csv", "r", encoding='utf8')
        # Skip the header line
        next(f)
        for line in f:
            tmp_dict = {}
            line = line.strip()
            tokens = line.split(",")
            tmp_dict["ProductID"] = tokens[0]
            tmp_dict["ProductName"] = tokens[1]
            tmp_dict["SupplierID"] = tokens[2]
            tmp_dict["CategoryID"] = tokens[3]
            tmp_dict["QuantityPerUnit"] = tokens[4]
            tmp_dict["UnitPrice"] = float(tokens[5])
            tmp_dict["UnitsInStock"] = int(tokens[6])
            tmp_dict["UnitsOnOrder"] = int(tokens[7])
            tmp_dict["ReorderLevel"] = int(tokens[8])
            tmp_dict["Discontinued"] = int(tokens[9])

            ret_values[tokens[0]] = tmp_dict
    except:
        print("Unable to process products")
    finally:
        f.close()

    return ret_values


def load_suppliers():
    try:
        ret_values = {}
        f = open(args.path + "/suppliers.csv", "r", encoding='utf8')
        # Skip the header line
        next(f)
        for line in f:
            tmp_dict = {}
            line = line.strip()
            tokens = line.split(",")
            tmp_dict["SupplierID"] = tokens[0]
            tmp_dict["CompanyName"] = tokens[1]
            tmp_dict["ContactName"] = tokens[2]
            tmp_dict["ContactTitle"] = tokens[3]
            tmp_dict["Address"] = tokens[4]
            tmp_dict["City"] = tokens[5]
            if tokens[6] != "NULL":
                tmp_dict["Region"] = tokens[6]
            tmp_dict["PostalCode"] = tokens[7]
            tmp_dict["Country"] = tokens[8]
            if tokens[9] != "NULL":
                tmp_dict["Phone"] = tokens[9]
            if tokens[10] != "NULL":
                tmp_dict["Fax"] = tokens[10]
            if tokens[11] != "NULL":
                tmp_dict["HomePage"] = tokens[11]

            ret_values[tokens[0]] = tmp_dict
    except:
        print("Unable to process suppliers")
    finally:
        f.close()

    return ret_values


def load_employees():
    try:
        ret_values = {}
        f = open(args.path + "/employees.csv", "r", encoding='utf8')
        # Skip the header line
        next(f)
        for line in f:
            tmp_dict = {}
            line = line.strip()
            tokens = line.split(",")
            tmp_dict["EmployeeID"] = tokens[0]
            tmp_dict["LastName"] = tokens[1]
            tmp_dict["FirstName"] = tokens[2]
            tmp_dict["Title"] = tokens[3]
            tmp_dict["TitleOfCourtesy"] = tokens[4]
            tmp_dict["BirthDate"] = tokens[5].split(" ")[0]
            tmp_dict["HireDate"] = tokens[6].split(" ")[0]
            tmp_dict["Address"] = tokens[7]
            tmp_dict["City"] = tokens[8]
            if tokens[9] != "NULL":
                tmp_dict["Region"] = tokens[9]
            tmp_dict["PostalCode"] = tokens[10]
            tmp_dict["Country"] = tokens[11]
            tmp_dict["HomePhone"] = tokens[12]
            tmp_dict["Extension"] = tokens[13]
            tmp_dict["Photo"] = tokens[14]
            tmp_dict["Notes"] = tokens[15]
            if tokens[16] != "NULL":
                tmp_dict["ReportsTo"] = tokens[16]
            tmp_dict["PhotoPath"] = tokens[17]


            ret_values[tokens[0]] = tmp_dict
    except:
        print("Unable to process employee")
    finally:
        f.close()

    return ret_values


def load_employee_territories():
    try:
        ret_values = {}
        f = open(args.path + "/employee-territories.csv", "r", encoding='utf8')
        # Skip the header line
        next(f)
        for line in f:
            line = line.strip()
            tokens = line.split(",")
            emp_id = tokens[0]
            terr_id = tokens[1]

            terr_ids = ret_values.get(emp_id)
            if terr_ids is None:
                terr_ids = [terr_id]
            else:
                terr_ids.append(terr_id)

            ret_values[emp_id] = terr_ids
    except:
        print("Unable to process employee territories")
    finally:
        f.close()

    return ret_values


def load_territories():
    try:
        ret_values = {}
        f = open(args.path + "/territories.csv", "r", encoding='utf8')
        # Skip the header line
        next(f)
        for line in f:
            tmp_dict = {}
            line = line.strip()
            tokens = line.split(",")
            tmp_dict["TerritoryID"] = tokens[0]
            tmp_dict["TerritoryDescription"] = tokens[1]
            tmp_dict["RegionID"] = tokens[2]

            ret_values[tokens[0]] = tmp_dict
    except:
        print("Unable to process territories")
    finally:
        f.close()

    return ret_values


def load_regions():
    try:
        ret_values = {}
        f = open(args.path + "/regions.csv", "r", encoding='utf8')
        # Skip the header line
        next(f)
        for line in f:
            tmp_dict = {}
            line = line.strip()
            tokens = line.split(",")
            tmp_dict["RegionID"] = tokens[0]
            tmp_dict["RegionDescription"] = tokens[1]

            ret_values[tokens[0]] = tmp_dict
    except:
        print("Unable to process regions")
    finally:
        f.close()

    return ret_values


def load_shippers():
    try:
        ret_values = {}
        f = open(args.path + "/shippers.csv", "r", encoding='utf8')
        # Skip the header line
        next(f)
        for line in f:
            tmp_dict = {}
            line = line.strip()
            tokens = line.split(",")
            tmp_dict["ShipperID"] = tokens[0]
            tmp_dict["CompanyName"] = tokens[1]
            tmp_dict["Phone"] = tokens[2]

            ret_values[tokens[0]] = tmp_dict
    except:
        print("Unable to process shipper")
    finally:
        f.close()

    return ret_values


def load_orders():
    try:
        ret_values = {}
        f = open(args.path + "/orders.csv", "r", encoding='utf8')
        # Skip the header line
        next(f)
        for line in f:
            tmp_dict = {}
            line = line.strip()
            tokens = line.split(",")
            tmp_dict["OrderID"] = tokens[0]
            tmp_dict["CustomerID"] = tokens[1]
            tmp_dict["EmployeeID"] = tokens[2]
            tmp_dict["OrderDate"] = tokens[3].split(" ")[0]
            tmp_dict["RequiredDate"] = tokens[4].split(" ")[0]
            if tokens[5] != "NULL":
                tmp_dict["ShippedDate"] = tokens[5].split(" ")[0]
            tmp_dict["ShipVia"] = tokens[6]
            tmp_dict["Freight"] = float(tokens[7])
            tmp_dict["ShipName"] = tokens[8]
            tmp_dict["ShipAddress"] = tokens[9]
            tmp_dict["ShipCity"] = tokens[10]
            if tokens[11] != "NULL":
                tmp_dict["ShipRegion"] = tokens[11]
            tmp_dict["ShipPostalCode"] = tokens[12]
            tmp_dict["ShipCountry"] = tokens[13]

            ret_values[tokens[0]] = tmp_dict
    except:
        print("Unable to process orders")
    finally:
        f.close()

    return ret_values


def load_customers():
    try:
        ret_values = {}
        f = open(args.path + "/customers.csv", "r", encoding='utf8')
        # Skip the header line
        next(f)
        for line in f:
            tmp_dict = {}
            line = line.strip()
            tokens = line.split(",")
            tmp_dict["CustomerID"] = tokens[0]
            tmp_dict["CompanyName"] = tokens[1]
            tmp_dict["ContactName"] = tokens[2]
            tmp_dict["ContactTitle"] = tokens[3]
            tmp_dict["Address"] = tokens[4]
            tmp_dict["City"] = tokens[5]
            if tokens[6] != "NULL":
                tmp_dict["Region"] = tokens[6]
            tmp_dict["PostalCode"] = tokens[7]
            tmp_dict["Country"] = tokens[8]
            tmp_dict["Phone"] = tokens[9]
            if tokens[10] != "NULL":
                tmp_dict["Fax"] = tokens[10]

            ret_values[tokens[0]] = tmp_dict
    except:
        print("Unable to process customers")
    finally:
        f.close()

    return ret_values


def load_order_details():
    try:
        ret_values = {}
        f = open(args.path + "/order-details.csv", "r", encoding='utf8')
        # Skip the header line
        next(f)
        for line in f:
            line = line.strip()
            tokens = line.split(",")
            order_id = tokens[0]
            tmp_value = {"ProductID": tokens[1], "UnitPrice": float(tokens[2]), "Quantity": int(tokens[3]),
                         "Discount": float(tokens[4])}

            line_items = ret_values.get(order_id)
            if line_items is None:
                line_items = [tmp_value]
            else:
                line_items.append(tmp_value)

            ret_values[order_id] = line_items
    except:
        print("Unable to process order details territories")
    finally:
        f.close()

    return ret_values


# Define methods to write denormalized data
def fmt_products():
    ret_values = {}
    for tmp_key in products:
        tmp_dict = products[tmp_key]
        # Get the supplier and remove the SupplierID from formatted object
        tmp_supplier = suppliers[tmp_dict.pop("SupplierID", None)]
        if tmp_supplier is not None:
            tmp_dict["Supplier"] = tmp_supplier

        # Get the category and remove the CategoryID from formatted object
        tmp_category = categories[tmp_dict.pop("CategoryID", None)]
        if tmp_category is not None:
            tmp_dict["Category"] = tmp_category

        ret_values[tmp_key] = tmp_dict

    try:
        f = open(args.outdir+"/products.json", "w", encoding="utf8")
        for print_key in ret_values:
            f.write("{}{}".format(json.dumps(ret_values[print_key]), "\n"))
    except:
        print("Unable to write product file")
    finally:
        f.close()


def fmt_employees():
    ret_values = {}
    for tmp_key in employees:
        tmp_dict = employees[tmp_key]
        # Get the supplier and remove the SupplierID from formatted object
        tmp_emp_terr = emp_territories[tmp_dict.get("EmployeeID")]
        if tmp_emp_terr is not None:
            fmt_terr = []
            for terr in tmp_emp_terr:
                tmp_terr = territories[terr]
                tmp_terr["Region"] = regions[tmp_terr.pop("RegionID", None)]
                fmt_terr.append(tmp_terr)

            tmp_dict["Territories"] = fmt_terr

        ret_values[tmp_key] = tmp_dict

    try:
        f = open(args.outdir+"/employees.json", "w", encoding="utf8")
        for print_key in ret_values:
            f.write("{}{}".format(json.dumps(ret_values[print_key]), "\n"))
    except:
        print("Unable to write employee file")
    finally:
        f.close()


def fmt_cust_orders():
    ret_orders = {}
    ret_customers = {}

    for tmp_key in orders:
        # Format Order
        tmp_order_dict = orders[tmp_key]
        tmp_order_dict["Employee"] = employees[tmp_order_dict.pop("EmployeeID", None)]
        tmp_order_dict["Shipper"] = shippers[tmp_order_dict.pop("ShipVia", None)]

        # Format Order Line Items to order and Customer
        tmp_cust_id = tmp_order_dict.pop("CustomerID", None)
        tmp_order_dict["CustomerID"] = tmp_cust_id

        # Process all line items for order
        tmp_short_order_items = []
        tmp_full_order_items = []
        tmp_line_items = order_details[tmp_key]
        for tmp_line_item in tmp_line_items:
            tmp_short_item = tmp_line_item.copy() # Copy short version as seperate item
            tmp_product = products[tmp_line_item.pop("ProductID", None)]
            tmp_line_item["Products"] = tmp_product
            tmp_short_item["ProductName"] = tmp_product["ProductName"]
            tmp_short_item["CategoryName"] = tmp_product["Category"]["CategoryName"]
            tmp_short_order_items.append(tmp_short_item)
            tmp_full_order_items.append(tmp_line_item)

        cust_order_item = {"OrderID" : tmp_key, "OrderDate" : tmp_order_dict["OrderDate"],
                           "Products" : tmp_short_order_items}

        try:
            shipped_date = tmp_order_dict["ShippedDate"]
            if shipped_date is not None:
                cust_order_item["ShippedDate"] = shipped_date
        except KeyError:
            pass  # Suppress Missing key


        # Set up formatted Customer information
        try:
            fmt_customer = ret_customers[tmp_cust_id]
        except KeyError:
            fmt_customer = customers[tmp_cust_id]
            ret_customers[tmp_cust_id] = fmt_customer

        fmt_customer_orders = fmt_customer.pop("Orders", None)
        if fmt_customer_orders is not None:
            fmt_customer_orders.append(cust_order_item)
        else:
            fmt_customer_orders = [cust_order_item]

        fmt_customer["Orders"] = fmt_customer_orders


        # Add Updated Dictionary to formatted orders
        tmp_order_dict["LineItems"] = tmp_full_order_items
        ret_orders[tmp_key] = tmp_order_dict

    # Print out the fmt files
    try:
        fo = open(args.outdir + "/orders.json", "w", encoding="utf8")
        fc = open(args.outdir + "/customers.json", "w", encoding="utf8")
        for print_key in ret_orders:
            fo.write("{}{}".format(json.dumps(ret_orders[print_key]), "\n"))
        for print_key in ret_customers:
            fc.write("{}{}".format(json.dumps(ret_customers[print_key]), "\n"))
    except:
        print("Error formatting customer and orders")
    finally:
        fo.close()
        fc.close()


# Add argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", default="../northwind-mongo", required=False,
                    help="The path to the data files. Default [../northwind-mongo]")
parser.add_argument("-o", "--outdir", default=".", required=False,
                    help="The output directory to generate files. Default [.]")
args = parser.parse_args()

# Load the files
categories = load_categories()
products = load_products()
suppliers = load_suppliers()
employees = load_employees()
emp_territories = load_employee_territories()
territories = load_territories()
regions = load_regions()
shippers = load_shippers()
order_details = load_order_details()
orders = load_orders()
customers = load_customers()


# Format the denormalized data
fmt_products()
fmt_employees()
fmt_cust_orders()

#for key in orders:
#    print("{} - {}".format(key, json.dumps(orders[key])))

