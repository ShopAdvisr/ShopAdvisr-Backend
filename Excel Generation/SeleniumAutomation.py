import os
from google.api_core.exceptions import DataLoss
from google.cloud import storage
from google.cloud import vision
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import urllib
import csv

categories = {
    "Food" : "https://www.loblaws.ca/food/c/27985?navid=flyout-L2-Food",
    "Baby" : "https://www.loblaws.ca/baby/c/27987?navid=flyout-L2-Baby",
    "Home & Kitchen" : "https://www.loblaws.ca/home-and-living/c/27986?navid=flyout-L2-Home%20&%20Kitchen",
    "Office & School Supplies" : "https://www.loblaws.ca/office-school-supplies/c/27991?navid=flyout-L2-Office-and-School-Supplies",
    "Electronics & Batteries" : "https://www.loblaws.ca/computers-electronics/c/27992?navid=flyout-L2-Electronics%20&%20Batteries",
    "Health & Beauty" : "https://www.loblaws.ca/health-beauty/c/27994?navid=flyout-L2-Health-and-Beauty",
    "Pet Supplies" : "https://www.loblaws.ca/pet-supplies/c/27988?navid=flyout-L2-Pet-Supplies",
    "Toys, Games & Hobbies" : "https://www.loblaws.ca/toys-games-hobbies/c/27990?navid=flyout-L2-Toys-Games-and-Hobbies"
}

def download_image(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with open("temp.png", "wb") as f:
        with urllib.request.urlopen(req) as r:
            f.write(r.read())
            print("done")
            f.close()

def upload_to_bucket(blob_name, img_url, bucket_name):
    """ Upload data to a bucket"""
    download_image(img_url)

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename("temp.png")
    link = 'gs://' + blob.path_helper(bucket_name, blob_name)

    return link

def getLoblawData(link):
    with webdriver.Chrome("C:\\Users\\Noor\\Downloads\\chromedriver_win32 (1)\\chromedriver.exe") as driver:
        driver.get(link)
        wait = WebDriverWait(driver, 10)
        data = []
        
        # expand page
        element = wait.until(expected_conditions. element_to_be_clickable((By.CLASS_NAME, "primary-button")))
        #element.click()

        # test item data
        divs = driver.find_elements_by_class_name("product-tile--marketplace")
        id = 0

        for product in divs:
            product_image = product.find_elements_by_class_name("responsive-image")[0].get_attribute("src")
            product_name = product.find_elements_by_class_name("product-name__item--name")[0].text.replace(" ", "_")
            product_price = product.find_elements_by_class_name("price__value")[0].text
            
            """
            extraTags = {"product-name__item--brand" : -1}
            for tagClassName in extraTags:
                product_tag = divs[3].find_elements_by_class_name(tagClassName)
                if len(product_tag) > 0:
                    extraTags[tagClassName] =  product_tag[0].text
            """

            internal_url = upload_to_bucket(product_image, product_name, "shopadvisr-bucket")
            data.append([internal_url, product_name, "product_set0", "product_id" + str(id), "general-v1", "", "price="+str(product_price), ""])
            id += 1

        return data

def createCSV(data):
    path = "ProductData.csv"
    with open(path, 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for r in range(len(data)):
            filewriter.writerow(data[r])
        
        csvfile.close()
        print("Product data saved to", path)

    storage_client = storage.Client()
    bucket = storage_client.get_bucket("shopadvisr-bucket")
    blob = bucket.blob("ProductData")
    blob.upload_from_filename(path)
    link = "gs://shopadvisr-bucket/ProductData"
    return link

def import_product_sets(project_id, location, gcs_uri):
    """Import images of different products in the product set.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        gcs_uri: Google Cloud Storage URI.
            Target files must be in Product Search CSV format.
    """
    client = vision.ProductSearchClient()

    # A resource that represents Google Cloud Platform location.
    location_path = f"projects/{project_id}/locations/{location}"

    # Set the input configuration along with Google Cloud Storage URI
    gcs_source = vision.ImportProductSetsGcsSource(
        csv_file_uri=gcs_uri)
    input_config = vision.ImportProductSetsInputConfig(
        gcs_source=gcs_source)

    # Import the product sets from the input URI.
    response = client.import_product_sets(
        parent=location_path, input_config=input_config)

    print('Processing operation name: {}'.format(response.operation.name))
    # synchronous check of operation status
    result = response.result()
    print('Processing done.')

    for i, status in enumerate(result.statuses):
        print('Status of processing line {} of the csv: {}'.format(
            i, status))
        # Check the status of reference image
        # `0` is the code for OK in google.rpc.Code.
        if status.code == 0:
            reference_image = result.reference_images[i]
            print(reference_image)
        else:
            print('Status code not OK: {}'.format(status.message))


def get_similar_products_file(
        project_id, location, product_set_id, product_category,
        file_path, filter):
    """Search similar products to image.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
        product_category: Category of the product.
        file_path: Local file path of the image to be searched.
        filter: Condition to be applied on the labels.
        Example for filter: (color = red OR color = blue) AND style = kids
        It will search on all products with the following labels:
        color:red AND style:kids
        color:blue AND style:kids
    """
    # product_search_client is needed only for its helper methods.
    product_search_client = vision.ProductSearchClient()
    image_annotator_client = vision.ImageAnnotatorClient()

    # Read the image as a stream of bytes.
    with open(file_path, 'rb') as image_file:
        content = image_file.read()

    # Create annotate image request along with product search feature.
    image = vision.Image(content=content)

    # product search specific parameters
    product_set_path = product_search_client.product_set_path(
        project=project_id, location=location,
        product_set=product_set_id)
    product_search_params = vision.ProductSearchParams(
        product_set=product_set_path,
        product_categories=[product_category],
        filter=filter)
    image_context = vision.ImageContext(
        product_search_params=product_search_params)

    # Search products similar to the image.
    response = image_annotator_client.product_search(
        image, image_context=image_context)

    index_time = response.product_search_results.index_time
    print('Product set index time: ')
    print(index_time)

    results = response.product_search_results.results

    print('Search results:')
    for result in results:
        product = result.product

        print('Score(Confidence): {}'.format(result.score))
        print('Image name: {}'.format(result.image))

        print('Product name: {}'.format(product.name))
        print('Product display name: {}'.format(
            product.display_name))
        print('Product description: {}\n'.format(product.description))
        print('Product labels: {}\n'.format(product.product_labels))

def main():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:\\Users\\Noor\\Desktop\\ShopAdvisr-Backend\\shopadvisr-88c9b580feff.json"

    data = getLoblawData(categories["Food"])
    print("Got data", len(data))

    link = createCSV(data)
    print("Created csv at", link)

    import_product_sets("shopadvisr", "us-east1")
    get_similar_products_file("shopadvisr", "us-east1", "4dd865abae2c6eae", "packagedgoods-v1", "temp.png", "category:food")
    
    print("Done")

if __name__ == '__main__':
    main()