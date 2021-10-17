from google.cloud import vision
from dotenv import load_dotenv
import io
import os

generatedcsvPath = "ExcelGeneration/Merged_Bulk.csv"
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
        #print(content)

    image = vision.Image(content=content)

    # Performs label detection on the image file
    response = client.label_detection(image=image)
    labels = response.label_annotations
    acceptedLabels = []

    #print('Labels:')
    for label in labels:
        if True: #not label.description.title() in categories:
            acceptedLabels.append(label)

        print(label.description, label.score)
        
    return acceptedLabels

def init_import():
    #load_dotenv()
    #os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= os.getenv("GOOGLE_APPLICATION_CREDENTIALS") 

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
            catalog[data[1]][fileKeys[cat]] = data[cat].replace("[newline]", "\n")

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

    #print("Labels: ", labels)

    potentialMatches = []
    def insertMatch(product, score):
        for i in range(len(potentialMatches)):
            if potentialMatches[i][1]["Product ID"] == product["Product ID"]:
                potentialMatches[i][0] += score
                return
        
        potentialMatches.append([score, product])

    for label in labels:
        if queryType != "labels" and label.description.title() in categories:
            forcedCategory = label.description.title()
            continue
        
        labelSearch = queryType == "labels" and label.lower() or label.description.lower()
        labelValue = queryType == "labels" and len(labels) - labels.index(label) or label.score + len(label.description)

        if len(labelSearch) <= 2 or labelSearch == "the": # most likely a filler word
            continue

        for product_name in catalog:
            if labelSearch in product_name.lower():
                insertMatch(catalog[product_name], labelValue)
            
            if labelSearch in catalog[product_name]["Description"].lower():
                insertMatch(catalog[product_name], catalog[product_name]["Description"].lower().count(labelSearch) * labelValue * 0.05)
    
    """
    categorScored = { e : 0 for e in categories}
    for match in potentialMatches:
        categorScored[match[1]["Category"]] += match[0]
    
    top = max(list(categorScored.values()))
    """

    finalMatches = []
    for match in potentialMatches:
        if forcedCategory == None or match[1]["Category"] == forcedCategory: #or forcedCategory == None and categorScored[match[1]["Category"]] == top:
            finalMatches.append(match)
    
    finalMatches.sort(key=sortLabelKey, reverse=True)
    final = [e[1] for e in finalMatches[:matchLimit]]
    #print(final)
    return final

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
    #os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "C:\\Users\\Noor\\Desktop\\ShopAdvisr-Backend\\credentials.json"

    #matches = productQuery("image path", "te.png", 5)
    #matches = productQuery("labels", ["birthday", "party"], 20)
    #matches = productQuery("labels", ["birthday", "gift", "for", "wife"], 20)
    #matches = productQuery("labels", ["I", "want" "my", "baby", "to", "be", "safe", "in", "the", "car", "with", "my", "back", "turned"], 5)
    #matches = productQuery("labels", ["cat", "food"], 20)
    #matches = productQuery("labels", ["cellery"], 20)
    #matches = productQuery("labels", ["thanksgiving"], 20)

    #displayMatches(matches)
    pass


#init_import()
if __name__ == '__main__':
    main()