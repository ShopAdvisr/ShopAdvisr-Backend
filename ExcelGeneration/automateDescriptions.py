from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import threading
import time

Chrome_options = Options()
Chrome_options.add_argument("--headless")
chcd = "C:\\Users\\Noor\\Downloads\\chromedriver_win32 (1)\\chromedriver.exe"
finalizedWrites = []

def getDescription(link):
    with webdriver.Chrome(chcd, chrome_options=Chrome_options) as driver:
        print(link)
        driver.get(link)
        wait = WebDriverWait(driver, 10)

        for a in range(40):
            time.sleep(0.5)
            try:
                time.sleep(0.25)

                driver.execute_script("window.scrollBy(0, -2000)")
                time.sleep(0.25)

                driver.execute_script("window.scrollBy(0, " + str( (a * 50) % 1500 ) + ")")
                time.sleep(0.25)
                
                elements = driver.find_elements_by_class_name('product-details-page-description__body')
                if len(elements) > 0:
                    return elements[0].text
                
            except:
                pass

def handleItem(item):
    global finalizedWrites
    item[5] = getDescription(item[7])
    finalizedWrites.append(",".join(str(e).replace(",", "-").replace("\n", "[newline]") for e in item) + "\n")

number_threads = 15
def reformatCSV():
    global finalizedWrites
    csvfile = open("ExcelGeneration/Finalized_Bulk.csv", 'w')
    csvfile.write(",".join([
        "Category", "Product", "Product ID", "Price", "Old Price" , "Description", "Image URL", "Product URL"
    ]) + "\n")
    
    file = open("ExcelGeneration/Generated_Bulk.csv", "r")
    allItems = [e.split(",") for e in file.read().split("\n")]
    cur = 0
    endSpot = len(allItems)

    while cur < 20:
        if threading.active_count() < number_threads:
            cur += 1
            if (cur % 50 == 0):
                print(" ======================= ", cur, " ======================= ")

            x = threading.Thread(target=handleItem, args=(allItems[cur],))
            x.start()
            time.sleep(0.05)
        else:
            time.sleep(0.4)
    
    while threading.active_count() > 1:
        print("Waiting to wrap up")
        time.sleep(1)
        
    for item in finalizedWrites:
        csvfile.write(item)
    
    file.close()
    csvfile.close()

def main():
    reformatCSV()
    print("Done")

if __name__ == "__main__":
    main()