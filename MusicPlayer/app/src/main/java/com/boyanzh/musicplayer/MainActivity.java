package com.boyanzh.musicplayer;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.content.ServiceConnection;
import android.os.IBinder;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;

public class MainActivity extends Activity implements OnClickListener{
    private Button play_pauseBtn, stopBtn, quitBtn, selectBtn;
    private MusicService musicService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);//绑定布局
        findView();//findIdByView，找到个个控件
        bindButton();//按钮绑定监听器。
        musicService = new MusicService();//新建一个MusicService后台服务
        Intent intent = new Intent(this, MusicService.class);
        bindService(intent, sc, BIND_AUTO_CREATE);//绑定服务
        new Thread(musicService.postMusicListTask).start();
    }

    private void findView() {
        /** 通过id获得各种组件 */
        play_pauseBtn = (Button) findViewById(R.id.play_pause);//开始/暂停按钮
        stopBtn = (Button) findViewById(R.id.stop);//停止按钮
        quitBtn = (Button) findViewById(R.id.quit);//退出按钮
        selectBtn = (Button) findViewById(R.id.select);//选择按钮
    }

    private void bindButton() {
        /** 为按钮添加监听 ，四个按钮的监听器都是MainActivity*/
        play_pauseBtn.setOnClickListener(this);
        stopBtn.setOnClickListener(this);
        quitBtn.setOnClickListener(this);
        selectBtn.setOnClickListener(this);
    }

    private ServiceConnection sc = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            musicService = ((MusicService.MyBinder) service).getService();
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {
            musicService = null;
        }
    };

    @Override
    public void onClick(View v) {
        switch (v.getId()) {
            case R.id.play_pause://点击play_pause按钮事件
                musicService.playORpuase();//调用musicService中的playORpause函数，暂停或开始音乐播放
                if (musicService.mediaPlayer.isPlaying()) {
                    play_pauseBtn.setText("PAUSE");//设置button的内容为Pause
                } else {
                    play_pauseBtn.setText("PLAY");//button内容为Play
                }
                break;
            case R.id.stop://点击暂停
                musicService.stop();//关闭音乐
                play_pauseBtn.setText("PLAY");//设置开始和暂停按钮的内容为Play
                break;
            case R.id.quit://点击退出
                unbindService(sc);//解除后台服务的绑定
                try {
                    MainActivity.this.finish();//结束当前的时间
                    System.exit(0);
                } catch (Exception e) {
                    e.printStackTrace();
                }
                break;
            case R.id.select://点击选择
                new Thread(musicService.postMusicListTask).start();
                new Thread(musicService.getNextMusicTask).start();
                break;
        }
    }
}