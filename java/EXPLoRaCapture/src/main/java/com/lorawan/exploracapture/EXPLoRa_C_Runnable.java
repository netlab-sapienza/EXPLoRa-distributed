/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.lorawan.exploracapture;

import static com.lorawan.exploracapture.Main.splitIntWithPercentages;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Random;
import java.util.Stack;
import java.util.stream.IntStream;
import java.util.stream.Stream;

/**
 *
 * @author Utente
 */


//Note that this solution will take the already splitted array of nodes, in a real case, the gateway takes all the nodes and then filter the ones that it should process, discarding the others

public class EXPLoRa_C_Runnable implements Runnable{
    
    private int numberOfNodes;
    private Stream<Node> nodeStream;
    private volatile Node[] outputArray;

    public EXPLoRa_C_Runnable(Stream<Node> inputNodes, int workerNumberOfNodes) {
        this.nodeStream = inputNodes;
        this.numberOfNodes = workerNumberOfNodes;
    }
    
    public void run() {
  
        
        float[] waterfillingProbabilityDistributionOrthogonal = {47.02f, 25.85f, 14.36f, 7.18f, 3.59f, 2.02f};
        int[] maxDevicesForSpreadingfactor = splitIntWithPercentages(waterfillingProbabilityDistributionOrthogonal, numberOfNodes);
        //Initialize a stack full of spreading factors to assign
        Stack<Integer> spreadingFactorsStack = new Stack<Integer>();
        for(int i=numberOfNodes; i>=1; i-- ){
            if(i<=maxDevicesForSpreadingfactor[0]){
                spreadingFactorsStack.push(7);
            }else if(i<=maxDevicesForSpreadingfactor[0]+maxDevicesForSpreadingfactor[1]){
                spreadingFactorsStack.push(8);
            }else if(i<=maxDevicesForSpreadingfactor[0]+maxDevicesForSpreadingfactor[1]+maxDevicesForSpreadingfactor[2]){
                spreadingFactorsStack.push(9);
            }else if(i<=maxDevicesForSpreadingfactor[0]+maxDevicesForSpreadingfactor[1]+maxDevicesForSpreadingfactor[2]+maxDevicesForSpreadingfactor[3]){
                spreadingFactorsStack.push(10);
            }else if(i<=maxDevicesForSpreadingfactor[0]+maxDevicesForSpreadingfactor[1]+maxDevicesForSpreadingfactor[2]+maxDevicesForSpreadingfactor[3]+maxDevicesForSpreadingfactor[4]){
                spreadingFactorsStack.push(11);
            }else if(i<=maxDevicesForSpreadingfactor[0]+maxDevicesForSpreadingfactor[1]+maxDevicesForSpreadingfactor[2]+maxDevicesForSpreadingfactor[3]+maxDevicesForSpreadingfactor[4]+maxDevicesForSpreadingfactor[5]){
                spreadingFactorsStack.push(12);
            }
        }
        
        //Define the sensitivity array for the bandwidth of 125 kHz for each spreding factor
        double[] sensitivityThresholds = {-124.0, -127.0, -130.0, -133.0, -135.0, -137.0};
        //define the SIR Threshold in dB
        double SIRThreshold = 1;
        
        //This is a satck that contains the last node used to make the comparisons, is possible to sobstitute this with a simple variable because can be overvritten with just the last node
        //Note that for now at the end of the phase 2 the stack will contain only the last nde because it is not deleted (the nodes inserted at iteration i are deleted at iteration i+1)
        Stack<Node> stackLastNode = new Stack<Node>();
        Random r = new Random();
        //Create the array of spreading factors given as output to the python
        outputArray = nodeStream.map(node -> {

                                    Node currentNode = (Node) node;

                                    //Find the maximum RSSI
                                    Double maxRSSI= currentNode.getBsRSSI().stream()
                                                                            .max(new Comparator<Double>(){
                                                                                                            public int compare(Double o1, Double o2){
                                                                                                               return Double.compare(o1, o2);
                                                                                                            }
                                                                                                        })
                                                                            .orElse((Double.valueOf(-1)));

                                    //Find the basestation associated to the maximum RSSI
                                    int maxRSSIindex = IntStream.range(0, currentNode.getBsRSSI()
                                                                .size())
                                                                .filter(i -> maxRSSI.equals(currentNode.getBsRSSI().get(i)) )
                                                                .findFirst().orElse(-1);

                                    //Save the references and iniztialize the spreading factor to 0
                                    currentNode.setReferenceBaseStation(maxRSSIindex);
                                    currentNode.setReferenceBaseStationRSSI(maxRSSI);
                                    currentNode.setReferenceSpreadingFactor(0);



                                    return currentNode;

                                })
                    //Sort in decreasing order of the reference RSSI
                    .sorted(new Comparator<Node>(){
                                                        public int compare(Node o1, Node o2){
                                                            return Double.compare(o2.getReferenceBaseStationRSSI(), o1.getReferenceBaseStationRSSI());
                                                        }
                                                    })
                    //Phases one and two
                    .map(node -> {
                                    Node currentNode = (Node) node;
                                    //If is the first node skip
                                    if(stackLastNode.empty()){
                                        //Set the spreading factor of the first node
                                        currentNode.setReferenceSpreadingFactor(spreadingFactorsStack.pop());
                                        stackLastNode.push(currentNode);
                                    }else{
                                        //Phase 1
                                        if( (stackLastNode.peek().getReferenceBaseStationRSSI()-currentNode.getReferenceBaseStationRSSI()) > SIRThreshold || (stackLastNode.peek().getReferenceBaseStation()!=currentNode.getReferenceBaseStation())){
                                            //Check if the current spreading factor is big enough to reach the reference base station
                                            if(currentNode.getReferenceBaseStationRSSI() >= sensitivityThresholds[spreadingFactorsStack.peek()-7]){
                                                currentNode.setReferenceSpreadingFactor(spreadingFactorsStack.pop());
                                            }else{
                                                //Pop from the stack until we can take the spreading factor big enough
                                                int stackIndex = 0;
                                                while(currentNode.getReferenceBaseStationRSSI() < sensitivityThresholds[spreadingFactorsStack.get(stackIndex)-7]){
                                                    stackIndex++;
                                                    if(stackIndex == spreadingFactorsStack.size()-1){
                                                        System.out.println("WARNING!! The waterfilling distribution cannot be respected because the nodes have to low RSSI and there are not enough big spreading factors");
                                                        break;
                                                    }
                                                }
                                                currentNode.setReferenceSpreadingFactor(spreadingFactorsStack.get(stackIndex));
                                                spreadingFactorsStack.remove(stackIndex);
                                            }
                                        }
                                        //Phase 2
                                        else{
                                            //Check if the nodes see different basestations, if yes you enter in the phase 2, otherwise skip this node
                                            int differentBAsestation = currentNode.haveDifferentBaseStations(stackLastNode.peek(), sensitivityThresholds[5]);
                                            if( differentBAsestation != -1 ){
                                                System.out.println("In the if for different basestations");
                                                //If the nodes see different basestations set the new reference basestation and the associated RSSI for the current node
                                                currentNode.setReferenceBaseStation(differentBAsestation);
                                                currentNode.setReferenceBaseStationRSSI(currentNode.getBsRSSI().get(currentNode.getBaseStations().indexOf(differentBAsestation)));

                                                //Check if the current spreding factor is enough to reach the new reference basestation, if yes assign the current spreding factor
                                                if(currentNode.getReferenceBaseStationRSSI()>= sensitivityThresholds[spreadingFactorsStack.peek()-7]){
                                                    currentNode.setReferenceSpreadingFactor(spreadingFactorsStack.pop());
                                                }
                                                //If the current spreading factor is not enough to reach the new reference base station, assign the minimum spreading factor able to reach the new basestation
                                                else{
                                                    //Find the correct spreading factor to assign
                                                    for(int j=0; j<sensitivityThresholds.length; j++){
                                                        if(currentNode.getReferenceBaseStationRSSI() >= sensitivityThresholds[j]){
                                                            //Check if the good spreading factor is available, otherwise go to the next one
                                                            if(spreadingFactorsStack.contains(j+7)){
                                                                //Set the found reference spreading factor to the node and remove the sf occurence from the stack
                                                                currentNode.setReferenceSpreadingFactor(j+7);
                                                                spreadingFactorsStack.removeElement(j+7);
                                                            }
                                                        }
                                                        if(j == (sensitivityThresholds.length-1) && currentNode.getReferenceSpreadingFactor()==0){
                                                            System.out.println("WARNING SPREADING FACTOR NOT ASSIGNED BECASUE NOT AVAILABLE, IS NEEDED TO OVERCOME THE DISTRIBUTION (EX. NODE NEED SF 12, DISTRIBUTION HAS 1 SF 12 TO ASSIGN, SF 12 ALREADY ASSIGNED)");
                                                            //Assign the minmum spreading factor needed to reach the Gateway without taking into account the distribution and all the EXPLoRa-C considerations PART DONE BY MYSELF, NO RULES IN THE PAPER
                                                            for(int k=0; k<sensitivityThresholds.length; k++){
                                                                if(currentNode.getReferenceBaseStationRSSI() >= sensitivityThresholds[k]){
                                                                    currentNode.setReferenceSpreadingFactor(k+7);
                                                                    break;
                                                                }
                                                            }
                                                        }
                                                        //If this happen insert a code that assign the first SF that satisfy the RSSI without taking into account the distribution
                                                    }
                                                }

                                            }
                                        }
                                        //Until now i have used only the peek(), so now i remove the the last node from the stack
                                        stackLastNode.pop();
                                        //In any case put in the stack the last note visited to be compared with the next one
                                        stackLastNode.push(currentNode);
                                    }

                                    return currentNode;
                                })
                    //Sort to order in base of the nodeID and more important, to avoid the vertically execution of these maps, becasue they will create a bug on the shared remaining spreading fator Stack, this can be done by the sort becasue it is a stream statefull operation
                    .sorted(new Comparator<Node>(){
                                                        public int compare(Node o1, Node o2){
                                                            return Integer.compare(o1.getNodeId(), o2.getNodeId());
                                                        }
                                                    })
                    //Phases 3
                    .map(node ->{
                                    Node currentNode = (Node) node;
                                    if(currentNode.getReferenceSpreadingFactor()==0){
                                        //Check if there is one remaining spreading factor big enough to be randomli assigned
                                        ArrayList<Integer> availableSFsForThisNode = new ArrayList<Integer>();
                                        for(int j=0; j<sensitivityThresholds.length; j++){
                                            if(currentNode.getReferenceBaseStationRSSI() >= sensitivityThresholds[j]){
                                                if(spreadingFactorsStack.contains(j+7)){
                                                    //Fill an array with the spreading factors good for this node and availables
                                                    availableSFsForThisNode.add(j+7);
                                                }
                                            }
                                        }
                                        //Check if at least one spreading facot is available
                                        if(!availableSFsForThisNode.isEmpty()){
                                            int randomSF = availableSFsForThisNode.get(r.nextInt(availableSFsForThisNode.size()));
                                            currentNode.setReferenceSpreadingFactor(randomSF);
                                            spreadingFactorsStack.removeElement(randomSF);
                                        }
                                        else{
                                            System.out.println("WARNING SPREADING FACTOR NOT ASSIGNED BECASUE NOT AVAILABLE, IS NEEDED TO OVERCOME THE DISTRIBUTION (EX. NODE NEED SF 12, DISTRIBUTION HAS 1 SF 12 TO ASSIGN, SF 12 ALREADY ASSIGNED)");
                                            //Assign the minmum spreading factor needed to reach the Gateway without taking into account the distribution and all the EXPLoRa-C considerations PART DONE BY MYSELF, NO RULES IN THE PAPER
                                            for(int k=0; k<sensitivityThresholds.length; k++){
                                                if(currentNode.getReferenceBaseStationRSSI() >= sensitivityThresholds[k]){
                                                    currentNode.setReferenceSpreadingFactor(k+7);
                                                    break;
                                                }
                                            }
                                            //If this happen insert a code that assign the first SF that satisfy the RSSI without taking into account the distribution
                                        }
                                    }
                                    //Last step is to transform the whole stream of node into a stream of spreading factors to give as output to the python
                                    return currentNode;
                                    //return (int)currentNode.getNodeId();
                                }
                        )
                        .toArray(Node[]::new);
                        //.forEach(node -> System.out.println(((Node)node).toString()));
                        //.forEach(sf -> System.out.println(Integer.toString((int)sf)));
     
    }

    public Node[] getOutputArray() {
        return outputArray;
    }

    
    
}
