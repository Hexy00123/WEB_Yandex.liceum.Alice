from flask import Flask, request
import logging
import json
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

cities = {
    'москва': ["213044/cbcaa176ec8643cdd235", '1030494/4471dc38b68b51205cea', 'россия'],
    'нью-йорк': ['1652229/addf48648aa6c07463b2', '1652229/9a4f8cee76dae7e184f0', 'сша'],
    'париж': ["1652229/c69451c1dc1a91edff68", "213044/f71830424d2a24063f53", 'франция']
}

sessionStorage = {}


@app.route('/', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'first_name': None,
            'game_started': False,
            'city': '',
            'country': '',
            'is_country': False,
        }
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            sessionStorage[user_id]['guessed_cities'] = []
            res['response'][
                'text'] = f'Приятно познакомиться, {first_name.title()}. Я Алиса. Отгадаешь город по фото?'
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                },
                {
                    'title': 'Покажи город на карте',
                    'hide': True
                }
            ]
    else:
        if not sessionStorage[user_id]['game_started']:
            if 'да' in req['request']['nlu']['tokens']:
                if len(sessionStorage[user_id]['guessed_cities']) == 3:
                    res['response']['text'] = 'Ты отгадал все города!'
                    res['end_session'] = True
                else:
                    sessionStorage[user_id]['game_started'] = True
                    sessionStorage[user_id]['attempt'] = 1
                    play_game(res, req)
            elif 'нет' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Ну и ладно!'
                res['end_session'] = True
            else:
                if len(sessionStorage[user_id]['guessed_cities']) > 0 and sessionStorage[user_id][
                    "city"] != '':
                    site = f'https://yandex.ru/maps/?mode=search&text={sessionStorage[user_id]["city"]}'
                    res['response']['text'] = f'Ссылка на город: {site}'
                else:
                    res['response']['text'] = f'Вы еще не играли'
                res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    },
                    {
                        'title': 'Покажи город на карте',
                        'hide': True
                    }
                ]
        else:
            play_game(res, req)


def play_game(res, req):
    user_id = req['session']['user_id']
    attempt = sessionStorage[user_id]['attempt']
    if attempt == 1 and not sessionStorage[user_id]['is_country']:
        city = random.choice(list(cities))
        while city in sessionStorage[user_id]['guessed_cities']:
            city = random.choice(list(cities))
        sessionStorage[user_id]['city'] = city
        sessionStorage[user_id]['country'] = cities[city][2]

        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card'][
            'title'] = f'{sessionStorage[user_id]["first_name"]}, Что это за город?'
        res['response']['card']['image_id'] = cities[city][attempt - 1]
        res['response']['text'] = 'Тогда сыграем!'
    elif not sessionStorage[user_id]['is_country']:
        city = sessionStorage[user_id]['city']
        if get_city(req) == city:
            res['response'][
                'text'] = f'{sessionStorage[user_id]["first_name"]}, Правильно! А что это за страна?'
            sessionStorage[user_id]['guessed_cities'].append(city)
            sessionStorage[user_id]['game_started'] = True
            sessionStorage[user_id]['is_country'] = True
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                },
                {
                    'title': 'Покажи город на карте',
                    'hide': True
                }
            ]
            return
        else:
            if attempt == 3:
                res['response'][
                    'text'] = f'{sessionStorage[user_id]["first_name"]}, Вы пытались.' \
                              f' Это {city.title()}. Сыграем ещё?'
                sessionStorage[user_id]['game_started'] = False
                sessionStorage[user_id]['guessed_cities'].append(city)
                return
            else:
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card'][
                    'title'] = f'{sessionStorage[user_id]["first_name"]}, Неправильно. ' \
                               f'Вот тебе дополнительное фото'
                res['response']['card']['image_id'] = cities[city][attempt - 1]
                res['response'][
                    'text'] = f'{sessionStorage[user_id]["first_name"]}, А вот и не угадал!'
    else:
        if req['request']['nlu']['tokens'][0] == sessionStorage[user_id]['country']:

            res['response'][
                'text'] = f'{sessionStorage[user_id]["first_name"]}, Правильно! Сыграем еще?'
            sessionStorage[user_id]['guessed_cities'].append(
                sessionStorage[user_id]['city'])
            sessionStorage[user_id]['game_started'] = False
            sessionStorage[user_id]['is_country'] = False
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                }]
        else:
            res['response'][
                'text'] = f'{sessionStorage[user_id]["first_name"]}, Не верно, ' \
                          f'это слово похоже на {sessionStorage[user_id]["country"][::2]}'

    sessionStorage[user_id]['attempt'] += 1


def get_city(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('city', None)


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
