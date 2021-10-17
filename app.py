import sys

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import json
import base64
from ProductSuggestion import ProductSuggestion
import GCFunctions
GCFunctions.init_import()

app = Flask(__name__)
productSuggestion = ProductSuggestion()
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/data', methods=["GET"])
def check():
    data = json.loads(request.get_data().decode('UTF-8'))


@app.route('/suggestions', methods=["GET","POST"])
def product_suggestion():

    data = request.get_data()


    return productSuggestion.run(base64.decodebytes(data))

@app.route('/ocr',methods=["POST"])
def ocr():
    data = request.get_data()
    
    results = GCFunctions.productQuery("image binary", data, 5)
    return json.dumps(results)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)

