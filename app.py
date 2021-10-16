from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import json
def create_app():
    app = Flask(__name__)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    @app.route('/data', methods=["GET"])
    def check():
        data = json.loads(request.get_data().decode('UTF-8'))


    return app
if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app = create_app()
    app.run(threaded=True, port=5000)
