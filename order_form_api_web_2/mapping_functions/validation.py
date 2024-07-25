import os
import requests

def get_environment_config():
    """
    Retrieve environment configuration variables.

    Returns:
    - dict: Dictionary containing the environment configuration.
    """
    return {
        "client_secret": os.getenv("CLIENT_SECRET"),
        "grant_type": os.getenv("GRANT_TYPE"),
        "scope": os.getenv("SCOPE"),
        "token_url": os.getenv('TOKEN_URL'),
        "cs": os.getenv('CS'),
        "order_endpoint": os.getenv('ORDERENDPOINT'),
        "delete_endpoint": os.getenv('DELETEENDPOINT')
    }

def get_access_token(bc_id):
    """
    Retrieve access token using the provided business center ID.

    Parameters:
    - bc_id (str): Business center ID.

    Returns:
    - str: Access token if successful, otherwise None.
    """
    config = get_environment_config()
    data = {
        "client_id": bc_id,
        "scope": config["scope"],
        "client_secret": config["client_secret"],
        "grant_type": config["grant_type"],
    }

    response = requests.post(config["token_url"], data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print('Error:', response.text)
        return None

def get_credentials():
    """
    Retrieve credentials and endpoints from environment configuration.

    Returns:
    - tuple: Client secret, order endpoint, and delete endpoint.
    """
    config = get_environment_config()
    return config['cs'], config['order_endpoint'], config['delete_endpoint']

def extract_order_batch(ck, cs, url_get_orders):
    """
    Extract order batch using the provided credentials and URL.

    Parameters:
    - ck (str): Client key.
    - cs (str): Client secret.
    - url_get_orders (str): URL to get orders.

    Returns:
    - dict: Extracted order data if successful, otherwise None.
    """
    session = requests.Session()
    session.auth = (ck, cs)
    response = session.get(url_get_orders)
    if response.status_code == 200:
        data = response.json()
        print(response.status_code, "Accessed", sep=" ")
        return data
    else:
        print("Request failed with status code:", response.status_code)
        return None
