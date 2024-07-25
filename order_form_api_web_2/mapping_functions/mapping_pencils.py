import json
import os
import requests
from Product_Catalog.VarianCodes.ProductHierarchy import personalized_vs_standard , state_of_pencils , graphite_seeds , \
    color_seeds , multi_color_seeds , packaging_types , packaging , languages , country_codes
from Product_Catalog.VarianCodes.variants import item_dict , packaging_items
import re


def get_environment_config() :
    """
    Retrieve environment configuration variables.

    Returns:
    - dict: Dictionary containing the environment configuration.
    """
    return {
        "base_url" : os.getenv("BASEURL") ,
        "tenant_id" : os.getenv("TENANTID") ,
        "environment" : os.getenv('TESTENVIRONMENT') ,
        "company" : os.getenv('COMPANYEU')
    }


def add_one_item(data , item_type , quantity , item_no , item_id , location , config , document_no) :
    """
    Add an item line to the sales order data.

    Parameters:
    - data (dict): Sales order data.
    - item_type (str): Type of the item.
    - quantity (int): Quantity of the item.
    - item_no (str): Item number.
    - item_id (str): Unique ID for the item.
    - location (str): Location code.
    - config (dict): Environment configuration.
    - document_no (str): Document number.
    """
    data['lines']['requests'].append({
        "method" : "POST" ,
        "id" : item_id ,
        "url" : f"{config['company']}/Sales_Order_ExcelSalesLines" ,
        "headers" : {
            "Content-Type" : "application/json"
        } ,
        "body" : {
            "Document_No" : document_no ,
            "Type" : item_type ,
            "No" : item_no ,
            "Location_Code" : location ,
            "Quantity" : quantity
        }
    })


def add_fee(data , item_type , quantity , item_no , item_id , location , config , document_no , price) :
    """
    Add a fee line to the sales order data.

    Parameters:
    - data (dict): Sales order data.
    - item_type (str): Type of the item.
    - quantity (int): Quantity of the item.
    - item_no (str): Item number.
    - item_id (str): Unique ID for the item.
    - location (str): Location code.
    - config (dict): Environment configuration.
    - document_no (str): Document number.
    - price (float): Unit price of the fee.
    """
    data['lines']['requests'].append({
        "method" : "POST" ,
        "id" : item_id ,
        "url" : f"{config['company']}/Sales_Order_ExcelSalesLines" ,
        "headers" : {
            "Content-Type" : "application/json"
        } ,
        "body" : {
            "Document_No" : document_no ,
            "Type" : item_type ,
            "No" : item_no ,
            "Location_Code" : location ,
            "Quantity" : quantity ,
            "Unit_Price" : price
        }
    })


def handle_language(entries , data , document_no) :
    """
    Handle the language specification for the sales order.

    Parameters:
    - entries (dict): Order entries.
    - data (dict): Sales order data.
    - document_no (str): Document number.
    """
    config=get_environment_config()

    if entries['30'] not in ["Other" , ""] :
        data['lines']['requests'].append({
            "method" : "POST" ,
            "id" : "898989" ,
            "url" : f"{config['company']}/Sales_Order_ExcelSalesLines" ,
            "headers" : {
                "Content-Type" : "application/json"
            } ,
            "body" : {
                "Document_No" : document_no ,
                "Type" : "Item" ,
                "No" : languages[entries['30']] ,
                "Location_Code" : "PP" ,
                "Quantity" : 1
            }
        })
    else :
        data['lines']['requests'].append({
            "method" : "POST" ,
            "id" : "89898asd9" ,
            "url" : f"{config['company']}/Sales_Order_ExcelSalesLines" ,
            "headers" : {
                "Content-Type" : "application/json"
            } ,
            "body" : {
                "Document_No" : document_no ,
                "Type" : "Item" ,
                "No" : '604' ,
                "Location_Code" : "PP" ,
                "Quantity" : 1 ,
                "Description" : entries['248']
            }
        })


def map_items(entry , data , access_token , quantity) :
    """
    Map the items from the order entry to the sales order data.

    Parameters:
    - entry (dict): Order entry.
    - data (dict): Sales order data.
    - access_token (str): Access token for authentication.
    - quantity (int): Total quantity of items.

    Returns:
    - dict: Updated sales order data.
    """
    config=get_environment_config()
    product_dict={ }
    data , product_dict , document_no=add_pencils(entry , product_dict , data , access_token , quantity)

    if entry['119'] not in ["Pencils only" , "" , " "] :
        add_packaging(entry , product_dict , data , document_no , quantity)
    if entry['233'] != "No thanks not this time" :
        add_sharpeners(entry , data , config , document_no)
    handle_language(entry , data , document_no)
    if entry['7'] in ["Customized laser engraved" , "Customized color print"] :
        add_fee(data , "Item" , 1 , "625" , "k1k1" , "PP" , config , document_no , 10.0)
    if entry['111'] == "Customized packaging (Your own design)" :
        add_fee(data , "Item" , 1 , "626" , "k1k2" , "PP" , config , document_no , 15.0)
    if entry['7'] in ["Customized color print" , "Standard color print"] :
        add_one_item(data , "Item" , quantity , "100" , "k1k3" , "PP" , config , document_no)
    add_one_item(data , "Item" , 1 , "997" , "k1k5" , "PP" , config , document_no)

    return data


def add_pencils(entry , product_dict , data , access_token , quantity) :
    """
    Add pencil items to the sales order data.

    Parameters:
    - entry (dict): Order entry.
    - product_dict (dict): Product dictionary.
    - data (dict): Sales order data.
    - access_token (str): Access token for authentication.
    - quantity (int): Total quantity of items.

    Returns:
    - tuple: Updated sales order data, product dictionary, and document number.
    """
    config=get_environment_config()
    lang=entry['30']

    size_and_state={
        "size" : "normal" if entry['121'] not in ["Mini Single Card" , "Hanger Tag"] else "mini" ,
        "state" : "up" if entry['121'] in ["Mini Single Card" , "Hanger Tag"] else (
            "sp" if entry['121'] in ["5-Pack" , "3-Pack"] else (
                "sp" if entry['28'] == "" else state_of_pencils[entry['28']]
            )
        )
    }

    personalized=entry['7'] in ["Customized laser engraved" , "Customized color print"]

    if entry['23'] != "" :
        product_dict[
            "Pencil_ID_gh"]=f"{personalized_vs_standard[personalized]} {size_and_state['state']} {'Other' if personalized or size_and_state['size'] == 'mini' else lang}"
    if entry['24'] != "" :
        product_dict[
            "Pencil_ID_cl"]=f"{personalized_vs_standard[personalized]} sp {'Other' if personalized or size_and_state['size'] == 'mini' else lang}"
    if entry['152'] != "" :
        product_dict["Pencil_ID_ml"]=f"{personalized_vs_standard[personalized]} sp Other"

    data , document_no=handle_pencils(product_dict , access_token , entry , data , size_and_state['size'] , quantity)

    return data , product_dict , document_no


def add_packaging(entry , product_dict , data , document_no , quantity) :
    """
    Add packaging items to the sales order data.

    Parameters:
    - entry (dict): Order entry.
    - product_dict (dict): Product dictionary.
    - data (dict): Sales order data.
    - document_no (str): Document number.
    - quantity (int): Total quantity of items.

    Returns:
    - dict: Updated sales order data.
    """
    config=get_environment_config()
    packaging_type=entry['121']
    customized_packaging=entry['111'] == "Customized packaging (Your own design)"
    lang="Other" if entry['153'] == "" else entry['153']
    product_dict[
        'packaging_id']=f"{packaging_types[packaging_type]} {(packaging[customized_packaging] if packaging_type != 'Hanger Tag' else 's')} {lang}"
    data=generate_packaging_batch(product_dict , data , "packaging_id" , document_no , quantity)

    return data


def handle_pencils(product_dict , access_token , entry , data , size , quantity) :
    """
    Handle the addition of pencil items to the sales order data.

    Parameters:
    - product_dict (dict): Product dictionary.
    - access_token (str): Access token for authentication.
    - entry (dict): Order entry.
    - data (dict): Sales order data.
    - size (str): Size of the pencils.
    - quantity (int): Total quantity of items.

    Returns:
    - tuple: Updated sales order data and document number.
    """
    config=get_environment_config()
    document_no=create_new_order(quantity , data['customer_number'] , access_token , entry)

    if "Pencil_ID_gh" in product_dict :
        data=generate_pencil_batch(product_dict , graphite_seeds , data , entry , size , "Pencil_ID_gh" , document_no)
    if "Pencil_ID_cl" in product_dict :
        data=generate_pencil_batch(product_dict , color_seeds , data , entry , size , "Pencil_ID_cl" , document_no)
    if "Pencil_ID_ml" in product_dict :
        data=generate_pencil_batch(product_dict , multi_color_seeds , data , entry , size , "Pencil_ID_ml" ,
                                   document_no)

    return data , document_no


def create_new_order(quantity , customer , access_token , entry) :
    """
    Create a new sales order.

    Parameters:
    - quantity (int): Total quantity of items.
    - customer (str): Customer number.
    - access_token (str): Access token for authentication.
    - entry (dict): Order entry.

    Returns:
    - str: Document number of the created sales order.
    """
    config=get_environment_config()

    order_data={
        "PTE_Total_Quantity" : int(quantity) ,
        "PTE_Status_Code" : "19-APPROVAL" ,
        "Sell_to_Customer_No" : customer ,
        "Sell_to_Contact" : entry['89.3'] ,
        "External_Document_No" : (entry['125'])[:35] if entry['125'] != '' else entry['id'] ,
        "Sell_to_Address" : (entry["87.1"])[:99] ,
        "Sell_to_Address_2" : (entry["87.2"])[:49] ,
        "Sell_to_City" : (entry["87.3"])[:29] ,
        "Sell_to_Post_Code" : (entry["87.5"])[:19] ,
        "Sell_to_Country_Region_Code" : (country_codes[entry["87.6"]])[:9] if entry["87.6"] in country_codes else "" ,
        "Sell_to_Phone_No" : re.sub('\D' , '' , entry["307"]) ,
        "Sell_to_E_Mail" : entry["88"] ,
        "ShippingOptions" : "Custom Address" ,
        "PTE_Ship_to_Email" : entry["88"]
    }

    if entry['139.1'] == "Delivery address is different from invoice" :
        ship_keys={
            'add_1' : '95.1' , 'add_2' : '95.2' , 'city' : '95.3' , 'post_code' : '95.5' , 'region' : '95.6' ,
            'contact_first' : '96.3' , 'contact_last' : '96.6' , 'phone' : '97' , 'company' : '94'
        }
    else :
        ship_keys={
            'add_1' : '87.1' , 'add_2' : '87.2' , 'city' : '87.3' , 'post_code' : '87.5' , 'region' : '87.6' ,
            'contact_first' : '89.3' , 'contact_last' : '89.6' , 'phone' : '307' , 'company' : '86'
        }

    order_data.update({
        "Ship_to_Address" : (entry[ship_keys['add_1']])[:99] ,
        "Ship_to_Address_2" : (entry[ship_keys['add_2']])[:49] ,
        "Ship_to_City" : (entry[ship_keys['city']])[:20] ,
        "Ship_to_Post_Code" : (entry[ship_keys['post_code']])[:19] ,
        "Ship_to_Country_Region_Code" : (country_codes[entry[ship_keys['region']]])[:9] if entry[ship_keys[
            'region']] in country_codes else "" ,
        "Ship_to_Contact" : f"{entry[ship_keys['contact_first']]} {entry[ship_keys['contact_last']]}" ,
        "PTE_Ship_to_Phone_No" : re.sub(r'\D' , '' , entry[ship_keys['phone']]) ,
        "Ship_to_Name" : entry[ship_keys['company']]
    })

    payload=json.dumps(order_data)
    headers={
        'Content-Type' : 'application/json' ,
        'Authorization' : f"Bearer {access_token}"
    }
    url=f"{config['base_url']}/{config['tenant_id']}/{config['environment']}/ODataV4/{config['company']}/Sales_Order_Excel"
    response=requests.post(url , headers=headers , data=payload)

    return response.json()['No']


def generate_pencil_batch(product_dict , seeds , data , entry , size , color_id , document_no) :
    """
    Generate a batch of pencil items for the sales order.

    Parameters:
    - product_dict (dict): Product dictionary.
    - seeds (dict): Seeds for generating pencil items.
    - data (dict): Sales order data.
    - entry (dict): Order entry.
    - size (str): Size of the pencils.
    - color_id (str): Color ID of the pencils.
    - document_no (str): Document number.

    Returns:
    - dict: Updated sales order data.
    """
    config=get_environment_config()

    for key in seeds.keys() :
        if entry[key] != "" :
            data['lines']['requests'].append({
                "method" : "POST" ,
                "id" : str(key) ,
                "url" : f"{config['company']}/Sales_Order_ExcelSalesLines" ,
                "headers" : {
                    "Content-Type" : "application/json"
                } ,
                "body" : {
                    "Document_No" : document_no ,
                    "Type" : "Item" ,
                    "No" : item_dict[f"{product_dict[color_id]} {seeds[key]} {size}"] ,
                    "Location_Code" : "PP" ,
                    "Quantity" : int(entry[key])
                }
            })
    return data


def generate_packaging_batch(product_dict , data , packaging_id , document_no , quantity) :
    """
    Generate a batch of packaging items for the sales order.

    Parameters:
    - product_dict (dict): Product dictionary.
    - data (dict): Sales order data.
    - packaging_id (str): ID of the packaging.
    - document_no (str): Document number.
    - quantity (int): Total quantity of items.

    Returns:
    - dict: Updated sales order data.
    """
    config=get_environment_config()
    packaging_item=packaging_items[product_dict[packaging_id]]

    if packaging_item in ["2100" , "5240"] :
        quantity=quantity / 3
    elif packaging_item in ["2300" , "5250"] :
        quantity=quantity / 5

    data['lines']['requests'].append({
        "method" : "POST" ,
        "id" : str(1) ,
        "url" : f"{config['company']}/Sales_Order_ExcelSalesLines" ,
        "headers" : {
            "Content-Type" : "application/json"
        } ,
        "body" : {
            "Document_No" : document_no ,
            "Type" : "Item" ,
            "No" : packaging_item ,
            "Location_Code" : "PP" ,
            "Quantity" : quantity
        }
    })
    return data


def add_sharpeners(entries , data , config , document_no) :
    """
    Add sharpeners to the sales order data.

    Parameters:
    - entries (dict): Order entries.
    - data (dict): Sales order data.
    - config (dict): Environment configuration.
    - document_no (str): Document number.
    """
    if entries['233'] == "Standard ( plain )" :
        add_one_item(data , "Item" , int(entries['238']) , "720" , "sharp1" , "PP" , config , document_no)
    elif entries['233'] == "Customized with color print" :
        add_one_item(data , "Item" , int(entries['238']) , "722" , "sharp2" , "PP" , config , document_no)
