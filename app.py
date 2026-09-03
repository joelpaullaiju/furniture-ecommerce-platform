from flask import Flask, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Connect to Firestore
db = firestore.client()

@app.route("/")
def home():
    return jsonify({"status": "success", "message": "Firebase & Flask Backend Connected!"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)