package com.example.bartek.praca_inzynierska;



import android.content.Intent;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.support.v4.content.LocalBroadcastManager;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;
import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;

import javax.crypto.BadPaddingException;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;


public class TCPReceiver extends AppCompatActivity
{
    ServerSocket serverSocket;
    Socket socket;
    public String message;
    private MainActivity mainActivity;

    public void initializeTCPReceiver()
    {
        mainActivity = new MainActivity();
        Thread thread = new Thread(new Runnable()
        {

            @Override
            public void run()
            {
                Handler mHandler = new Handler(Looper.getMainLooper()) {
                    @Override
                    public void handleMessage(Message message) {

                    }
                };
                try
                {
                    serverSocket = new ServerSocket(9000);
                    while (true)
                    {
                        socket = serverSocket.accept();
                        BufferedReader inStream = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                        message = inStream.readLine();
                        Log.i("TCPReceiver", message);

                        if (!message.substring(0,2).equals("DH"))
                        {
                           message = decryptStringWithAES(message);
                            Log.i("TCPReceiver decrypted:", message);
                        }


                        Intent incomingMessageIntent = new Intent("incomingMessage");
                        incomingMessageIntent.putExtra("theMessage", message);
                        LocalBroadcastManager.getInstance(MainActivity.context).sendBroadcast(incomingMessageIntent);


                    }
                } catch (IOException e)
                {
                    e.printStackTrace();
                }

            }



        });
        thread.start();
    }

    private String decryptStringWithAES(String message)
    {
        Crypt c = Crypt.getInstance();
        String messageToDecrypt = null;
        try {
           messageToDecrypt = c.decrypt_string(message);
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
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return messageToDecrypt;
    }


}


