package com.example.bartek.praca_inzynierska;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;

import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioRecord;
import android.media.AudioTrack;
import android.media.MediaRecorder;
import android.util.Log;

public class PhoneCall
{
    private static final String LOG_TAG = "PhoneCall";
    private static final int SAMPLE_RATE = 44100; // Hertz
    private static final int SAMPLE_INTERVAL = 20; // Milliseconds
    private static final int BUFF_SIZE = 4096; //Bytes
    private InetAddress inetAddress; // Address to call
    private int port = 7000; // Port the packets are addressed to
    private volatile boolean microphoneActivated = false; // Enable microphoneActivated?
    private volatile boolean speakersActivated = false; // Enable speakersActivated?



    public PhoneCall(InetAddress inetAddress)
    {
        this.inetAddress = inetAddress;
    }

    public boolean isMicrophoneActivated()
    {
        return microphoneActivated;
    }

    public void deactivateMicrophone()
    {
        microphoneActivated = false;
    }
    public void deactivateSpeakers()
    {
        speakersActivated = false;
    }

    public void initializeMicrophone() {
        if (!microphoneActivated)
        {
            microphoneActivated = true;
            Thread thread = new Thread(new Runnable() {
                @Override
                public void run() {
                    // Create an instance of the AudioRecord class
                    Log.i(LOG_TAG, "Microphone thread started. Thread id: " + Thread.currentThread().getId());
                    AudioRecord audioRecorder = new AudioRecord(MediaRecorder.AudioSource.MIC, SAMPLE_RATE,
                            AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT,
                            AudioRecord.getMinBufferSize(SAMPLE_RATE, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT));
                    int bytes_read = 0;
                    int bytes_sent = 0;
                    byte[] buf = new byte[BUFF_SIZE];
                    try {
                        Log.i(LOG_TAG, "Packet destination: " + inetAddress.toString());
                        DatagramSocket socket = new DatagramSocket();
                        audioRecorder.startRecording();
                        while (microphoneActivated) {
                            bytes_read = audioRecorder.read(buf, 0, BUFF_SIZE);
                            DatagramPacket packet = new DatagramPacket(buf, bytes_read, inetAddress, port);
                            socket.send(packet);
                            bytes_sent += bytes_read;
                            Thread.sleep(SAMPLE_INTERVAL, 0);
                        }
                        audioRecorder.stop();
                        audioRecorder.release();
                        socket.disconnect();
                        socket.close();
                        Log.i(LOG_TAG, "Microphone thread ended.");
                        microphoneActivated = false;
                        return;
                    } catch (InterruptedException e) {

                        Log.e(LOG_TAG, "InterruptedException: " + e.toString());
                        microphoneActivated = false;
                    } catch (SocketException e) {

                        Log.e(LOG_TAG, "SocketException: " + e.toString());
                        microphoneActivated = false;
                    } catch (UnknownHostException e) {

                        Log.e(LOG_TAG, "UnknownHostException: " + e.toString());
                        microphoneActivated = false;
                    } catch (IOException e) {

                        Log.e(LOG_TAG, "IOException: " + e.toString());
                        microphoneActivated = false;
                    }
                }
            });
            thread.start();
        }
    }


    public void initializeSpeakers()
    {
        if(!speakersActivated)
        {

            speakersActivated = true;
            Thread thread = new Thread(new Runnable() {

                @Override
                public void run() {
                    Log.i(LOG_TAG, "Speakers thread started. Thread id: " + Thread.currentThread().getId());
                    AudioTrack audioTrack = new AudioTrack(AudioManager.STREAM_VOICE_CALL, SAMPLE_RATE,
                            AudioFormat.CHANNEL_OUT_MONO, AudioFormat.ENCODING_PCM_16BIT,
                            BUFF_SIZE, AudioTrack.MODE_STREAM);
                    audioTrack.play();
                    try {
                        DatagramSocket socket = new DatagramSocket(port);
                        byte[] buf = new byte[BUFF_SIZE];
                        while(speakersActivated)
                        {
                            DatagramPacket packet = new DatagramPacket(buf, BUFF_SIZE);
                            socket.receive(packet);
                            audioTrack.write(packet.getData(), 0, BUFF_SIZE);
                        }
                        socket.disconnect();
                        socket.close();
                        audioTrack.stop();
                        audioTrack.flush();
                        audioTrack.release();
                        Log.i(LOG_TAG, "Speakers thread ended.");
                        speakersActivated = false;
                        return;
                    }
                    catch(SocketException e) {

                        Log.e(LOG_TAG, "SocketException: " + e.toString());
                        speakersActivated = false;
                    }
                    catch(IOException e) {

                        Log.e(LOG_TAG, "IOException: " + e.toString());
                        speakersActivated = false;
                    }
                }
            });
            thread.start();
        }
    }
}
