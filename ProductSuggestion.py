import math
import os
from dotenv import load_dotenv
import requests
import time
import sys
import pprint
import csv
from ProductDb import db
import spacy
from collections import defaultdict

load_dotenv()
nlp = spacy.load('en_core_web_sm')


# TODO: CHECK IF WORD IS NOUN
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
        audio_id = self.process_audio(audio_url)

        keywords, topics = self.get_audio_data(audio_id)
        associated_words = self.get_associated_words(keywords)

        results = []
        print(associated_words)
        for word in associated_words:
            results = results + db.product_search(word)

        return results

    def get_associated_words(self, keywords):
        all_words = defaultdict(int)
        for k in keywords:
            for w in k[0].split():
                if nlp(w)[0].pos_ != "NOUN":
                    continue
                related = requests.get(f"https://api.datamuse.com/words?rel_trg={w}").json()
                for i in related:
                    if nlp(i['word'])[0].pos_ == "NOUN":
                        all_words[i['word']] += k[1] * 1000 + i["score"]

                all_words[w] = math.inf
        return sorted(set(i for i in all_words.keys()), key=lambda k: all_words[k], reverse=True)

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
