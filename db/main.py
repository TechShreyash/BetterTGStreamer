from flask import Flask,jsonify
from pymongo import MongoClient
import os

# Replace YOUR_MONGO_DB_URL with your MongoDB URL, same as used on bot
MONGO_DB_URL = "YOUR_MONGO_DB_URL"

db = MongoClient(MONGO_DB_URL)['BetterTGStreamer']['files']

app = Flask(__name__)

@app.route('/get/<hash>')
def get_file(hash):
    file = db.find_one({'hash': hash})
    file.pop('_id')
    return jsonify(file)

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))