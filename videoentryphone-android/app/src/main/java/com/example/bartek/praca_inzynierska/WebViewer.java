package com.example.bartek.praca_inzynierska;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.media.MediaPlayer;
import android.support.v4.content.LocalBroadcastManager;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;


public class WebViewer extends AppCompatActivity implements View.OnClickListener
{
    private WebView webView;
    private Button btnAnswer;
    private Button btnReject;
    public static MediaPlayer mediaPlayer;


    BroadcastReceiver mReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String text = intent.getStringExtra("theMessage");
            Log.i("mMain", text);
            if (text.equals("CANCEL"))
            {
                if (mediaPlayer != null)
                {
                    try{
                        mediaPlayer.stop();
                        mediaPlayer.release();
                    }
                    catch (Exception e)
                    {
                        Log.d("WebViewer Activity", e.toString());
                    }

                }

                webView.loadUrl("about:blank");
                finish();
                startActivity(new Intent(context, MainActivity.class));

            }
        }


    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_web_viewer);

            instantiate();
            linkWebView();
            setButtonListeners();
            startRingingSound();
            LocalBroadcastManager.getInstance(this).registerReceiver(mReceiver, new IntentFilter("incomingMessage"));
    }
    private void startRingingSound()
    {
        mediaPlayer = MediaPlayer.create(WebViewer.this, R.raw.rush);
        mediaPlayer.setLooping(true);
        mediaPlayer.start();

    }
    private void instantiate()
    {
        webView = (WebView) findViewById(R.id.webView);
        btnAnswer = (Button) findViewById(R.id.btnAnswer);
        btnReject = (Button) findViewById(R.id.btnReject);

        webView.getSettings().setLoadWithOverviewMode(true);
        webView.getSettings().setUseWideViewPort(true);
    }
    private void linkWebView()
    {
        webView.setWebViewClient(new WebViewClient());
        String link = "http://" + MainActivity.addressRPi + ":8000/stream.mjpg";
        webView.loadUrl(link);
    }
    private void setButtonListeners()
    {
        btnReject.setOnClickListener(this);
        btnAnswer.setOnClickListener(this);
    }




    @Override
    public void onClick(View v)
    {
        mediaPlayer.stop();
        mediaPlayer.release();
        if (v == btnAnswer)
        {
            webView.loadUrl("about:blank");
            finish();
            startActivity(new Intent(this, ReceivePhoneCall.class));
        }
        else if (v == btnReject)
        {
            webView.loadUrl("about:blank");
            finish();
            startActivity(new Intent(this, MainActivity.class));
        }
    }
}
