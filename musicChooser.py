from flask import Flask, request
from queue import Queue
import argparse
import sys
import random
import string
import logging
import glob

SECRET_KEY = 'BoYanZhhhh'

app = Flask(__name__)

q = Queue()

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# identify user's identity
@app.route("/")
def hello():
    return "Hello World!"


@app.route("/music/api")
def musicApi():
    try:
        if request.args.get('secretKey') != SECRET_KEY or \
           request.args.get('action') is None:
            raise Exception('invalid')
        action = request.args.get('action')
        if action == 'get':
            if q.empty():
                return 'Empty queue'
            else:
                return q.get()
    except Exception as e:
        return 'Request Error:' + str(e)


@app.route('/music')
def music():
    re = ''
    if (request.args.get('id') is not None):
        re += '<a href="/music">Back</a>'
        id = int(request.args.get('id'))
        fileList = glob.glob(r'*.mp3')
        if id >= 1 and id <= len(fileList):
            q.put(str(id))
    else:
        id = 1
        for fileName in glob.glob(r'*.mp3'):
            re += '<p>' + str(id) + '. ' + \
               '<a href="?id=' + str(id) + '">' + fileName[:-4] + '</a>' + \
               '</p>\n'
            id += 1
    return re


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Music Chooser Server.')
    parser.add_argument('-ip', default='0.0.0.0', type=str)
    parser.add_argument('-port', default='5000', type=str)
    parser.add_argument('-sk', default='BoYanZhhhh', type=str)
    args = vars(parser.parse_args())
    SECRET_KEY = args['sk']
    if SECRET_KEY == 'YourSecretKey':
        SECRET_KEY = ''.join(
            random.sample(string.ascii_letters + string.digits, 8))
    print('Your Secret Key: ' + SECRET_KEY)
    app.run(host=args['ip'], port=args['port'])
