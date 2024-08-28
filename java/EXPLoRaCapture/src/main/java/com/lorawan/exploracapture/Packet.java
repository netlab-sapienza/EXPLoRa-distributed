/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.lorawan.exploracapture;

import java.io.Serializable;
import java.util.Random;

/**
 *
 * @author Utente
 */
public class Packet implements Serializable{
    
    private String deviceId;
    private String gatewayId;
    private float RSSI;
    private int spreadingFactor;

    public Packet() {
    }
    
    public Packet(String deviceId, String gatewayId, float RSSI) {
        this.deviceId = deviceId;
        this.gatewayId = gatewayId;
        this.RSSI = RSSI;
    }

    public String getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(String deviceId) {
        this.deviceId = deviceId;
    }

    public String getGatewayId() {
        return gatewayId;
    }

    public int getSpreadingFactor() {
        return spreadingFactor;
    }

    public void setGatewayId(String gatewayId) {
        this.gatewayId = gatewayId;
    }

    public float getRSSI() {
        return RSSI;
    }

    public void setRSSI(float RSSI) {
        this.RSSI = RSSI;
    }

    public void setSpreadingFactor(int spreadingFactor) {
        this.spreadingFactor = spreadingFactor;
    }

    @Override
    public String toString() {
        return "Packet{" + "deviceId=" + deviceId + ", gatewayId=" + gatewayId + ", RSSI=" + RSSI + ", spreadingFactor=" + spreadingFactor + '}';
    }
    
    public static Packet generateRandomPacket(int devicesNumber, int gatewaysNumber, int RSSImin, int RSSImax){
        Random r = new Random();
        //int randomDeviceId = (int)Math.floor(Math.random()*(devicesNumber-0+1)+0);
        int randomDeviceId = r.nextInt(devicesNumber);
        //int randomGatewayId = (int)Math.floor(Math.random()*(gatewaysNumber-0+1)+0);
        int randomGatewayId = r.nextInt(gatewaysNumber);
        //float randomRSSI = (float)Math.floor(Math.random()*(RSSImax-RSSImin+1)+RSSImin);
        float randomRSSI = (float)((r.nextInt((int)((RSSImax-RSSImin)*10+1))+RSSImin*10) / 10.0);
        
        Packet packet = new Packet(Integer.toString(randomDeviceId), Integer.toString(randomGatewayId), randomRSSI);
        
        return packet;
    }
    
    public static Packet[] generateOneRandomPacketForEachDevice(int devicesNumber, int gatewaysNumber, int RSSImin, int RSSImax){
        Random r = new Random();
        Packet[] arrayOfRandomPackets= new Packet[devicesNumber];
                
        for (int i = 0; i < devicesNumber; i++) {
            int randomGatewayId = r.nextInt(gatewaysNumber);
            float randomRSSI = (float)((r.nextInt((int)((RSSImax-RSSImin)*10+1))+RSSImin*10) / 10.0);
            arrayOfRandomPackets[i] = new Packet(Integer.toString(i), Integer.toString(randomGatewayId), randomRSSI);
        }
        
        return arrayOfRandomPackets;
    }
    
    
}
