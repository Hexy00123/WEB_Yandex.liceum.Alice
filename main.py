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
        if users[req['session']['user_id']] == 0:
            agree_messages = ['ладно', 'куплю', 'покупаю', 'хорошо']

            if len(set(req['request']['original_utterance'].lower().split()).intersection(
                    set(agree_messages))) != 0:
                users[req['session']['user_id']] = 2
                response['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
                response['response']['end_sessiion'] = True
            else:
                response['response']['text'] = 'Все говорят «Нет». А ты купи слона'

    return json.dumps(response)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
