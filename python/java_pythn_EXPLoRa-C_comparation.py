import subprocess as sb
import sys
import pandas as pd

def run(cmd):
    completed = sb.run(["powershell", "-Command", cmd], capture_output=True)
    return completed

def fromExecutionOutputToDerValue(stdout):
    output = str(stdout.stdout, "utf-8")
    listOfLines = str(output).split("\n")
    listOfStrings = None
    for i in listOfLines:
        listOfStrings = i.split(" ")
        if(listOfStrings[0] == "DER:"):
            stringOfJustTheNumber = listOfStrings[1][:-2]
            derValue = float(stringOfJustTheNumber)
            return derValue
        
    print(str(stdout.stdout, "utf-8"))
    return None


#*********************************
#*******DATAFRAME CREATION********
#*********************************
dataframeRows = ['3', '5', '10', '20']
dataframeFirstColumn = [100, 500, 1000, 2000, 5000, 7500, 10000, 15000]
pythonDF = pd.DataFrame(columns=dataframeRows)
javaDF = pd.DataFrame(columns=dataframeRows)
javaDistributedDF = pd.DataFrame(columns=dataframeRows)
javaGeoDistributedDF = pd.DataFrame(columns=dataframeRows)
javaGeoDistributedSplitVisionDF = pd.DataFrame(columns=dataframeRows)
javaDistributedSplitVisionDF = pd.DataFrame(columns=dataframeRows)

pythonDF.insert(0, "#nodes", dataframeFirstColumn)
javaDF.insert(0, "#nodes", dataframeFirstColumn)
javaDistributedDF.insert(0, "#nodes", dataframeFirstColumn)
javaGeoDistributedDF.insert(0, "#nodes", dataframeFirstColumn)
javaGeoDistributedSplitVisionDF.insert(0, "#nodes", dataframeFirstColumn)
javaDistributedSplitVisionDF.insert(0, "#nodes", dataframeFirstColumn)

dataframe_y_index = 0

#*********************************
#*******LORASIM PARAMETERS********
#*********************************
#parameter number of nodes to spawn
nrNodes = 100
#parameter time between messages for each node
avgSendTime = 4800000
#parameter experiment to run
experiment = 6
#AF_COMMENTS parameter total time of the running experiment
simtime = 172800000
#parameter number of base station to spawn
nrBS = 3
#parameter flag to enable to allow the half of collision in the cases foreseen by the Capture effect, if not enabled count as collided both the packets
full_collision = 1
#parameter inter spreading factors interference, given that the SFs are not perfectly orthogonals, if enabled count the interference between SFs with SNR under a threshold
interfSF = 0
#parameter flag to enable to allow the fading effect (variable power signal at the same distance or at different distances)
fading = 7
#parameter starter spreding factor of the devices
ssff = 7
#parameter rate of the device
ccrr = 1
#parameter bandwidth of the devices
bbww = 125
#parameter exponent with which the power is attenuated, higher is the exponent, higher is the attenuation effect
eta = 2.9
#parameter that specify the ADR algorithm to run
SF_input = 27
#parameter that specify the maximum distance at which the nodes can be placed far away from the base station at which they are assigned (the assignment is 1 node for each base station at iteration)
max_dist_input = 12000
#parameter that specify distance between the base stations
distanceBetweenGW = 12000
#name of the file with the nodes
nodes_file = str(nrNodes)+"-nodes-raw.txt"
#use "python" to run the professor code, use "java" to run my code in default (None) the python version is runned
javaPythonVersion = "python"

#*********************************
#******BENCHMARK PARAMETERS*******
#*********************************
iterationsNumber = 3 #8
powershellCommand = "python loraDirMulBSfading_uniformSF_collSF_v9_5.py "+str(nrNodes)+" "+str(avgSendTime)+" "+str(experiment)+" "+str(simtime)+" "+str(nrBS)+" "+str(full_collision)+" "+str(interfSF)+" "+str(fading)+" "+str(ssff)+" "+str(ccrr)+" "+str(bbww)+" "+str(eta)+" "+str(SF_input)+" "+str(max_dist_input)+" "+str(distanceBetweenGW)+" "+nodes_file+" "+javaPythonVersion
run_return = None
arrayOfNumberOfBasestations = [3, 5, 10, 20]
arrayOfNumberOfNodes = [100, 500, 1000, 2000, 5000, 7500, 10000, 15000]
arrayOfEXPLoRaCDdivisions = [2, 2, 2, 4]
arrayOfEXPLoRaCDdivisions_x = [2, 1, 1, 2]
arrayOfEXPLoRaCDdivisions_y = [1, 2, 2, 2]
#if the arrays are composed by 1 value, is like to run just 1 test on specific number of basestations and end-devices
#arrayOfNumberOfBasestations = [3]
#arrayOfNumberOfNodes = [100]
#arrayOfEXPLoRaCDdivisions = [2]
#arrayOfEXPLoRaCDdivisions_x = [2]
#arrayOfEXPLoRaCDdivisions_y = [1]

for nodesNumber in arrayOfNumberOfNodes:
    for basestationsNumber in arrayOfNumberOfBasestations:
        nrBS = basestationsNumber
        nrNodes = nodesNumber

        javaEXPLoRaCDdivision = arrayOfEXPLoRaCDdivisions[arrayOfNumberOfBasestations.index(nrBS)]
        javaEXPLoRaCDdivision_x = arrayOfEXPLoRaCDdivisions_x[arrayOfNumberOfBasestations.index(nrBS)]
        javaEXPLoRaCDdivision_y = arrayOfEXPLoRaCDdivisions_y[arrayOfNumberOfBasestations.index(nrBS)]

        #arrays in which store the resultin DER
        pythonDERvalues = []
        javaDERvalues = []
        javaDistributedDERvalues = []
        javaGeoDistributedDERvalues = []
        javaGeoDistributedSplitVisionDERvalues = []
        javaDistributedSplitVisionDERvalues = []

        print("BENCHMARK WITH "+str(nrNodes)+" NODES AND "+str(nrBS)+" BASE STATIONS ON "+str(iterationsNumber)+" ITERATIONS")
        for i in range(iterationsNumber):
            #print("Iteration "+str(i+1)+"\\"+str(iterationsNumber)+" ...")
            '''
            #first run the python version, so set the variables for the python version
            nodes_file = "None"
            javaPythonVersion = "python"
            powershellCommand = "python loraDirMulBSfading_uniformSF_collSF_v9_5.py "+str(nrNodes)+" "+str(avgSendTime)+" "+str(experiment)+" "+str(simtime)+" "+str(nrBS)+" "+str(full_collision)+" "+str(interfSF)+" "+str(fading)+" "+str(ssff)+" "+str(ccrr)+" "+str(bbww)+" "+str(eta)+" "+str(SF_input)+" "+str(max_dist_input)+" "+str(distanceBetweenGW)+" "+nodes_file+" "+javaPythonVersion
            run_return = run(powershellCommand)
            #print(str(run_return.stdout, "utf-8"))
            #check if the execution has been sucessfull
            if run_return.returncode < 0:
                break
            else:
                derValueBuffer = fromExecutionOutputToDerValue(run_return)
                pythonDERvalues.append(derValueBuffer)

            #then run the java version, so set the variables for the java version
            nodes_file = str(nrNodes)+"-nodes-raw.txt"
            javaPythonVersion = "java"
            powershellCommand = "python loraDirMulBSfading_uniformSF_collSF_v9_5.py "+str(nrNodes)+" "+str(avgSendTime)+" "+str(experiment)+" "+str(simtime)+" "+str(nrBS)+" "+str(full_collision)+" "+str(interfSF)+" "+str(fading)+" "+str(ssff)+" "+str(ccrr)+" "+str(bbww)+" "+str(eta)+" "+str(SF_input)+" "+str(max_dist_input)+" "+str(distanceBetweenGW)+" "+nodes_file+" "+javaPythonVersion
            run_return = run(powershellCommand)
            #print(str(run_return.stdout, "utf-8"))
            #check if the execution has been sucessfull
            if run_return.returncode < 0:
                break
            else:
                derValueBuffer = fromExecutionOutputToDerValue(run_return)
                javaDERvalues.append(derValueBuffer)

            #java distributed version with first division method, so set the variables for the java distributed version
            nodes_file = str(nrNodes)+"-nodes-raw.txt"
            javaPythonVersion = "java-cd-m1"
            powershellCommand = "python loraDirMulBSfading_uniformSF_collSF_v9_5.py "+str(nrNodes)+" "+str(avgSendTime)+" "+str(experiment)+" "+str(simtime)+" "+str(nrBS)+" "+str(full_collision)+" "+str(interfSF)+" "+str(fading)+" "+str(ssff)+" "+str(ccrr)+" "+str(bbww)+" "+str(eta)+" "+str(SF_input)+" "+str(max_dist_input)+" "+str(distanceBetweenGW)+" "+nodes_file+" "+javaPythonVersion+" "+str(javaEXPLoRaCDdivision)
            run_return = run(powershellCommand)
            #print(str(run_return.stdout, "utf-8"))
            #check if the execution has been sucessfull
            if run_return.returncode < 0:
                break
            else:
                derValueBuffer = fromExecutionOutputToDerValue(run_return)
                javaDistributedDERvalues.append(derValueBuffer)

            #java distributed version with second division method, so set the variables for the java distributed version
            nodes_file = str(nrNodes)+"-nodes-raw.txt"
            javaPythonVersion = "java-cd-m2"
            powershellCommand = "python loraDirMulBSfading_uniformSF_collSF_v9_5.py "+str(nrNodes)+" "+str(avgSendTime)+" "+str(experiment)+" "+str(simtime)+" "+str(nrBS)+" "+str(full_collision)+" "+str(interfSF)+" "+str(fading)+" "+str(ssff)+" "+str(ccrr)+" "+str(bbww)+" "+str(eta)+" "+str(SF_input)+" "+str(max_dist_input)+" "+str(distanceBetweenGW)+" "+nodes_file+" "+javaPythonVersion+" "+str(javaEXPLoRaCDdivision)+" "+str(javaEXPLoRaCDdivision_x)+" "+str(javaEXPLoRaCDdivision_y)
            run_return = run(powershellCommand)
            #print(str(run_return.stdout, "utf-8"))
            #check if the execution has been sucessfull
            if run_return.returncode < 0:
                break
            else:
                derValueBuffer = fromExecutionOutputToDerValue(run_return)
                javaGeoDistributedDERvalues.append(derValueBuffer)

            #java distributed version with second division method and the vision of the gateways by the nodes splittd
            nodes_file = str(nrNodes)+"-nodes-raw.txt"
            #nodes_file = "None"
            javaPythonVersion = "java-cd-m2-splitVision"
            powershellCommand = "python loraDirMulBSfading_uniformSF_collSF_v9_5.py "+str(nrNodes)+" "+str(avgSendTime)+" "+str(experiment)+" "+str(simtime)+" "+str(nrBS)+" "+str(full_collision)+" "+str(interfSF)+" "+str(fading)+" "+str(ssff)+" "+str(ccrr)+" "+str(bbww)+" "+str(eta)+" "+str(SF_input)+" "+str(max_dist_input)+" "+str(distanceBetweenGW)+" "+nodes_file+" "+javaPythonVersion+" "+str(javaEXPLoRaCDdivision)+" "+str(javaEXPLoRaCDdivision_x)+" "+str(javaEXPLoRaCDdivision_y)
            run_return = run(powershellCommand)
            #print(str(run_return.stdout, "utf-8"))
            #check if the execution has been sucessfull
            if run_return.returncode < 0:
                break
            else:
                derValueBuffer = fromExecutionOutputToDerValue(run_return)
                javaGeoDistributedSplitVisionDERvalues.append(derValueBuffer)
            '''
            #java distributed version with second division method and the vision of the gateways by the nodes splittd
            #nodes_file = str(nrNodes)+"-nodes-raw.txt"
            nodes_file = "None"
            javaPythonVersion = "java-cd-m1-splitVision"
            powershellCommand = "python loraDirMulBSfading_uniformSF_collSF_v9_5.py "+str(nrNodes)+" "+str(avgSendTime)+" "+str(experiment)+" "+str(simtime)+" "+str(nrBS)+" "+str(full_collision)+" "+str(interfSF)+" "+str(fading)+" "+str(ssff)+" "+str(ccrr)+" "+str(bbww)+" "+str(eta)+" "+str(SF_input)+" "+str(max_dist_input)+" "+str(distanceBetweenGW)+" "+nodes_file+" "+javaPythonVersion+" "+str(javaEXPLoRaCDdivision)
            run_return = run(powershellCommand)
            #print(str(run_return.stdout, "utf-8"))
            #check if the execution has been sucessfull
            if run_return.returncode < 0:
                break
            else:
                derValueBuffer = fromExecutionOutputToDerValue(run_return)
                javaDistributedSplitVisionDERvalues.append(derValueBuffer)


        #check if an error is occurred or all are going well at each iteration 
        if run_return.returncode < 0:
            print('An error is occurred during the execution of the command "' + powershellCommand + '"')
            print("The error is: ", run_return.stderr)
        else:
            print("All the executions eded succefully !!!")
            #print("Python executions DER result: ", pythonDERvalues)
            #print("Java executions DER result: ", javaDERvalues)

            #make an average of all the resulting DER values
            '''pythonAVG = 0
            javaAVG = 0
            javaDistributedAVG = 0
            javaGeoDistributedAVG = 0
            javaGeoDistributedSplitVisionAVG = 0'''
            javaDistributedSplitVisionAVG = 0
            for i in range(iterationsNumber):
                '''pythonAVG += pythonDERvalues[i]
                javaAVG += javaDERvalues[i]
                javaDistributedAVG += javaDistributedDERvalues[i]
                javaGeoDistributedAVG += javaGeoDistributedDERvalues[i]
                javaGeoDistributedSplitVisionAVG += javaGeoDistributedSplitVisionDERvalues[i]'''
                javaDistributedSplitVisionAVG += javaDistributedSplitVisionDERvalues[i]
                
            '''pythonAVG = pythonAVG/iterationsNumber
            javaAVG = javaAVG/iterationsNumber
            javaDistributedAVG = javaDistributedAVG/iterationsNumber
            javaGeoDistributedAVG = javaGeoDistributedAVG/iterationsNumber
            javaGeoDistributedSplitVisionAVG = javaGeoDistributedSplitVisionAVG/iterationsNumber'''
            javaDistributedSplitVisionAVG = javaDistributedSplitVisionAVG/iterationsNumber

            '''print("Python average DER on "+str(iterationsNumber)+" iterations: ", pythonAVG)
            print("Java average DER on "+str(iterationsNumber)+" iterations: ", javaAVG)
            print("Java distributed average DER on "+str(iterationsNumber)+" iterations: ", javaDistributedAVG)
            print("Java geo distributed average DER on "+str(iterationsNumber)+" iterations: ", javaGeoDistributedAVG)
            print("Java geo distributed with splitted vision average DER on "+str(iterationsNumber)+" iterations: ", javaGeoDistributedSplitVisionAVG)'''
            print("Java distributed with splitted vision average DER on "+str(iterationsNumber)+" iterations: ", javaDistributedSplitVisionAVG)
            print("\n")

            #Insert in the dataframes
            '''pythonDF.at[dataframe_y_index, str(nrBS)] = pythonAVG
            javaDF.at[dataframe_y_index, str(nrBS)] = javaAVG
            javaDistributedDF.at[dataframe_y_index, str(nrBS)] = javaDistributedAVG
            javaGeoDistributedDF.at[dataframe_y_index, str(nrBS)] = javaGeoDistributedAVG
            javaGeoDistributedSplitVisionDF.at[dataframe_y_index, str(nrBS)] = javaGeoDistributedSplitVisionAVG'''
            javaDistributedSplitVisionDF.at[dataframe_y_index, str(nrBS)] = javaDistributedSplitVisionAVG


    #Increment the y index counter of the dataframe to fill the next row
    dataframe_y_index += 1


'''print(pythonDF)
print(javaDF)
print(javaDistributedDF)
print(javaGeoDistributedDF)
print(javaGeoDistributedSplitVisionDF)'''
print(javaDistributedSplitVisionDF)