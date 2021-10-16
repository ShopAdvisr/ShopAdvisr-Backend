import os
from dotenv import load_dotenv
import requests
import time
import pprint

load_dotenv()


class ProductSuggestion:
    endpoint = "https://api.assemblyai.com/v2/transcript"

    TOKEN = os.getenv('ASSEMBLYTOKEN')
    headers = {
        "authorization": TOKEN,
        "content-type": "application/json"
    }

    def __init__(self):
        pass

    def run(self, audio):
        audio_url = self.upload_audio(audio)
        audio_id = self.process_audio(audio)

        keywords, topics = self.get_audio_data(audio_id)
        print(keywords,topics)

    def process_audio(self, audio_url):
        req_data = {
            "auto_highlights": True,
            "iab_categories": True,
            "audio_url": audio_url
        }
        response = requests.post(self.endpoint, json=req_data, headers=self.headers)
        data = response.json()
        return data['id']

    def get_audio_data(self, audio_id):

        completed = False
        while not completed:
            time.sleep(1)
            audio_endpoint = "https://api.assemblyai.com/v2/transcript/" + audio_id
            response = requests.get(audio_endpoint, headers=self.headers)
            data = response.json()
            if data["status"] in ["error", "completed"]:
                completed = True

        keywords = [(i['text'], i['rank']) for i in data['auto_highlights_result']['results']]

        topics = data["iab_categories_result"]['summary']
        return keywords, topics

    def upload_audio(self, audio):
        response = requests.post('https://api.assemblyai.com/v2/upload',
                                 headers=self.headers,
                                 data=audio)
        return response.json()["upload_url"]
