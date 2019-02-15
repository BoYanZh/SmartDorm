# coding = utf-8
import os
import time
import signal
import re
import threading as td
from queue import Queue
import random
from urllib.request import urlopen, urlretrieve, Request
from urllib.parse import urlencode
import json
import subprocess
from PIL import Image
import glob
import signal

var_set = json.load(open('config.json'))
HEAD = {'User-Agent': 'BiLiBiLi Audio Streamer/1.0.0 (1328410180@qq.com)', "Cookie": "buvid3=91585DCB-8DE6-4C63-9173-45C98A2A511C77387infoc; LIVE_BUVID=AUTO5015502255888665"}

class JsonDB:
    def __init__(self):
        if not os.path.exists("db.json"):
            f = open("db.json", "w")
            json.dump([], f)
            f.close()
            self.objects = []
        else:
            f = open("db.json", 'r')
            self.objects = json.load(f)
            f.close()

    def save(self):
        f = open("db.json", "w")
        json.dump(self.objects, f)
        f.close()

    def append(self, obj):
        self.objects.append(obj)

    def get_object_by_key(self, key, value):
        for obj in self.objects:
            if obj[key] == value:
                return obj


class PlayListManager:
    def __init__(self):
        print('Initializing play list...')
        self.play_list_ids = []
        self.file_names = []
        self.q_new_song = Queue()
        self.play_next = False
        self.pause = False
        self.db = JsonDB()
        self.now_adding = []
        try:
            self.ffserver = subprocess.Popen(
                        ["ffserver", "-f", var_set['ffserver_config']],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True
                    )
        except FileNotFoundError:
            print("ffserver not found!")

        self.song_path = os.path.join(var_set['download_path'], 'song')
        # load local playlist
        if not os.path.exists(var_set['download_path']):
            os.mkdir(var_set['download_path'])
            os.mkdir(self.song_path)
            self.add_song_by_id(521416315)

        self.player = td.Thread(target=self._player, name='Player')
        self.player.start()

    def next(self):
        self.play_next = True
        return

    def add_song_by_name_or_link(self, name):
        if not name:
            return
        print('Searching', name)
        try:
            id = re.search(r'http://music\.163\.com/song/(\d+)/', name)
            if id:
                self.add_song_by_id(int(id.group(1)))
                return

            id = re.search(r'https://www.bilibili.com/video/av(\d+)', name)
            if id:
                self.add_song_by_av(int(id.group(1)))
                return

            api_url = 'https://api.imjad.cn/cloudmusic/?'
            code = urlencode({'type': 'search', 'limit': 1, 's': name})
            code = json.loads(urlopen(api_url + code).read().decode('utf-8'))
            if code['code'] == 200:
                song_id = code['result']['songs'][0]['id']
                self.add_song_by_id(song_id)
        except Exception as e:  # 防炸
            print('shit')
            print(e)

    def add_song_by_av(self, aid):
        print('Adding', aid)
        try:
            song_id = int(aid)
            if song_id in self.now_adding:
                return
            self.now_adding.append(song_id)

            # check id
            old_obj = self.db.get_object_by_key('song_id', 'av{}'.format(song_id))
            if old_obj:
                self.q_new_song.put(old_obj)
                self.play_next = True
                self.now_adding.append(song_id)
                return

            # get song url
            req = Request('http://api.imjad.cn/bilibili/v2/?aid=' + str(song_id) + '&type=archieve', headers=HEAD)
            info = json.loads(
                urlopen(req).read().decode('utf-8')
            )
            if info['code'] != 0:
                print('[error]')
                print(info)
                return

            song_name = info['data']['title']
            song_tname = info['data']['tname']
            song_uploader = info['data']['owner']['name']


            # download song
            mp3_file_name = 'av%012d' % song_id + '.mp3'

            print('Downloading...')
            print('songName: ' + song_name)
            print('songUploader: ' + song_uploader)
            req = Request('http://api.bilibili.com/playurl?callback=callbackfunction&aid={}&page=1&platform=html5&quality=1&vtype=mp4'.format(song_id), headers=HEAD)
            song_url = json.loads(
                urlopen(req).read().decode('utf-8')
            )['durl'][0]['url']
            print('songUrl: ' + song_url)
            req = Request(song_url, headers=HEAD)
            if os.path.exists(os.path.join(self.song_path, mp3_file_name)):
                os.remove(os.path.join(self.song_path, mp3_file_name))
            savep = subprocess.Popen(
                ["ffmpeg", "-i", "pipe:0", os.path.join(self.song_path, mp3_file_name)],
                stdin=subprocess.PIPE,
            )
            tmp_file = urlopen(req)
            while True:
                buf = tmp_file.read(1024)
                savep.stdin.write(buf)
                savep.stdin.flush()
                if len(buf) < 1024 or buf[-1] == b'\0':
                    print(len(buf), buf[-1])
                    break

            savep.stdin.write(b'\0')
            savep.stdin.flush()
            savep.send_signal(signal.SIGINT)
            print("downloaded")
            savep.wait()
            savep.kill()
            new_song_obj = {
                'mp3_file_name': mp3_file_name,
                'song_url': song_url,
                'song_name': song_name,
                'song_id': 'av{}'.format(song_id),
                'states': 'downloaded',
                'ar': song_uploader,
                'al': 'bilibili_'+song_tname,
                'detail': info,
            }
            self.db.append(new_song_obj)
            self.db.save()
            print(new_song_obj)

            # push q_new_song
            self.q_new_song.put(new_song_obj)
            self.next()
            self.now_adding.remove(song_id)
        except Exception as e:  # 防炸
            print('shit')
            print(e)

    def add_song_by_id(self, song_id):
        print('Adding', song_id)
        try:
            song_id = int(song_id)
            if song_id in self.now_adding:
                return
            self.now_adding.append(song_id)

            # check id
            old_obj = self.db.get_object_by_key('song_id', song_id)
            if old_obj:
                self.q_new_song.put(old_obj)
                self.play_next = True
                self.now_adding.append(song_id)
                return

            # get song url
            info = json.loads(
                urlopen('https://api.imjad.cn/cloudmusic/?id=' + str(song_id) + '&br=320000').read().decode('utf-8')
            )
            if info['code'] != 200:
                print('[error]')
                print(info)
                return
            song_url = info['data'][0]['url']
            detail_info = json.loads(
                urlopen('https://api.imjad.cn/cloudmusic/?type=detail&id=' + str(song_id)).read().decode('utf-8')
            )
            if detail_info['code'] != 200:
                print('[error]')
                print(detail_info)
                return
            song_name = detail_info['songs'][0]['name']

            # download song
            mp3_file_name = '%012d' % song_id + '.mp3'

            print('Downloading...')
            print('songName: ' + song_name)
            print('songUrl: ' + song_url)
            urlretrieve(song_url, os.path.join(self.song_path, mp3_file_name))
            new_song_obj = {
                'mp3_file_name': mp3_file_name,
                'song_url': song_url,
                'song_name': song_name,
                'song_id': song_id,
                'states': 'downloaded',
                'ar': ' '.join([ar['name'] for ar in detail_info['songs'][0]['ar']]),
                'al': detail_info['songs'][0]['al']['name'],
                'detail': detail_info,
            }
            self.db.append(new_song_obj)
            self.db.save()

            # push q_new_song
            self.q_new_song.put(new_song_obj)
            self.next()
            self.now_adding.remove(song_id)
        except Exception as e:  # 防炸
            print('shit')
            print(e)

    def del_song_by_id(self, song_id):
        # del song files
        try:
            self.file_names = os.listdir(self.song_path)
            self.play_list_ids = []
            for file_name in self.file_names:
                self.play_list_ids.append(int(file_name[:10]))

            if song_id in self.play_list_ids:
                for file in glob.glob(os.path.join(self.song_path, '%010d' % song_id + '*')):
                    os.remove(file)
            print('Deleted')
        except Exception as e:  # 防炸
            print('shit')
            print(e)

    def _player(self):
        while True:
            # get next song
            if not self.q_new_song.empty():
                nxt_song = self.q_new_song.get()
            else:
                nxt_song = random.choice(self.db.objects)

            song_path = os.path.join(var_set['download_path'], 'song')
            mp3_file_path = os.path.join(song_path, nxt_song['mp3_file_name'])
            p = subprocess.Popen(
                ["ffmpeg", "-re", "-i", mp3_file_path, "http://127.0.0.1:8090/feed1.ffm"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            p_start_time = time.time()
            t = 0
            while p.poll() is None:
                time.sleep(0.1)

                # Pause
                if self.pause:
                    t += int(time.time() - p_start_time)
                    p.send_signal(2)
                    p.wait()
                    p.kill()
                    silent = subprocess.Popen(
                        ["ffmpeg", "-re", "-f", "lavfi", "-i", "aevalsrc=0", "http://127.0.0.1:8090/feed1.ffm"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True
                    )
                    print("Paused, will start at", t)
                    while self.pause:
                        time.sleep(0.01)
                    silent.send_signal(2)
                    silent.wait()
                    silent.kill()
                    time.sleep(0.1)
                    print("Starting at", t)
                    p_start_time = time.time()
                    p = subprocess.Popen(
                        ["ffmpeg", "-ss", str(t), "-re", "-i", mp3_file_path, "http://127.0.0.1:8090/feed1.ffm"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True
                    )

                # Next
                try:
                    if self.play_next:
                        p.send_signal(2)
                        self.play_next = False
                        p.wait()
                except ValueError:
                    p.kill()
                    self.play_next = False
            # print('FFmpeg Ended with code', p.poll())
            p.kill()
