# SmartDorm
Make Your Dorm Smarter!

## Music Player

You should deploy linux on android before hand.

```bash
sudo apt install ffmpeg
```

Backup and rewrite /etc/ffserver.conf

```bash
/etc/ffserver.conf
```

```
HttpPort 8090
MaxHTTPConnections 2000
MaxClients 1000
MaxBandwidth 4096
CustomLog -
NoDaemon

<Feed feed1.ffm>
File /tmp/feed1.ffm
FileMaxSize 5M
</Feed>

# MP3 audio

<Stream test.mp3>
Feed feed1.ffm
AudioCodec libmp3lame
AudioBitRate 128
AudioChannels 2
AudioSampleRate 44100
NoVideo
StartSendOnKey
</Stream>
```

Feed Audio

```bash
ffmpeg -re -i test.mp3 http://localhost:8090/feed1.ffm
```

Play 

open in vlc: `http://127.0.0.1:8090/test.mp3`

## Internal Use Only

python
```python
import subprocess
p = subprocess.Popen(["ffmpeg", "-re", "-i", "test.mp3", "http://localhost:8090/feed1.ffm"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,universal_newlines=True)
p.kill()
```
