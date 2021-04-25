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
    response['response']['text'] = 'Странная команда'

    tokens = req['request']['nlu']['tokens']
    if tokens[0] in ['переведи', 'переведите'] and tokens[1] == 'слово':
        text = ' '.join(tokens[2:])
        response['response']['text'] = f'Нужен перевод фразы: "{text}"'

    return json.dumps(response)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
