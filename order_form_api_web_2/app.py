import inspect
import os
import warnings
import requests
from Product_Catalog.templates import templates , country_dict
from mapping_functions.customer_mapping import check_if_customer_exists , get_customers_from_bc
from mapping_functions.mapping_pencils import map_items
from mapping_functions.validation import get_access_token , get_credentials , extract_order_batch
from flask import Flask , jsonify , request , Response


# Initialize Flask app
app=Flask(__name__)


# Route to return a test JSON response
@app.route('/' , methods=['GET'])
def get_json_data() :
    return jsonify("tester_json")


# Route to check server status
@app.route('/serverIsActive' , methods=['GET'])
def check_server() :
    return jsonify("Connection is open")


# Route to retrieve access token
@app.route('/retrieve_ac' , methods=['POST'])
def get_access_token_route() :
    business_center_id=request.json.get('bc_id')
    access_token=get_access_token(business_center_id)
    return jsonify({ 'ac' : access_token })


# Route to get customer data
@app.route('/get_customers' , methods=['POST'])
def get_customers_route() :
    entry=request.json.get('entry')
    access_token=request.json.get('ac')
    customers=request.json.get('customers')

    # Filter out blocked customers
    customers_not_blocked=[customer for customer in customers if not customer['Blocked'] == "All"]

    # Check if customers exist
    customers_found=check_if_customer_exists(entry['138'] , entry['88'] , entry['307'] , entry['86'] ,
                                             customers_not_blocked)

    return jsonify({
                       'customer_mapping' : { 'no' : customers_found } , "ac" : access_token ,
                       't_id' : os.getenv('TENANTID') , 'templates' : templates , 'countries' : country_dict
                   })


# Route to process new orders
@app.route('/newOrders' , methods=['POST'])
def new_orders_route() :
    try :
        entry=request.json.get('entry')
        access_token=request.json.get('ac')
        customer_number=request.json.get('customer_no')

        # Get quantities of different types of pencils
        graphite_quantity=int(entry.get('23' , 0)) if entry.get('23' , '') != '' else 0
        color_quantity=int(entry.get('24' , 0)) if entry.get('24' , '') != '' else 0
        multi_quantity=int(entry.get('152' , 0)) if entry.get('152' , '') != '' else 0
        total_quantity=int(entry.get('25' , 0)) if entry.get('25' , '') != '' else 0

        # Determine total quantity
        quantity=total_quantity if total_quantity != 0 else color_quantity + graphite_quantity + multi_quantity

        # Create data structure for order
        order_data={
            "order" : { "Total Quantity" : quantity } ,
            "lines" : { "requests" : [] } ,
            "customer_number" : customer_number
        }

        # Map items and process order
        mapped_items=map_items(entry , order_data , access_token , quantity)

        return jsonify(mapped_items) , 200  # Return success response with status code 200

    except Exception as e :
        error_message={ "error" : str(e) }
        print(error_message)
        return jsonify(error_message) , 500  # Return error message and HTTP status code 500 (Internal Server Error)



# Run the Flask app
if __name__ == '__main__' :
    app.run(debug=True , host="0.0.0.0" , port=2237)
