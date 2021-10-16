import os
from google.cloud import storage
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import time

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

def upload_to_bucket(blob_name, path_to_file, bucket_name):
    """ Upload data to a bucket"""
    storage_client = storage.Client()

    bucket = storage_client.get_bucket(bucket_name)

    blob = bucket.blob(blob_name)
    #blob.upload_from_filename(path_to_file)
    link = 'gs://' + blob.path_helper(bucket_name, blob_name)

    return link

def getLoblawData():
    #This example requires Selenium WebDriver 3.13 or newer
    with webdriver.Chrome("C:\\Users\\Noor\\Downloads\\chromedriver_win32 (1)\\chromedriver.exe") as driver:
        driver.get("https://www.loblaws.ca/food/c/27985?navid=flyout-L2-Food")
        wait = WebDriverWait(driver, 10)
        
        # expand page
        element = wait.until(expected_conditions. element_to_be_clickable((By.CLASS_NAME, "primary-button")))
        #element.click()

        # test item data
        a = driver.find_elements_by_class_name("product-tracking")
        print(len(a))

def createCSV():
    pass
        

def main():
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:\\Users\\Noor\\Desktop\\ShopAdvisr-Backend\\shopadvisr-88c9b580feff.json"
    b = upload_to_bucket("Hotwheels", "C:\\Users\\Noor\\Desktop\\ShopAdvisr-Backend\\Excel Generation\\Images\\20098552_front_a06_@2.png", "shopadvisr-bucket")
    print(b)
    """

    getLoblawData()

if __name__ == '__main__':
    main()