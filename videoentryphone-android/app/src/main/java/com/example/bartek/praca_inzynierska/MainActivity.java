package com.example.bartek.praca_inzynierska;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Build;
import android.os.Bundle;
import android.support.v4.content.LocalBroadcastManager;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import java.util.Random;


public class MainActivity extends AppCompatActivity implements View.OnClickListener
{
    public static Context context;
    public static String addressRPi;
    private Button btnMinimalize;
    private Button btnExit;
    private Button btnConnect;
    private EditText editText_addressRPi;
    private TextView tv2;
    private ImageView imgOk;
    private int sharedPrime = 23;
    private int sharedBase = 5;
    private int androidSecret = 7;
    private boolean message_showed = false;
    BroadcastReceiver mReceiver = new BroadcastReceiver()
    {
        @Override
        public void onReceive(Context context, Intent intent)
        {
            String text = intent.getStringExtra("theMessage");
            Log.i("mMain", text);
            if (text.equals("CALL"))
            {
                startActivity(new Intent(context, WebViewer.class));
            }
            else if (text.substring(0,2).equals("DH"))
            {
                negotiateDHkey(text);
            }
        }
    };
    private void negotiateDHkey(String text)
    {

        double B = (Math.pow(sharedBase, androidSecret)) % sharedPrime;
        TCPSender tcpSender = new TCPSender();
        tcpSender.execute("DH;"+Integer.toString((int)B));
        Log.i("DH","wysylam moj kluczyk");
        int RPiPublicKey = Integer.parseInt(text.substring(3));
        double sharedSecret = (Math.pow(RPiPublicKey, androidSecret)) % sharedPrime;
        Log.i("DH","dostalem i sekret to:" + String.valueOf(sharedSecret));
        int value = (int) sharedSecret;
        // tutaj tworze szyfr z kluczem
        Crypt c = Crypt.getInstance();
        c.setSharedKey(String.valueOf(value));

        if (message_showed == false)
        {
            Toast.makeText(MainActivity.this, "Połączono z "+editText_addressRPi.getText().toString(), Toast.LENGTH_SHORT).show();
            message_showed = true;
            imgOk.setVisibility(View.VISIBLE);
            btnConnect.setVisibility(View.INVISIBLE);
            btnMinimalize.setVisibility(View.VISIBLE);
            tv2.setVisibility(View.VISIBLE);
            editText_addressRPi.setFocusable(false);
        }



    }

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Random generator = new Random();
        androidSecret = generator.nextInt(20 + 1 - 1) + 1;
        initializeButtons();
        editText_addressRPi.setText("192.168.1.17");
        imgOk.setVisibility(View.INVISIBLE);
        btnMinimalize.setVisibility(View.INVISIBLE);
        tv2.setVisibility(View.INVISIBLE);



    }
    private void initializeButtons()
    {
        btnMinimalize = (Button) findViewById(R.id.btnMinimalize);
        btnExit = (Button) findViewById(R.id.btnExit);
        btnConnect = (Button) findViewById(R.id.btnConnect);
        imgOk = (ImageView) findViewById(R.id.imgOk);
        btnMinimalize.setOnClickListener(this);
        btnExit.setOnClickListener(this);
        btnConnect.setOnClickListener(this);
        editText_addressRPi = (EditText) findViewById(R.id.addressRPi);

        tv2 = (TextView) findViewById(R.id.tv2);
    }
    private void startTCPReceiver()
    {
        TCPReceiver tcpReceiver = new TCPReceiver();
        tcpReceiver.initializeTCPReceiver();
        LocalBroadcastManager.getInstance(this).registerReceiver(mReceiver, new IntentFilter("incomingMessage"));
    }
    private void sendNotificationToRPi()
    {
        TCPSender tcpSender = new TCPSender();
        tcpSender.execute("HI");
    }
    private void connectToRPi()
    {
        addressRPi = editText_addressRPi.getText().toString();
        context = getApplicationContext();
        startTCPReceiver();
        Log.i("MainActivity", "pierwsze odpalenie programu");
        sendNotificationToRPi();

    }
    private void closeKeyboard()
    {
        View view = this.getCurrentFocus();
        if (view != null)
        {
            InputMethodManager imm = (InputMethodManager)getSystemService(Context.INPUT_METHOD_SERVICE);
            imm.hideSoftInputFromWindow(view.getWindowToken(),0);
        }
    }

    @Override
    public void onClick(View v)
    {
        if (v == btnMinimalize)
        {
            MainActivity.this.moveTaskToBack(true);
        }
        else if (v == btnExit)
        {

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP)
            {
                finishAndRemoveTask();
            }
            else
            {
                this.finishAffinity();
            }
        }
        else if (v == btnConnect)
        {
            closeKeyboard();
            message_showed = false;
            connectToRPi();
        }
    }
}
