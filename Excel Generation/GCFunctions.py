from google.cloud import vision
import io
import os

def imageRecognition(img):
    client = vision.ImageAnnotatorClient()

    # Loads the image into memory
    with io.open(img, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # Performs label detection on the image file
    response = client.label_detection(image=image)
    labels = response.label_annotations

    print('Labels:')
    for label in labels:
        print(label.description, label.score)

def main():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:\\Users\\Noor\\Desktop\\ShopAdvisr-Backend\\shopadvisr-88c9b580feff.json"
    imageRecognition("temp3.png")

if __name__ == '__main__':
    main()