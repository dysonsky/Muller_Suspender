from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/status')
def status():
    return jsonify({
        "status": "online",
        "bot": os.getenv("MULLER SUSPENDER X1 "),
        "admin_numbers": os.getenv("254705101667,2541144468030")
    })
