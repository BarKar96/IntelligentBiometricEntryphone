package com.example.bartek.praca_inzynierska;

import android.os.AsyncTask;
import android.util.Log;

import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;

public class TCPSender extends AsyncTask<String, Void, Void>
{
    @Override
    protected Void doInBackground(String... strings)
    {
        try
        {
            Socket socket = new Socket(MainActivity.addressRPi, 9000);
            PrintWriter printWriter = new PrintWriter(new OutputStreamWriter(socket.getOutputStream()));
            printWriter.print(strings[0]);
            Log.i("TCPSender", strings[0]);
            printWriter.flush();
            socket.close();

        } catch (UnknownHostException e)
        {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return null;
    }
}
