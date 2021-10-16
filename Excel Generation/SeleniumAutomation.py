from datetime import time
from logging import exception
from PIL import Image
from google.api_core.exceptions import DataLoss
from google.cloud import storage
from google.cloud import vision
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import requests
import pprint
import urllib
import time
import os

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
            f.close()

            png = Image.open("temp.png").convert('RGBA')
            background = Image.new('RGBA', png.size, (255,255,255))

            alpha_composite = Image.alpha_composite(background, png).convert("RGB")
            alpha_composite.save('temp.jpg', 'JPEG', quality=80)
            print("done")

def upload_to_bucket(blob_name, img_url, bucket_name):
    """ Upload data to a bucket"""
    links = []
    download_image(img_url)

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name + "0")
    blob.upload_from_filename("temp.jpg")
    links.append('gs://' + bucket_name + "/" + blob_name+ "0")
    
    for i in range(1, 6):
        try:
            blob = bucket.blob(blob_name + str(i))
            blob.upload_from_filename("temp" + str(i) + ".png")
            links.append('gs://' + bucket_name + "/" + blob_name+ str(i))

        except:
            pass

    return links

def googleSearch(item):

    with webdriver.Chrome(cdcd) as driver:
        driver.get("https://images.google.com/")
        wait = WebDriverWait(driver, 10)
  
        # Type the search query in the search box
        box = driver.find_element_by_xpath('//*[@id="sbtc"]/div/div[2]/input')
        box.send_keys(item)
        box.send_keys(Keys.ENTER)

        for i in range(1, 6):
            try:
                img = driver.find_element_by_xpath(
                    '//*[@id="islrg"]/div[1]/div[' +
                str(i) + ']/a[1]/div[1]/img')

                img.click()
                time.sleep(0.5)

                img2 = driver.find_element_by_xpath('//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div[2]/div/a/img')
                img2.screenshot("temp" + str(i) + ".png")
                time.sleep(0.2)
            except:
                pass


cdcd = "C:\\Users\\Noor\\Downloads\\chromedriver_win32 (1)\\chromedriver.exe"
def getLoblawData(link, productsetid, starting_id):
    with webdriver.Chrome(cdcd) as driver:
        driver.get(link)
        wait = WebDriverWait(driver, 10)
        data = []
        
        # expand page
        element = wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "primary-button")))
        #element.click()

        # test item data

        divs = driver.find_elements_by_class_name("product-tile--marketplace")
        #return [1 for i in range(len(divs))]

        id = starting_id

        for product in divs:
            try:
                driver.execute_script("return arguments[0].scrollIntoView();", product)
                product_image = product.find_elements_by_class_name("responsive-image")[0].get_attribute("src")
                product_name = product.find_elements_by_class_name("product-name__item--name")[0].text.replace(",", "").replace(" ", "_")
                product_price = product.find_elements_by_class_name("price__value")[0].text
                googleSearch(product_name)

                internal_urls = upload_to_bucket(product_name, product_image, "shopadvisr-bucket")
                for uri in internal_urls:
                    data.append([uri, product_name, productsetid, "product_id" + str(id), "general-v1", "", "price="+str(product_price), ""])

                id += 1

                #For testing
                if id >= starting_id + 5:
                    break 

            except :
                print("Could not find")
                continue
            
            

        return data

def createCSV(data):
    path = "ProductData.csv"

    with open(path, 'w') as csvfile:
        csvfile.write("\n".join([",".join(e) for e in data]))        
        csvfile.close()
        print("Product data saved to", path)
    
    storage_client = storage.Client()
    bucket = storage_client.get_bucket("shopadvisr-bucket")
    blob = bucket.blob("ProductData")
    blob.upload_from_filename(path)
    link = "gs://shopadvisr-bucket/ProductData"
    return link

from google.cloud import vision

def create_product_set(
        project_id, location, product_set_id, product_set_display_name):
    """Create a product set.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
        product_set_display_name: Display name of the product set.
    """
    client = vision.ProductSearchClient()

    # A resource that represents Google Cloud Platform location.
    location_path = f"projects/{project_id}/locations/{location}"

    # Create a product set with the product set specification in the region.
    product_set = vision.ProductSet(
            display_name=product_set_display_name)

    # The response is the product set with `name` populated.
    response = client.create_product_set(
        parent=location_path,
        product_set=product_set,
        product_set_id=product_set_id)

    # Display the product set information.
    print('Product set name: {}'.format(response.name))

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
        # Check the status of reference image
        # `0` is the code for OK in google.rpc.Code.
        if status.code != 0:
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

    print(response)

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

from google.cloud import vision

def get_product_set(project_id, location, product_set_id):
    """Get info about the product set.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
    """
    client = vision.ProductSearchClient()

    # Get the full path of the product set.
    product_set_path = client.product_set_path(
        project=project_id, location=location,
        product_set=product_set_id)

    # Get complete detail of the product set.
    product_set = client.get_product_set(name=product_set_path)

    # Display the product set information.
    print('Product set name: {}'.format(product_set.name))
    print('Product set id: {}'.format(product_set.name.split('/')[-1]))
    print('Product set display name: {}'.format(product_set.display_name))
    print('Product set index time: ')
    print(product_set.index_time)

def list_products_in_product_set(
        project_id, location, product_set_id):
    """List all products in a product set.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
    """
    client = vision.ProductSearchClient()

    # Get the full path of the product set.
    product_set_path = client.product_set_path(
        project=project_id, location=location,
        product_set=product_set_id)

    # List all the products available in the product set.
    products = client.list_products_in_product_set(name=product_set_path)

    # Display the product information.
    for product in products:
        print('Product name: {}'.format(product.name))
        print('Product id: {}'.format(product.name.split('/')[-1]))
        print('Product display name: {}'.format(product.display_name))
        print('Product description: {}'.format(product.description))
        print('Product category: {}'.format(product.product_category))
        print('Product labels: {}'.format(product.product_labels))

def list_reference_images(
        project_id, location, product_id):
    """List all images in a product.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_id: Id of the product.
    """
    client = vision.ProductSearchClient()

    # Get the full path of the product.
    product_path = client.product_path(
        project=project_id, location=location, product=product_id)

    # List all the reference images available in the product.
    reference_images = client.list_reference_images(parent=product_path)

    # Display the reference image information.
    for image in reference_images:
        print('Reference image name: {}'.format(image.name))
        print('Reference image id: {}'.format(image.name.split('/')[-1]))
        print('Reference image uri: {}'.format(image.uri))
        print('Reference image bounding polygons: {}'.format(
            image.bounding_polys))


def main():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:\\Users\\Noor\\Desktop\\ShopAdvisr-Backend\\shopadvisr-88c9b580feff.json"
    product_set_id = "product_set8"
    
    create_product_set("shopadvisr", "us-east1", product_set_id, "productTest")
    print("Created empty set")
    
    data = getLoblawData(categories["Food"], product_set_id, 200)
    print("Got data", len(data))

    link = createCSV(data)
    print("Created csv at", link)

    import_product_sets("shopadvisr", "us-east1", link)
    print("Imported product data")
    
    #get_product_set("shopadvisr", "us-east1", product_set_id)
    #list_products_in_product_set("shopadvisr", "us-east1", product_set_id)
    #list_reference_images("shopadvisr", "us-east1", "product_id100")
    #get_similar_products_file("shopadvisr", "us-east1", product_set_id, "general-v1", "ref.jpg", "")  

    #data = getLoblawData(categories["Food"], product_set_id)
    #print(len(data))

if __name__ == '__main__':
    main()