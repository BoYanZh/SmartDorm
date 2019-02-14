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
    private Button play_pauseBtn, selectBtn;
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
        selectBtn = (Button) findViewById(R.id.select);//选择按钮
    }

    private void bindButton() {
        /** 为按钮添加监听 ，四个按钮的监听器都是MainActivity*/
        play_pauseBtn.setOnClickListener(this);
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
                musicService.mediaPlayer.start();
                break;
            case R.id.select://点击选择
                new Thread(musicService.postMusicListTask).start();
                break;
        }
    }
}