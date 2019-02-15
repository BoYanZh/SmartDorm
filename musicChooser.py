from flask import Flask, request, render_template
from queue import Queue
import argparse
import sys
import random
import string
import logging
import json
import PlayListManager

play_list_manager = PlayListManager.PlayListManager()

SECRET_KEY = 'BoYanZhhhh'

app = Flask(__name__)

q = Queue()
commandQ = Queue()
data_list = []
play_list = []

# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)


@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/add_by_id")
def add_by_id():
    play_list_manager.add_song_by_id(request.args.get('id'))
    return 'OK'


@app.route("/add_by_name")
def add_by_name():
    play_list_manager.add_song_by_name(request.args.get('name'))
    return 'OK'


@app.route("/next")
def next():
    play_list_manager.play_next = True
    return 'OK'


@app.route('/music/list')
def musicList():
    re = ''
    for obj in play_list_manager.db.objects:
        re += '{}<br/>'.format(obj)
    return re


@app.route('/music')
def music():
    re = '<p><a href="?command=start">start</a>&nbsp; \
             <a href="?command=pause">pause</a>&nbsp; \
             <a href="?command=next">next</a>&nbsp; \
             <a href="?command=vup">vup</a>&nbsp; \
             <a href="?command=vdown">vdown</a></p>'
    for obj in play_list_manager.db.objects:
        re += '<p>{id}.<a href="?id={id}">{name}</a></p>\n'.format(
            id=obj['song_id'], name=obj['song_name'])
    if request.args.get('id') is not None:
        id = int(request.args.get('id'))
        play_list_manager.add_song_by_id(id)
    if request.args.get('command') is not None:
        command = request.args.get('command')
        if command == 'next':
            next()
        elif command in ['start', 'pause', 'next', 'vup', 'vdown']:
            commandQ.put(command)
            re += '<p>{}</p>'.format(command)
    return render_template('music.html', re=re, data_list=play_list_manager.db.objects)


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
