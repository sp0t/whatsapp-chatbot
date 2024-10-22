import boto3
from botocore.signers import RequestSigner
import requests

AMAZON_ACCESS_KEY = 'YOUR_ACCESS_KEY'
AMAZON_SECRET_KEY = 'YOUR_SECRET_KEY'
AMAZON_ASSOCIATE_TAG = 'YOUR_ASSOCIATE_TAG'
AMAZON_REGION = 'us-east-1'

def create_signed_url(operation, parameters):
    # Create a signer using boto3
    service_name = 'execute-api'
    endpoint_url = f"https://webservices.amazon.com/onca/xml"
    
    request_signer = RequestSigner(
        service_name,
        AMAZON_REGION,
        'amazon',
        AMAZON_ACCESS_KEY,
        AMAZON_SECRET_KEY
    )
    
    params = {
        'Service': 'AWSECommerceService',
        'Operation': operation,
        'AWSAccessKeyId': AMAZON_ACCESS_KEY,
        'AssociateTag': AMAZON_ASSOCIATE_TAG,
        **parameters
    }
    
    # Construct a signed URL
    signed_url = request_signer.generate_presigned_url(
        'GET',
        endpoint_url,
        params
    )
    
    return signed_url

# Example usage: Searching for a product
product_url = create_signed_url('ItemSearch', {
    'Keywords': 'Wilson "The Duke" Official NFL Game Football',
    'SearchIndex': 'All',
    'ResponseGroup': 'ItemAttributes,Offers'
})


ALIEXPRESS_APP_KEY = 'YOUR_APP_KEY'
ALIEXPRESS_TRACKING_ID = 'YOUR_TRACKING_ID'

def get_aliexpress_affiliate_link(product_name):
    api_url = f"https://gw.api.alibaba.com/openapi/param2/2/portals.open/api.listPromotionProduct/{ALIEXPRESS_APP_KEY}"
    params = {
        'fields': 'productId,productTitle,productUrl',
        'keywords': product_name,
        'highQualityItems': 'true',
        'trackingId': ALIEXPRESS_TRACKING_ID
    }
    
    response = requests.get(api_url, params=params)
    data = response.json()
    
    if 'result' in data and 'products' in data['result']:
        for product in data['result']['products']:
            print(product['productTitle'], product['productUrl'])

# Example usage: Searching for a product
get_aliexpress_affiliate_link('Wilson "The Duke" Official NFL Game Football')

