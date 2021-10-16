import os
from dotenv import load_dotenv
import requests
import time
import sys
import pprint
import csv

load_dotenv()
#TODO: CHECK IF WORD IS NOUN
class ProductSuggestion:
    endpoint = "https://api.assemblyai.com/v2/transcript"

    TOKEN = os.getenv('ASSEMBLYTOKEN')
    headers = {
        "authorization": TOKEN,
        "content-type": "application/json"
    }

    def __init__(self):
        print(True)



    def run(self, audio):
        print(audio)
        sys.stdout.flush()
        audio_url = self.upload_audio(audio)
        print(audio_url)
        sys.stdout.flush()
        audio_id = self.process_audio(audio_url)
        print(audio_id)
        sys.stdout.flush()

        keywords, topics = self.get_audio_data(audio_id)
        print(keywords, topics)
        return {'words':keywords,'topics':topics}
        associated_words = self.get_associated_words(keywords)
        # for word in associated_words:



    def get_associated_words(self, keywords):
        all_words = set()
        for k in keywords:
            for w in k[0].split():
                related = requests.get(f"https://api.datamuse.com/words?rel_trg={w}").json()

                words = {(i['word'], k[1]*1000 * i["score"]) for i in related if i['word']}
                all_words.union(words)
        return all_words

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
        print(data)
        sys.stdout.flush()

        keywords = [(i['text'], i['rank']) for i in data['auto_highlights_result']['results']]

        topics = data["iab_categories_result"]['summary']
        return keywords, topics

    def upload_audio(self, audio):
        response = requests.post('https://api.assemblyai.com/v2/upload',
                                 headers=self.headers,
                                 data=audio)
        return response.json()["upload_url"]
ProductSuggestion()