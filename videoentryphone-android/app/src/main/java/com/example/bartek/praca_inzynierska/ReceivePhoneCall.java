package com.example.bartek.praca_inzynierska;


import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.Chronometer;

import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;

import javax.crypto.BadPaddingException;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;


public class ReceivePhoneCall extends AppCompatActivity implements View.OnClickListener
{
    private Button btnEndPhoneCall;
    private Button btnLetIn;
    private Button btnMuteMicrophone;
    private Chronometer chronometer;
    private InetAddress inetAddress;
    private PhoneCall phoneCall;

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_receive_phone_call);

        initiate();
        setButtonListeners();
        startCall();
        Log.i("ReceivePhoneCall", "after onCreate");
    }

    private void initiate()
    {
        btnEndPhoneCall = (Button) findViewById(R.id.btnEndPhoneCall);
        btnLetIn = (Button) findViewById(R.id.btnLetIn);
        btnMuteMicrophone = (Button) findViewById(R.id.btnMuteMicrophone);
        chronometer = (Chronometer) findViewById(R.id.simpleChronometer);

    }
    private void setButtonListeners()
    {
        btnLetIn.setOnClickListener(this);
        btnEndPhoneCall.setOnClickListener(this);
        btnMuteMicrophone.setOnClickListener(this);
    }

    private void startCall()
    {
        try
        {

            inetAddress = InetAddress.getByName(MainActivity.addressRPi);
            phoneCall = new PhoneCall(inetAddress);
            phoneCall.initializeMicrophone();
            phoneCall.initializeSpeakers();
            chronometer.start();
            Log.i("TCPSender: ", "OK");
            String messageToSend = encryptWithAES("OK");
            TCPSender tcpSender = new TCPSender();
            tcpSender.execute(messageToSend);
        }
        catch (UnknownHostException e)
        {
            e.printStackTrace();
        }
    }

    public void f()
    {
        chronometer.stop();
        phoneCall.deactivateSpeakers();
        phoneCall.deactivateMicrophone();
    }
    @Override
    public void onClick(View v)
    {

        if (v == btnLetIn)
        {
            String messageToSend = encryptWithAES("LETIN");

            Log.i("ReceivePhoneCall","btnLetIn - onClick");
            TCPSender tcpSender = new TCPSender();
            tcpSender.execute(messageToSend);
            f();
            finish();
            startActivity(new Intent(this, MainActivity.class));
        }
        else if (v == btnEndPhoneCall)
        {
            String messageToSend = encryptWithAES("BYE");

            Log.i("ReceivePhoneCall","btnEndPhoneCall - onClick");
            TCPSender tcpSender = new TCPSender();
            tcpSender.execute(messageToSend);
            f();
            finish();
            startActivity(new Intent(this, MainActivity.class));
        }
        else if (v == btnMuteMicrophone)
        {
            if (phoneCall.isMicrophoneActivated())
            {
                phoneCall.deactivateMicrophone();
                btnMuteMicrophone.setBackgroundResource(R.drawable.microphone_unmute);
            }
            else
            {
                phoneCall.initializeMicrophone();
                btnMuteMicrophone.setBackgroundResource(R.drawable.microphone_mute);
            }

        }
    }
    private String encryptWithAES(String message)
    {
        Crypt c = Crypt.getInstance();
        String messageToSend = null;
        try {
            messageToSend = c.encrypt_string(message);
        } catch (InvalidKeyException e) {
            e.printStackTrace();
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        } catch (NoSuchPaddingException e) {
            e.printStackTrace();
        } catch (InvalidAlgorithmParameterException e) {
            e.printStackTrace();
        } catch (IllegalBlockSizeException e) {
            e.printStackTrace();
        } catch (BadPaddingException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return messageToSend;
    }
}
