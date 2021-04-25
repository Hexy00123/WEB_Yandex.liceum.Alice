import os
import json
import googletrans
from flask import Flask, request

app = Flask(__name__)
users = {}
translator = googletrans.Translator()


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

    if req['request']['original_utterance']:
        tokens = req['request']['nlu']['tokens']
        if tokens[0] in ['переведи', 'переведите'] and tokens[1] == 'слово':
            text = ' '.join(tokens[2:])
            res = translator.translate(text, scr='ru', dest='en').text
            response['response']['text'] = f'{res}'
        return json.dumps(response)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
