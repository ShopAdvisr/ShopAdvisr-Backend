# Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from google.cloud import vision
import time
import io
import os

# Globals
id_count = 0
chcd = "C:\\Users\\Noor\\Downloads\\chromedriver_win32 (1)\\chromedriver.exe"
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
Chrome_options = Options()
#Chrome_options.add_argument("--headless")

def getProductDetails(link):
    with webdriver.Chrome(chcd, chrome_options=Chrome_options) as driver:
        driver.get(link)
        wait = WebDriverWait(driver, 10)
        time.sleep(1)

        for inc in range(200, 800, 50):
            try:
                time.sleep(0.5)
                driver.execute_script("window.scrollBy(0,"+  inc +")")
                im_desc = driver.find_element_by_class_name('product-description-text__text') 
                product_desc = im_desc.text

                return product_desc

            except:
                time.sleep(0.15)
                driver.execute_script("window.scrollBy(0,-800)")
                continue


def getCategoryProducts(category, productsPerCategory, csvfile):
    global id_count
    link = categories[category]

    with webdriver.Chrome(chcd, chrome_options=Chrome_options) as driver:
        driver.get(link)
        wait = WebDriverWait(driver, 10)
        print("=========", category, "=========")

        # expand page
        for i in range(10):
            try:
                element = wait.until(expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="site-content"]/div/div/div[5]/div/div[2]/div[4]/div/button')))
                element.click()
                time.sleep(2)
            except:
                pass

        # test item data
        divs = driver.find_elements_by_class_name("product-tile--marketplace")

        for product in divs[: min(productsPerCategory, len(divs))]:
            #try:
            id_count += 1

            driver.execute_script("return arguments[0].scrollIntoView();", product)
            
            product_image = product.find_elements_by_class_name("responsive-image")[0].get_attribute("src")
            product_name = product.find_elements_by_class_name("product-name__item--name")[0].text
            product_price = product.find_elements_by_class_name("selling-price-list__item__price--now-price__value")[0].text
            old_price_el = product.find_elements_by_class_name("selling-price-list__item__price--was-price__value")
            old_price = ""
            if (len(old_price_el) > 0):
                old_price = old_price_el[0].text
            
            product_link = product.find_elements_by_class_name("product-tile__details__info__name__link")[0].get_attribute("href")
            description = getProductDetails(product_link)
            
            csvfile.write(",".join(str(e).replace(",", "-").replace("\n", "[newline]") for e in [
                    category, product_name, id_count, product_price, old_price, description, product_image, product_link
                ]) + "\n")

            print("Handled", product_name)

def automateLoblawsData(filename, productsPerCategory):
    csvfile = open(filename, 'w')
    csvfile.write(",".join([
        "Category", "Product", "Product ID", "Price", "Old Price" , "Description", "Image URL", "Product URL"
    ]) + "\n")

    for category in categories:
        getCategoryProducts(category, productsPerCategory, csvfile)
    csvfile.close()

def main():
    automateLoblawsData("Excel Generation\\Generated.csv", 75)
    print("Done")

if __name__ == '__main__':
    main()