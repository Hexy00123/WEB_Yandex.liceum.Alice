import os
import json
from flask import Flask, request

app = Flask(__name__)
users = {}


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
        users[req['session']['user_id']] = 0
        response['response']['text'] = 'Привет!\nКупи слона!'
    else:
        if users[req['session']['user_id']] == 1:
            response['response']['text'] = 'Stage 1'

    return json.dumps(response)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
