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
thread_duty = 75
start_duty = 7501

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

    for st in range(start_duty, 8100, 300):

        csvfile = open("ExcelGeneration/Finalized_Bulk" + str(st) + ".csv", 'w')
        csvfile.write(",".join([
            "Category", "Product", "Product ID", "Price", "Old Price" , "Description", "Image URL", "Product URL"
        ]) + "\n")
        
        file = open("ExcelGeneration/Generated_Bulk.csv", "r")
        allItems = [e.split(",") for e in file.read().strip().split("\n")]
        #endSpot = len(allItems)
        cur = st

        for _ in range(number_threads):
            x = threading.Thread(target=handleThread, args=(cur, ))
            x.start()
            cur += thread_duty
            time.sleep(0.05)
        
        while threading.active_count() > 1:
            print("COMPLETED: ", len(finalizedWrites))
            time.sleep(3)
            
        for item in finalizedWrites:
            try:
                csvfile.write(item)
            except:
                print("====COULD NOT WRITE ON SOMETHING=====")
        
        file.close()
        csvfile.close()
        endTime = time.time()
        print("Finished making", len(finalizedWrites), "in", endTime-startTime, "seconds")

        finalizedWrites = []
        if (st >= start_duty + thread_duty*number_threads*2):
            print("Free up system memory, ending program here")
            print("Please rerun in 2-5 minutes")
            return

        print("Waiting a minute before next patch")
        time.sleep(60)


def makeMerged():
    csvfile = open("ExcelGeneration/Merged_Bulk.csv", 'w')
    csvfile.write(",".join([
        "Category", "Product", "Product ID", "Price", "Old Price" , "Description", "Image URL", "Product URL"
    ]) + "\n")
    
    for st in range(1, 7802, 300):
        file = open("ExcelGeneration/Finalized_Bulk" + str(st) + ".csv", 'r')
        allItems = [e for e in file.read().strip().split("\n")[1:]]
        for line_str in allItems:
            csvfile.write(line_str + "\n")
        file.close()
    
    csvfile.close()

def main():
    #reformatCSV()
    #makeMerged()
    #print("Done")
    pass

if __name__ == "__main__":
    main()