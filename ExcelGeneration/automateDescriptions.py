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
allItems = []

def getDescription(driver):
    for a in range(40):
        time.sleep(0.5)
        
        try:
            time.sleep(0.25)

            driver.execute_script("window.scrollBy(0, -2000)")
            time.sleep(0.25)

            driver.execute_script("window.scrollBy(0, " + str( (a * 50) % 1500 ) + ")")
            time.sleep(0.25)
            
            element = driver.find_element(By.CLASS_NAME,"product-details-page-description__body")
            return element.text
            
        except:
            pass

    return "Could not find desc"

number_threads = 4
thread_duty = 672

def handleThread(startVar):
    global finalizedWrites
    global allItems

    with webdriver.Chrome(chcd, chrome_options=Chrome_options) as driver:
        for a in range(thread_duty):
            if startVar + a >= len(allItems):
                return
                
            driver.get(allItems[startVar + a][7])
            allItems[startVar + a][5] = getDescription(driver)
            finalizedWrites.append(",".join(str(e).replace(",", "-").replace("\n", "[newline]") for e in allItems[startVar + a]) + "\n")


def reformatCSV():
    global finalizedWrites
    global allItems
    startTime = time.time()

    csvfile = open("ExcelGeneration/Finalized_Bulk.csv", 'w')
    csvfile.write(",".join([
        "Category", "Product", "Product ID", "Price", "Old Price" , "Description", "Image URL", "Product URL"
    ]) + "\n")
    
    file = open("ExcelGeneration/Generated_Bulk.csv", "r")
    allItems = [e.split(",") for e in file.read().strip().split("\n")]
    endSpot = len(allItems)
    cur = 1

    for _ in range(number_threads):
        x = threading.Thread(target=handleThread, args=(cur, ))
        x.start()
        cur += thread_duty
        time.sleep(0.05)
    
    while threading.active_count() > 1:
        print("COMPLETED: ", len(finalizedWrites))
        time.sleep(3)
        
    for item in finalizedWrites:
        csvfile.write(item)
    
    file.close()
    csvfile.close()
    endTime = time.time()
    print("Finished making", len(finalizedWrites), "in", endTime-startTime, "seconds")

def main():
    reformatCSV()
    print("Done")

if __name__ == "__main__":
    main()