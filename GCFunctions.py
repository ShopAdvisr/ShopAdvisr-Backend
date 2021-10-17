from google.cloud import vision
from dotenv import load_dotenv
import io
import os

generatedcsvPath = "ExcelGeneration/Generated_Bulk.csv"
categories = {
    "Food" : "https://www.loblaws.ca/food/c/27985?navid=flyout-L2-Food",
    "Baby" : "https://www.loblaws.ca/baby/c/27987?navid=flyout-L2-Baby",
    "Home & Kitchen" : "https://www.loblaws.ca/home-and-living/c/27986?navid=flyout-L2-Home%20&%20Kitchen",
    "Office & School Supplies" : "https://www.loblaws.ca/office-school-supplies/c/27991?navid=flyout-L2-Office-and-School-Supplies",
    "Electronics & Batteries" : "https://www.loblaws.ca/computers-electronics/c/27992?navid=flyout-L2-Electronics%20&%20Batteries",
    "Health & Beauty" : "https://www.loblaws.ca/health-beauty/c/27994?navid=flyout-L2-Health-and-Beauty",
    "Pet Supplies" : "https://www.loblaws.ca/pet-supplies/c/27988?navid=flyout-L2-Pet-Supplies",
    "Toys- Games & Hobbies" : "https://www.loblaws.ca/toys-games-hobbies/c/27990?navid=flyout-L2-Toys-Games-and-Hobbies"
}
catalog = None

def imageRecognition(img, isBinary = False):
    client = vision.ImageAnnotatorClient()
    if isBinary:
        content = img
    else:
        # Loads the image into memory
        with io.open(img, 'rb') as image_file:
            content = image_file.read()

    image = vision.Image(content=content)

    # Performs label detection on the image file
    response = client.label_detection(image=image)
    labels = response.label_annotations

    acceptedLabels = []

    #print('Labels:')
    for label in labels:
        if True: #not label.description.title() in categories:
            acceptedLabels.append(label)

        #print(label.description, label.score)
        
    return acceptedLabels

def init_import():
    #os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    import random
    global catalog

    print("Importing file data")
    file = open(generatedcsvPath, "r")
    allItems = file.read().split("\n")
    fileKeys = ["Category", "Product", "Product ID", "Price", "Old Price", "Description", "Image URL", "Product URL"]
    catalog = {}
    for e in allItems[1:]:
        if e.count(",") == 0: break
        data = e.split(",")
        catalog[data[1]] = {}
        
        for cat in range(len(fileKeys)):
            catalog[data[1]][fileKeys[cat]] = data[cat]#.replace("[newline]", "\n")

        catalog[data[1]]["Aisle"] = random.randint(1, 20) #Later overriten by product management 
        #print(catalog[data[1]])

    file.close()

def sortLabelKey(match):
    return match[0]

def productQuery(queryType, queryInfo, matchLimit, forcedCategory=None):
    if catalog == None:
        init_import()

    labels = None
    if queryType == "image path":
        labels = imageRecognition(queryInfo)
    elif queryType == "labels":
        labels = queryInfo
    elif queryType == "image binary":
        labels = imageRecognition(queryInfo, True)

    potentialMatches = []

    for label in labels[:5]:
        if queryType != "labels" and label.description.title() in categories:
            forcedCategory = label.description.title()
            continue

        for product_name in catalog:
            if queryType == "labels":
                if label.lower() in product_name.lower():
                    potentialMatches.append([len(labels) - labels.index(label), catalog[product_name]])
            else:
                if label.description.lower() in product_name.lower():
                    potentialMatches.append([label.score + len(label.description), catalog[product_name]])
    
    categorScored = { e : 0 for e in categories}
    for match in potentialMatches:
        categorScored[match[1]["Category"]] += match[0]
    
    top = max(list(categorScored.values()))
    finalMatches = []
    for match in potentialMatches:
        if match[1]["Category"] == forcedCategory or forcedCategory == None and categorScored[match[1]["Category"]] == top:
            finalMatches.append(match)
    
    finalMatches.sort(key=sortLabelKey, reverse=True)
    return [e[1] for e in finalMatches[:matchLimit]]

def displayMatches(matches):
    i = len(matches)
    for match in matches[::-1]:
        print(" ====== Product Match #" + str(i) + " ====== ")
        for item in match:
            print(item, match[item])
        i -= 1
      

def main():
    #load_dotenv()
    #os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:\\Users\\Noor\\Desktop\\ShopAdvisr-Backend\\shopadvisr-88c9b580feff.json"
    matches = productQuery("image path", "ref.jpg", 5)
    displayMatches(matches)
    pass


init_import()
if __name__ == '__main__':
    main()