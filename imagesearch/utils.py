import os

from google.cloud import storage, vision
from google.oauth2 import service_account
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from django.conf import settings

# constants
KEY_FILE = 'key.json'

# authentication
def create_storage_client():
    credentials = service_account.Credentials.from_service_account_file(os.path.join(BASE_DIR, KEY_FILE))
    client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT_ID, credentials=credentials)
    return client

def create_product_search_client():
    credentials = service_account.Credentials.from_service_account_file(os.path.join(BASE_DIR, KEY_FILE))
    client = vision.ProductSearchClient(credentials=credentials)
    return client

def create_image_annotator_client():
    credentials = service_account.Credentials.from_service_account_file(os.path.join(BASE_DIR, KEY_FILE))
    client = vision.ImageAnnotatorClient(credentials=credentials)
    return client

# storage part
def list_blobs():
    client = create_storage_client()
    blobs = client.list_blobs(settings.GOOGLE_STORAGE_BUCKET_NAME)
    return blobs

def upload_file(file_name, storage_path):
    client = create_storage_client()
    bucket = client.get_bucket(settings.GOOGLE_STORAGE_BUCKET_NAME)
    new_blob = bucket.blob(storage_path)
    new_blob.upload_from_filename(file_name)
    return new_blob

# product search part
def create_product_set(product_set_id, product_set_display_name):
    client = create_product_search_client()
    location_path = client.location_path(project=settings.GOOGLE_CLOUD_PROJECT_ID, location=settings.GOOGLE_CLOUD_LOCATION_ID)

    new_product_set = vision.types.ProductSet(display_name=product_set_display_name)
    response = client.create_product_set(
        parent=location_path,
        product_set=new_product_set,
        product_set_id=product_set_id
    )
    return response

def create_product_add_to_product_set(product_set_path, product_display_name, product_category):
    client = create_product_search_client()
    location_path = client.location_path(project=settings.GOOGLE_CLOUD_PROJECT_ID, location=settings.GOOGLE_CLOUD_LOCATION_ID)

    new_product = vision.types.Product(
        display_name=product_display_name,
        product_category=product_category,
    )

    new_product_response = client.create_product(
        parent=location_path,
        product=new_product,
    )

    client.add_product_to_product_set(name=product_set_path, product=new_product_response.name)

    return new_product_response

def create_reference_image(product_path, gcs_uri, boundingPolys=None):
    create_ref_image_api_url = 'https://vision.googleapis.com/v1/{}/referenceImages?key={}'.format(product_path, settings.GOOGLE_CLOUD_API_KEY)
    if boundingPolys is not None:
        r = requests.post(
            create_ref_image_api_url, json={
                "uri": gcs_uri,
                "boundingPolys": [
                    {
                        "normalizedVertices": boundingPolys,
                    }
                ]
            }
        )
        return r.json()
    else:
        r = requests.post(
            create_ref_image_api_url, json={
                "uri": gcs_uri,
            }
        )
        return r.json()

def create_multiple_reference_images(csv_gcs_uri):
    client = create_product_search_client()
    location_path = client.location_path(project=settings.GOOGLE_CLOUD_PROJECT_ID, location=settings.GOOGLE_CLOUD_LOCATION_ID)
    
    gcs_source = vision.types.ImportProductSetsGcsSource(csv_file_uri=csv_gcs_uri)
    input_config = vision.types.ImportProductSetsInputConfig(gcs_source=gcs_source)

    response = client.import_product_sets(parent=location_path, input_config=input_config)

    print('Processing operation name: {}'.format(response.operation.name))
    # synchronous check of operation status
    result = response.result()
    print('Processing done.')

    for i, status in enumerate(result.statuses):
        print('Status of processing line {} of the csv: {}'.format(i, status))
        # Check the status of reference image
        # `0` is the code for OK in google.rpc.Code.
        if status.code == 0:
            reference_image = result.reference_images[i]
            print(reference_image)
        else:
            print('Status code not OK: {}'.format(status.message))

def list_product_sets():
    client = create_product_search_client()
    location_path = client.location_path(project=settings.GOOGLE_CLOUD_PROJECT_ID, location=settings.GOOGLE_CLOUD_LOCATION_ID)

    product_sets = client.list_product_sets(parent=location_path)
    return product_sets

def get_product_set(product_set_path):
    client = create_product_search_client()
    product_set = client.get_product_set(name=product_set_path)
    return product_set

def list_products_in_product_set(product_set_path):
    client = create_product_search_client()
    products = client.list_products_in_product_set(name=product_set_path)
    return products

def get_product(product_path):
    client = create_product_search_client()
    product = client.get_product(name=product_path)
    return product

def list_reference_images(product_path):
    client = create_product_search_client()
    reference_images = client.list_reference_images(parent=product_path)
    return reference_images

def get_reference_image(reference_image_path):
    client = create_product_search_client()
    image = client.get_reference_image(name=reference_image_path)
    return image

def remove_product_from_product_set(product_path, product_set_path):
    client = create_product_search_client()
    client.remove_product_from_product_set(
        name=product_set_path,
        product=product_path
    )
    return True

def delete_product_set(product_set_path):
    client = create_product_search_client()
    client.delete_product_set(name=product_set_path)
    return True

def delete_product(product_path):
    client = create_product_search_client()
    client.delete_product(name=product_path)
    return True

def delete_all_products(force):
    client = create_product_search_client()
    parent = client.location_path(project=settings.GOOGLE_CLOUD_PROJECT_ID, location=settings.GOOGLE_CLOUD_LOCATION_ID)
    operation = client.purge_products(
        parent=parent,
        delete_orphan_products=True,
        force=force
    )
    operation.result(timeout=300)

def delete_reference_image(image_path):
    client = create_product_search_client()
    client.delete_reference_image(name=image_path)

    return True

def delete_all_products_in_product_set(product_set_id, force):
    client = create_product_search_client()
    parent = client.location_path(project=settings.GOOGLE_CLOUD_PROJECT_ID, location=settings.GOOGLE_CLOUD_LOCATION_ID)
    product_set_purge_config = vision.types.ProductSetPurgeConfig(product_set_id=product_set_id)
    operation = client.purge_products(
        parent=parent, 
        product_set_purge_config=product_set_purge_config, 
        force=force
    )
    operation.result(timeout=300)

def get_similar_product_uri(product_set_path, image_uri):
    product_search_client = create_product_search_client()
    image_annotator_client = create_image_annotator_client()

    image_source = vision.types.ImageSource(image_uri=image_uri)
    image = vision.types.Image(source=image_source)
    
    product_search_params = vision.types.ProductSearchParams(
        product_set=product_set_path,
        product_categories=['apparel-v2', 'homegoods-v2', 'toys-v2', 'packagedgoods-v1', 'general-v1'],
        # filter=filter
    )
    image_context = vision.types.ImageContext(product_search_params=product_search_params)

    response = image_annotator_client.product_search(image, image_context=image_context)

    index_time = response.product_search_results.index_time
    print('Product set index time:')
    print('  seconds: {}'.format(index_time.seconds))
    print('  nanos: {}\n'.format(index_time.nanos))

    results = response.product_search_results.results

    print('Search results:')
    for result in results:
        product = result.product

        print('Score(Confidence): {}'.format(result.score))
        print('Image name: {}'.format(result.image))
        print('Image URI:', product_search_client.get_reference_image(name=result.image).uri)

        print('Product name: {}'.format(product.name))
        print('Product display name: {}'.format(product.display_name))
        print('Product description: {}\n'.format(product.description))
        print('Product labels: {}\n'.format(product.product_labels))