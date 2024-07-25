import json
import os
import requests
from mapping_functions.validation import get_access_token
import re


def get_customers_from_bc(access_token) :
    """
    Retrieve customers from Business Central who are not blocked.

    Parameters:
    - access_token (str): Access token for authentication.

    Returns:
    - List[dict]: A list of dictionaries containing customer information.
    """
    base_url=os.getenv("BASEURL")
    tenant_id=os.getenv("TENANTID")
    environment=os.getenv('PRODENVIRNMENT')
    company=os.getenv('COMPANYEU')
    endpoint=os.getenv('CUSTOMERENDPOINT')
    url=f"{base_url}/{tenant_id}/{environment}/ODataV4/{company}/{endpoint}?$select=Blocked,No,VAT_Registration_No,Phone_No,Name,E_Mail"

    headers={
        "Content-Type" : "application/json" ,
        "Authorization" : f"Bearer {access_token}"
    }

    response=requests.get(url , headers=headers)
    customers=response.json().get('value' , [])

    # Filter out blocked customers
    active_customers=[customer for customer in customers if customer['Blocked'] != "All"]

    return active_customers


def check_if_customer_exists(vat_no , email , phone , name , customers) :
    """
    Check if a customer exists based on VAT number, email, phone, or name.

    Parameters:
    - vat_no (str): VAT registration number.
    - email (str): Email address.
    - phone (str): Phone number.
    - name (str): Customer name.
    - customers (List[dict]): List of customers to check against.

    Returns:
    - List[dict]: A list of dictionaries with customer IDs and names of matching customers.
    """
    # Pre-compile the regex pattern to remove non-digits
    pattern=re.compile(r'\D')

    matching_customers=[]
    encountered_customer_ids=set()

    for customer in customers :
        vat_match=pattern.sub('' , customer['VAT_Registration_No']) == pattern.sub('' , vat_no) and pattern.sub('' ,
                                                                                                                customer[
                                                                                                                    'VAT_Registration_No']) != ""
        email_domain_match='gmail.com' not in customer['E_Mail'].lower() and customer['E_Mail'].split('@' , 1)[
            -1].upper() == email.split('@' , 1)[-1].upper()
        phone_match=customer['Phone_No'] == phone and phone != ""
        name_match=customer['Name'].upper() == name.upper() and name != ""

        if vat_match or email_domain_match or phone_match or name_match :
            if customer['No'] not in encountered_customer_ids :
                matching_customers.append(
                    { 'title' : f"{customer['No']} - {customer['Name']}" , 'value' : customer['No'] })
                encountered_customer_ids.add(customer['No'])

    return matching_customers
