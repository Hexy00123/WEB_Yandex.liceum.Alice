import os
import json
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=["GET"])
def start_page():
    return 'Стартовая страница'


@app.route('/', methods=['POST'])
def main():
    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }
    req = request.json
    if req['session']['new']:
        response['response']['text'] = 'Привет!'
    else:
        response['response']['text'] = 'Рада снова вас видеть здесь!'

    return json.dumps(response)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)