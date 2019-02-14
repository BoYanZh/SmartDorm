from flask import Flask, request
from queue import Queue
import argparse
import sys
import random
import string
import logging
import glob
import json

app = Flask(__name__)

q = Queue()
commandQ = Queue()
data_list = []
play_list = []

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# identify user's identity
@app.route("/")
def hello():
    return "Hello World!"


@app.route('/music/json', methods=['POST'])
def fetchJson():
    global data_list
    if request.method == 'POST':
        data = request.get_data()
        for music in data.decode("utf-8").split('\n')[:-1]:
            if music not in data_list:
                data_list.append(music)
        print(data_list)
        return "\n".join(data_list)


@app.route("/music/api")
def musicApi():
    try:
        # if request.args.get('secretKey') != SECRET_KEY or \
        #    request.args.get('action') is None:
        #     raise Exception('invalid')
        if request.args.get('action') == 'get':
            if q.empty():
                return random.choice(data_list)
            else:
                play_list.pop[0]
                return q.get()
        if request.args.get('action') == 'command':
            if commandQ.empty():
                return ''
            else:
                return commandQ.get()
    except Exception as e:
        return 'Request Error:' + str(e)


@app.route('/music/list')
def musicList():
    re = ''
    for fileName in play_list:
        re += '{}<br/>'.format(fileName)
    return re


@app.route('/music')
def music():
    re = '<p><a href="?command=start">start</a>&nbsp; \
             <a href="?command=pause">pause</a>&nbsp; \
             <a href="?command=vup">vup</a>&nbsp; \
             <a href="?command=vdown">vdown</a></p>'

    for idx, fileName in enumerate(data_list):
        re += '<p>{id}.<a href="?id={id}">{name}</a></p>\n'.format(
            id=str(idx), name=fileName)
    if (request.args.get('id') is not None):
        id = int(request.args.get('id'))
        if id >= 0 and id <= len(data_list):
            play_list.append(data_list[id])
            q.put(data_list[id])
            re += '<p>{name} Added</p>'.format(name=data_list[id])
    if (request.args.get('command') is not None):
        command = request.args.get('command')
        if command in ['start', 'pause', 'vup', 'vdown']:
            commandQ.put(command)
            re += '<p>{}</p>'.format(command)
    return re


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Music Chooser Server.')
    parser.add_argument('-ip', default='0.0.0.0', type=str)
    parser.add_argument('-port', default='5001', type=str)
    parser.add_argument('-sk', default='BoYanZhhhh', type=str)
    args = vars(parser.parse_args())
    SECRET_KEY = args['sk']
    if SECRET_KEY == 'YourSecretKey':
        SECRET_KEY = ''.join(
            random.sample(string.ascii_letters + string.digits, 8))
    print('start')
    app.run(host=args['ip'], port=args['port'])
