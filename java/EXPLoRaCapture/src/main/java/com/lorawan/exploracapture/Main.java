/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.lorawan.exploracapture;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.Random;
import java.util.Scanner;
import java.util.Stack;
import java.util.concurrent.TimeUnit;
import java.util.stream.*;
import org.apache.commons.lang3.ArrayUtils;


/**
 *
 * @author Utente
 */
public class Main {
    
    
    public static long currentExecutionTime;
    
    
    public Main(){
        
    }

    public static void main(String[] args) throws FileNotFoundException, InterruptedException {

        System.out.println("Multithread EXPLoRa_C algorithm execution started!");
        System.out.println("Available processors: " + Runtime.getRuntime().availableProcessors()+"\n\n");

        String inputFile = "/home/gabriele/Desktop/EXPLoRa-CD/python/simulation_files/100000-nodes-raw.txt";

        int numberOfThreads = 4;
        int repeatExecution = 10;
        int numberOfNodes = 100000;

        long avg = 0;
        double avgSeconds;

        System.out.println("Executing with "+numberOfThreads+" threads and "+numberOfNodes+" nodes...");

        ArrayList<Integer> selectedBasestationsID = selectBaseStationsID(numberOfThreads);
        ArrayList<ArrayList<Node>> splittedLists = getNodesFromFileMultithread(inputFile,selectedBasestationsID);

        for(int i=0; i<repeatExecution; i++){
            long executionTime = EXPLoRa_CD_py(numberOfNodes,splittedLists);
            avg += executionTime;

            double currentExecutionSeconds = (double) executionTime/1000000000;

            System.out.println("The execution time of EXPLoRa-CD (without the reading of the file) is: " + executionTime+" ns");
            System.out.println("...or "+currentExecutionSeconds+" s\n");
        }

        avgSeconds = (double) avg/1000000000;
        avgSeconds = avgSeconds / repeatExecution;

        System.out.println("AVG execution time for "+repeatExecution+" iterations is: "+avgSeconds+"s");
        System.out.println("Exiting...");
    }

    public static ArrayList<ArrayList<Node>> getNodesFromFileMultithread(String inputFile, ArrayList<Integer> selectedBasestationsID) throws FileNotFoundException {

        //***************************************** Read the file and split the nodes in sublists *************************************************
        //Path in the txt file direction
        String path = inputFile;

        System.out.println("Reading from file, please wait...");

        //Array list of array list of nodes
        ArrayList<ArrayList<Node>> splittedLists = new ArrayList<ArrayList<Node>>();
        for(int i=0; i<selectedBasestationsID.size(); i++){
            splittedLists.add(new ArrayList<Node>());
        }

        //Read the file from the path string as input
        File fileObject = new File(path);
        Scanner myReader = new Scanner(fileObject);
        while (myReader.hasNextLine()) {
            //Read one line at a time
            String data = myReader.nextLine();
            //Parse each line
            String[] splittedString = data.split("\\s+");
            int nodeId = Integer.parseInt(splittedString[0]);
            double coordinateX = Double.parseDouble(splittedString[1]);
            double coordinateY = Double.parseDouble(splittedString[2]);
            //Create a node witht the lists of gateways id|RSSI|SF empty
            Node bufferNode = new Node(nodeId, coordinateX, coordinateY);
            //Fill the lists with all the gateways parameters
            int currentBasestationId = 0;
            //The minimum RSSI that can be taken into account is the minimum listenable at SF 12 and Bandwidth 125
            //double maxRSSI = -137; //This is the starting wrong version where i thought that if one selected basestation is npt in range of a node, the nothe will lost all the packets, this is wrong because the basestation willa ssign the node to the gateway that is able to listen it
            double maxRSSI = Double.NEGATIVE_INFINITY;
            int maxBs = -1;

            for(int i=3; i<splittedString.length; i+=2){
                double RSSI = Double.parseDouble(splittedString[i]);
                int SF = Integer.parseInt(splittedString[i+1]);
                bufferNode.addBaseStation(currentBasestationId);
                bufferNode.addBsRSSI(RSSI);
                bufferNode.addBsSF(SF);

                //Check to understand the destination list, so first check if the current basesatation is one between the selected ones, then check if the RSSI is higher than the min sesnitivity and higer than the previous RSSI
                if( (selectedBasestationsID.contains(currentBasestationId)) && (RSSI >= maxRSSI) ){
                    maxRSSI = RSSI;
                    maxBs = currentBasestationId;
                }

                currentBasestationId++;
            }

            //If no one of the selected basestation is able to listen the current node, error, else put the node in the selected list of basestations
            //The previous affermation is not correct because even if the node is not listened by the current selected, the current selected node will assign it to a basestation tha listen it
            /*if(maxBs == -1){
                System.out.println("Error, one node is not in the range of the selected base stations and cannot be pricessed." + bufferNode.toString());
                splittedLists.get(selectedBasestationsID.size()-1).add(bufferNode);
            }else{
                splittedLists.get(selectedBasestationsID.indexOf(maxBs)).add(bufferNode);
            }*/
            splittedLists.get(selectedBasestationsID.indexOf(maxBs)).add(bufferNode);

        }

        myReader.close();

        System.out.println("...reading complete!\n\n");

        return splittedLists;
    }

    public static ArrayList<Integer> selectBaseStationsID(int numberOfBaseStations){
        ArrayList<Integer> selectedBasestationsID = new ArrayList<Integer>();

        if(numberOfBaseStations==2) {
            selectedBasestationsID.add(67);
            selectedBasestationsID.add(142);
        } else if(numberOfBaseStations==4){
            selectedBasestationsID.add(64);
            selectedBasestationsID.add(69);
            selectedBasestationsID.add(139);
            selectedBasestationsID.add(144);
        } else {
            System.out.println("Not supported. Try again with 2 or 4 threads.");
            return null;
        }

        System.out.println("Number of selected basestations: " + selectedBasestationsID.size());
        System.out.println("Selected base stations: " + selectedBasestationsID.toString());

        return selectedBasestationsID;
    }
    
    //Function to wee diivide the spreading factor following the Waterfilling distribution
    public static int[] splitIntWithPercentages(float[] distributionArray, int numberToDivide){
        
        //From distribution to rounded integers for the division (the sum may not make the starting integer)
        int[] integerDIvision = new int[distributionArray.length];
        for(int i=0; i< distributionArray.length; i++){
            integerDIvision[i] = Math.round((distributionArray[i]/100)*numberToDivide);
        }
        //Create an array of size the number to divide
        int[] arrayFromInteger = new int[numberToDivide];
        
        //Create an array of aarays to popolate with the different splits of the startin array
        int[][] splits = new int[distributionArray.length][];
        
        //Starting from the end of the array create slices
        for(int i=(distributionArray.length-1); i>0; i--){
            
            //The copyOfRange(originalArray, splitStartingPoint, splitEndingPoint)
            splits[i] = Arrays.copyOfRange(arrayFromInteger, arrayFromInteger.length-integerDIvision[i], arrayFromInteger.length);
        
            //Delethe the splitted part from the starting array
            arrayFromInteger = Arrays.copyOfRange(arrayFromInteger, 0, arrayFromInteger.length-integerDIvision[i]);
            
        }
        //For the first element takes all the remaining array
        splits[0] = arrayFromInteger;
        
        //Create the final array of integers
        int[] finalArray = new int[splits.length];
        for(int i=0; i<splits.length; i++){
            finalArray[i] = splits[i].length;
        }
        
        return finalArray;
    }
    
    //Funtion to merge the EXPLoRa_CD_multiexecution_py threads output (that are already sorted) into just one sorted array using the merge-join theory
    public static int[] threadsOutputMergeJoin(ArrayList<Node[]> splittedArrays, int numberOfNodes){
        
        int[] spreadingFactorsArray = new int[numberOfNodes];
        
        int totalNumberOfSplits = splittedArrays.size();
        //Continue until one list remain
        while(totalNumberOfSplits > 1){
            //ArrayList with the merges for the current iteration
            ArrayList<Node[]> bufferListOfListOfNodes = new ArrayList<>();
            //Cycle two lists at a time to merge them
            for(int i=0; i<totalNumberOfSplits-1; i+=2){
                //Keep the indexes for each list
                int firstIndex = 0;
                int secondIndex = 0;
                int outputIndex = 0;
                //Create a buffer array of size the sum of the two lists size
                Node[] bufferOutputTwoListsMerge = new Node[splittedArrays.get(i).length+splittedArrays.get(i+1).length];
                //At maximum this for cycles a number of times equals to the sum of nodes in the current two lists
                for(int j=0; j<(splittedArrays.get(i).length+splittedArrays.get(i+1).length); j++){
                    //If one list is emptyed befor the other one, fill the output array with the remaining elemts of the other list
                    if( firstIndex == splittedArrays.get(i).length ){
                        while(secondIndex < splittedArrays.get(i+1).length){
                            //If this is the last step (last two splits), instead of populate an array of nodes, populate just the array of spreading factors
                            if(totalNumberOfSplits == 2){
                                //System.out.println(splittedArrays.get(i+1)[secondIndex].toString()); //DELETEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
                                spreadingFactorsArray[outputIndex] = splittedArrays.get(i+1)[secondIndex].getReferenceSpreadingFactor();
                                //bufferOutputTwoListsMerge[outputIndex] = splittedArrays.get(i+1)[secondIndex];          //This is only to know if all is working by create a final array of nodes
                            }else{
                                bufferOutputTwoListsMerge[outputIndex] = splittedArrays.get(i+1)[secondIndex];
                            }
                            secondIndex++;
                            outputIndex++;
                        }
                        break;
                    }else if( secondIndex == splittedArrays.get(i+1).length ){
                        while(firstIndex < splittedArrays.get(i).length){
                            //If this is the last step (last two splits), instead of populate an array of nodes, populate just the array of spreading factors
                            if(totalNumberOfSplits == 2){
                                //System.out.println(splittedArrays.get(i)[firstIndex].toString());//DELETEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
                                spreadingFactorsArray[outputIndex] = splittedArrays.get(i)[firstIndex].getReferenceSpreadingFactor();
                                //bufferOutputTwoListsMerge[outputIndex] = splittedArrays.get(i)[firstIndex];          //This is only to know if all is working by create a final array of nodes
                            }else{
                                bufferOutputTwoListsMerge[outputIndex] = splittedArrays.get(i)[firstIndex];
                            }
                            firstIndex++;
                            outputIndex++;
                        }
                        break;
                    }
                    //Check the current elements on head of each list and insert in the output the lowest one
                    if( splittedArrays.get(i)[firstIndex].getNodeId() < splittedArrays.get(i+1)[secondIndex].getNodeId() ){
                        //If this is the last step (last two splits), instead of populate an array of nodes, populate just the array of spreading factors
                        if(totalNumberOfSplits == 2){
                            //System.out.println(splittedArrays.get(i)[firstIndex].toString());//DELETEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
                            spreadingFactorsArray[outputIndex] = splittedArrays.get(i)[firstIndex].getReferenceSpreadingFactor();
                            //bufferOutputTwoListsMerge[outputIndex] = splittedArrays.get(i)[firstIndex];          //This is only to know if all is working by create a final array of nodes
                        }else{
                            bufferOutputTwoListsMerge[outputIndex] = splittedArrays.get(i)[firstIndex];
                        }
                        firstIndex++;
                        outputIndex++;
                    }else{
                        //If this is the last step (last two splits), instead of populate an array of nodes, populate just the array of spreading factors
                        if(totalNumberOfSplits == 2){
                            //System.out.println(splittedArrays.get(i+1)[secondIndex].toString());//DELETEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
                            spreadingFactorsArray[outputIndex] = splittedArrays.get(i+1)[secondIndex].getReferenceSpreadingFactor();
                            //bufferOutputTwoListsMerge[outputIndex] = splittedArrays.get(i+1)[secondIndex];          //This is only to know if all is working by create a final array of nodes
                        }else{
                            bufferOutputTwoListsMerge[outputIndex] = splittedArrays.get(i+1)[secondIndex];
                        }
                        secondIndex++;
                        outputIndex++;
                    }
                }
                //Every merge of two lists, insert the resulting one in the list of arrays of nodes
                bufferListOfListOfNodes.add(bufferOutputTwoListsMerge);
                splittedArrays.set(i, null);
                splittedArrays.set(i+1, null);
            }
            //If the number of arrays of nodes is odd, the last list is not keept by the cycle, so insert it in the list of arrays
            if(splittedArrays.size()%2 != 0){
                bufferListOfListOfNodes.add( splittedArrays.get(splittedArrays.size()-1) );
                splittedArrays.set(splittedArrays.size()-1, null);
            }
            //Ogni scorrimento di tutte le liste sostituisci la precedente lista di liste con la nuova dimezzata e diminuisci il numero di liste
            //Each time all the lists are managed, substitute the previous list of arrays with the new one and decrease the number of arrays used by the while
            splittedArrays = bufferListOfListOfNodes;
            totalNumberOfSplits = splittedArrays.size();
        }
        
        /*for(int i=0; i<numberOfNodes; i++ ){
            System.out.println(splittedArrays.get(0)[i].toString());
        }
        System.out.println(splittedArrays.get(0).length+"");*/
        
        return spreadingFactorsArray;
    }

    //EXPLoRa_C multithread algorithm, dividing the nodes in sub groups with the first method (select n basestations equidistants each others)
    public static long EXPLoRa_CD_py(int numberOfNodes, ArrayList<ArrayList<Node>> splittedList)throws InterruptedException{

        //***************************************** Multithreading phase *************************************************
        ArrayList<ArrayList<Node>> splittedCopy = new ArrayList<ArrayList<Node>>(splittedList);
        //One list contains the thread objects and the other contains the workers objects, the first is used to start and stop the threads, the second is used to take the output of the threads
        ArrayList<EXPLoRa_C_Runnable> workers = new ArrayList<EXPLoRa_C_Runnable>();
        ArrayList<Thread> threads = new ArrayList<Thread>();
        
        //Get the index of the split with the maximum size for the final merge-sort of the threads output
        int maxSizeSplit = -1;
        
        //Create the threads passing the stream
        for(int i=0; i<splittedCopy.size(); i++){
            EXPLoRa_C_Runnable buffer = new EXPLoRa_C_Runnable(splittedCopy.get(i).stream(), splittedCopy.get(i).size());
            workers.add(buffer);
            threads.add(new Thread(buffer));
            //Ger the maximum size split
            if( maxSizeSplit < splittedCopy.get(i).size() ){
                maxSizeSplit = splittedCopy.get(i).size();
            }
            splittedCopy.set(i, null);
        }
        
        //Start the threads
        System.out.println("Starting " + String.valueOf(splittedCopy.size()) + " threads");
        for(int i=0; i<splittedCopy.size(); i++){
            threads.get(i).start();
        }
        
        ArrayList<Node[]> splittedArrays = new ArrayList<>();
        
        //Start the timer for the performances
        long startTimeThreadExecution = System.nanoTime();
        
        //Wait for the threads ends
        for(int i=0; i<splittedCopy.size(); i++){
            threads.get(i).join();
            //Put the output of the threads in one list of arrays of nodes
            splittedArrays.add(workers.get(i).getOutputArray());
            workers.set(i, null);
        }
        
        //***************************************** Merge and Final Output *************************************************
        
        //Merge the threads output and given that their output is already sorted, this can be a sort last step of the sort-merge algoritm
        //Note that this can be done in a lot of different ways, the classical merge sort will require a lot of space (we have memory problem), is also possible to implement a multithread version of the merge sort (memory problem again)
        //Note the current implemented version takes two ythread output array at a time and merge them until to have a last final single array that will be stored in the ArrayList of size 1
        //The output will be the array of integer and is populated at the last step of the merge-join, when the last two split lists tare joined into one
        int[] spreadingFactorsArray = threadsOutputMergeJoin(splittedArrays, numberOfNodes);
        /*for(int i=0; i<numberOfNodes; i++ ){
            System.out.println(spreadingFactorsArray[i]);
        }*/
        
        //Stop the timer
        long stopTimeEndFunction = System.nanoTime();
        
        currentExecutionTime = stopTimeEndFunction-startTimeThreadExecution;
        
        return currentExecutionTime;
    }

}