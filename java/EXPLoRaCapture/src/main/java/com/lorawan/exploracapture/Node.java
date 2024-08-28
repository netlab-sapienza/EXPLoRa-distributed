/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.lorawan.exploracapture;

import java.io.Serializable;
import java.util.ArrayList;

/**
 *
 * @author Utente
 */
public class Node implements Serializable{
    
    private int nodeId;
    private double coordinateX;
    private double coordinateY;
    private ArrayList<Integer> baseStations;
    private ArrayList<Double> bsRSSI;
    private ArrayList<Integer> bsSF;
    private int referenceBaseStation;
    private Double referenceBaseStationRSSI;
    private int referenceSpreadingFactor;

    
    public Node() {
        this.baseStations = new ArrayList<Integer>();
        this.bsRSSI = new ArrayList<Double>();
        this.bsSF = new ArrayList<Integer>();
    }

    public Node(int nodeId, double coordinateX, double coordinateY) {
        this.nodeId = nodeId;
        this.coordinateX = coordinateX;
        this.coordinateY = coordinateY;
        this.baseStations = new ArrayList<Integer>();
        this.bsRSSI = new ArrayList<Double>();
        this.bsSF = new ArrayList<Integer>();
    }

    //ID
    public int getNodeId() {
        return nodeId;
    }

    public void setNodeId(int nodeId) {
        this.nodeId = nodeId;
    }
    
    //X
    public double getCoordinateX() {
        return coordinateX;
    }

    public void setCoordinateX(double coordinateX) {
        this.coordinateX = coordinateX;
    }

    //Y
    public double getCoordinateY() {
        return coordinateY;
    }

    public void setCoordinateY(double coordinateY) {
        this.coordinateY = coordinateY;
    }

    //Base stations
    public void addBaseStation(int baseStations) {
        this.baseStations.add(baseStations);
    }
    
    public ArrayList<Integer> getBaseStations() {
        return baseStations;
    }

    public void setBaseStations(ArrayList<Integer> baseStations) {
        this.baseStations = baseStations;
    }

    //Base stations RSSI
    public void addBsRSSI(double bsRSSI) {
        this.bsRSSI.add(bsRSSI);
    }
    
    public ArrayList<Double> getBsRSSI() {
        return bsRSSI;
    }
    
    public void setBsRSSI(ArrayList<Double> bsRSSI) {
        this.bsRSSI = bsRSSI;
    }

    //Base stations spreading factor
    public void addBsSF(int bsSF) {
        this.bsSF.add(bsSF);
    }
    
    public ArrayList<Integer> getBsSF() {
        return bsSF;
    }

    public void setBsSF(ArrayList<Integer> bsSF) {
        this.bsSF = bsSF;
    }
    
    //Reference base station
    public int getReferenceBaseStation() {
        return referenceBaseStation;
    }

    public void setReferenceBaseStation(int referenceBaseStation) {
        this.referenceBaseStation = referenceBaseStation;
    }

    //Reference RSSI
    public Double getReferenceBaseStationRSSI() {
        return referenceBaseStationRSSI;
    }

    public void setReferenceBaseStationRSSI(Double referenceBaseStationRSSI) {
        this.referenceBaseStationRSSI = referenceBaseStationRSSI;
    }

    //Reference spreading factor
    public int getReferenceSpreadingFactor() {
        return referenceSpreadingFactor;
    }

    public void setReferenceSpreadingFactor(int referenceSpreadingFactor) {
        this.referenceSpreadingFactor = referenceSpreadingFactor;
    }

    @Override
    public Node clone(){
        Node bufferNode = new Node();
        bufferNode.setNodeId(this.nodeId);
        bufferNode.setCoordinateX(this.coordinateX);
        bufferNode.setCoordinateY(this.coordinateY);
        ArrayList<Integer> bufferBaseStations = new ArrayList<>();
        for (int item : this.baseStations) bufferBaseStations.add(item);
        bufferNode.setBaseStations(bufferBaseStations);
        ArrayList<Double> bufferBsRSSI = new ArrayList<>();
        for (double item : this.bsRSSI) bufferBsRSSI.add(item);
        bufferNode.setBsRSSI(bufferBsRSSI);
        ArrayList<Integer> bufferBsSF = new ArrayList<>();
        for (int item : this.bsSF) bufferBsSF.add(item);
        bufferNode.setBsSF(bufferBsSF);
        bufferNode.setReferenceBaseStation(this.referenceBaseStation);
        bufferNode.setReferenceBaseStationRSSI(this.referenceBaseStationRSSI);
        bufferNode.setReferenceSpreadingFactor(this.referenceSpreadingFactor);
        return bufferNode;
    }

    @Override
    public boolean equals(Object obj) {
        
        if (obj == this) {
            return true;
        }
        
        if (!(obj instanceof Node)) {
            return false;
        }
        
        Node bufferNode = (Node)obj;
        boolean flag = true;
        if(!(nodeId == bufferNode.getNodeId())){
            flag = false;
        }else if(!(coordinateX == bufferNode.getCoordinateX())){
            flag = false;
        }else if(!(coordinateY == bufferNode.getCoordinateY())){
            flag = false;
        }else if(!(referenceBaseStation == bufferNode.getReferenceBaseStation())){
            flag = false;
        }else if(!(referenceSpreadingFactor == bufferNode.getReferenceSpreadingFactor())){
            flag = false;
        }else if(!(referenceBaseStationRSSI==null && bufferNode.getReferenceBaseStationRSSI()==null) && !(Double.compare(referenceBaseStationRSSI, bufferNode.getReferenceBaseStationRSSI()) == 0)){
            flag = false;
        }else{
            //This will check bot the element in the lists and also theyr position in the lists, so if ordered differently will return false
            for(int i=0; i<baseStations.size(); i++){
                if(!(baseStations.get(i)==bufferNode.getBaseStations().get(i))){
                    flag = false;
                }else if(!(bsSF.get(i)==bufferNode.getBsSF().get(i))){
                    flag = false;
                }else if(!(Double.compare(bsRSSI.get(i), bufferNode.getBsRSSI().get(i)) == 0)){
                    flag = false;
                }
            }
        }
        
        return flag;
    }

    
    
    @Override
    public String toString() {
        return "Node{" + "nodeId=" + nodeId + ", coordinateX=" + coordinateX + ", coordinateY=" + coordinateY + ", baseStations=" + baseStations + ", bsRSSI=" + bsRSSI + ", bsSF=" + bsSF + ", referenceBaseStation=" + referenceBaseStation + ", referenceBaseStationRSSI=" + referenceBaseStationRSSI + ", referenceSpreadingFactor=" + referenceSpreadingFactor + '}';
    }

    //This function comapre the basestation of this object with the basestations of a different node, return -1 if the nodes have the same basestations
    public int haveDifferentBaseStations(Node comparedNode, double minSensitivity){
        for(int i=0; i<this.baseStations.size(); i++){
            //If check if the compared node have this basestation, if not there is one basestation that differ and it is returned, otherwise continue
            if(!(comparedNode.getBaseStations().contains(this.baseStations.get(i))) && (this.bsRSSI.get(i) >= minSensitivity)){
                return this.baseStations.get(i);
            }
        }
        return -1;
    }
    
}
