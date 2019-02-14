package com.boyanzh.musicplayer;

import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.media.MediaPlayer;
import android.media.AudioManager;
import android.os.Binder;
import android.os.Handler;
import android.os.IBinder;
import android.util.Log;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;

public class MusicService extends Service {
    public String IP = "http://192.168.1.9:5001";
    public String filePath = "/storage/emulated/0/netease/cloudmusic/Music/";
//    public AudioManager audioManager = (AudioManager) getSystemService(this.AUDIO_SERVICE);
    public MediaPlayer mediaPlayer = new MediaPlayer();
    private final IBinder binder = new MyBinder();
    private Timer timer = new Timer();

    public class MyBinder extends Binder {
        MusicService getService() {
            return MusicService.this;//找到后台服务的指针，返回后台服务实例
        }
    }

    public MusicService() {
        mediaPlayer.setOnCompletionListener(new MediaPlayer.OnCompletionListener() {
            @Override
            public void onCompletion(MediaPlayer mp) {
                new Thread(postMusicListTask).start();
                new Thread(getNextMusicTask).start();
            }
        });
        mediaPlayer.setOnErrorListener(new MediaPlayer.OnErrorListener() {
            @Override
            public boolean onError(MediaPlayer mp, int what, int extra) {
                return true;
            }
        });
    }

    Runnable getNextMusicTask = new Runnable() {
        @Override
        public void run() {
            filePath += getHttp(IP + "/music/api?action=get").replace("\n", "");
            loadMusic(filePath);
            playORpuase();
        }
    };

    Runnable postMusicListTask = new Runnable() {
        @Override
        public void run() {
            List fileList = getFileName(filePath);
            loadMusic(filePath + fileList.get(0).toString());
            String strData = "";
            for (int i = 0; i < fileList.size(); i++) {
                strData += fileList.get(i) + "\n";
            }
            postHttp(IP + "/music/json", strData);
        }
    };

    public String getHttp(String url) {
        HttpURLConnection connection;
        String response = null;
        try {
            URL myUrl = new URL(url);
            connection = (HttpURLConnection) myUrl.openConnection();
            connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
            connection.setRequestMethod("GET");
            String line = "";
            InputStreamReader isr = new InputStreamReader(connection.getInputStream());
            BufferedReader reader = new BufferedReader(isr);
            StringBuilder sb = new StringBuilder();
            while ((line = reader.readLine()) != null) {
                sb.append(line + "\n");
            }
            response = sb.toString();
            isr.close();
            reader.close();
        } catch (IOException e) {
            // Error
            e.printStackTrace();
        }
        return response;
    }

    public String postHttp(String url, String data) {
        HttpURLConnection connection;
        OutputStreamWriter request = null;
        String response = null;
        try {
            URL myUrl = new URL(url);
            connection = (HttpURLConnection) myUrl.openConnection();
            connection.setDoOutput(true);
            connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
            connection.setRequestMethod("POST");
            request = new OutputStreamWriter(connection.getOutputStream());
            request.write(data);
            request.flush();
            request.close();
            String line = "";
            InputStreamReader isr = new InputStreamReader(connection.getInputStream());
            BufferedReader reader = new BufferedReader(isr);
            StringBuilder sb = new StringBuilder();
            while ((line = reader.readLine()) != null) {
                sb.append(line + "\n");
            }
            response = sb.toString();
            Log.e("ee", "Message from Server: \n" + response);
            isr.close();
            reader.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return response;
    }

    public static List<String> getFileName(String fileAbsolutePath) {
        List<String> fileList = new ArrayList<>();
        File file = new File(fileAbsolutePath);
        File[] subFile = file.listFiles();
        for (int iFileLength = 0; iFileLength < subFile.length; iFileLength++) {
            // 判断是否为文件夹
            if (!subFile[iFileLength].isDirectory()) {
                String filename = subFile[iFileLength].getName();
                fileList.add(subFile[iFileLength].getName());
                Log.e("eee", "文件名 ： " + filename);
            }
        }
        return fileList;
    }

    @Override
    public IBinder onBind(Intent intent) {
        // TODO: Return the communication channel to the service.
        //throw new UnsupportedOperationException("Not yet implemented");
        return binder;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        TimerTask timerTask = new TimerTask() {
            @Override
            public void run() {
                String command = getHttp(IP + "/music/api?action=command").replace("\n","");
                switch (command) {
                    case "pause":
                        mediaPlayer.pause();//暂停
                        break;
                    case "start":
                        mediaPlayer.start();//开始
                        break;
//                    case "vup":
//                        audioManager.adjustStreamVolume(AudioManager.STREAM_MUSIC, AudioManager.ADJUST_RAISE, AudioManager.FLAG_SHOW_UI);
//                        break;
//                    case "vdown":
//                        audioManager.adjustStreamVolume(AudioManager.STREAM_MUSIC, AudioManager.ADJUST_LOWER, AudioManager.FLAG_SHOW_UI);
//                        break;
                }
            }
        };
        timer.schedule(timerTask,
                1000,//延迟1秒执行
                1000);//周期时间
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (mediaPlayer != null) {
            mediaPlayer.stop();//停止歌曲播放
            mediaPlayer.release();//释放mediaPlayer资源
        }
    }

    public void playORpuase() {
        if (mediaPlayer.isPlaying()) {
            mediaPlayer.pause();//暂停
        } else {
            mediaPlayer.start();//开始
        }
    }

    public void stop() {
        if (mediaPlayer != null) {
            mediaPlayer.stop();//停止
            try {
                mediaPlayer.prepare();//就绪
                mediaPlayer.seekTo(0);//设置歌曲回到最开始
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    public void loadMusic(String path) {
        try {
            mediaPlayer.reset();
            mediaPlayer.setDataSource(path);
            mediaPlayer.prepare();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

