import subprocess as sb
import sys

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
#define the number of different gateways on which run the EXPLoRa-CD
javaEXPLoRaCDdivision = 15

#*********************************
#******BENCHMARK PARAMETERS*******
#*********************************
iterationsNumber = 10
powershellCommand = "python loraDirMulBSfading_uniformSF_collSF_v9_5.py "+str(nrNodes)+" "+str(avgSendTime)+" "+str(experiment)+" "+str(simtime)+" "+str(nrBS)+" "+str(full_collision)+" "+str(interfSF)+" "+str(fading)+" "+str(ssff)+" "+str(ccrr)+" "+str(bbww)+" "+str(eta)+" "+str(SF_input)+" "+str(max_dist_input)+" "+str(distanceBetweenGW)+" "+nodes_file+" "+javaPythonVersion
run_return = None
#arrayOfNumberOfBasestations = [3, 5, 10, 20]
#arrayOfNumberOfNodes = [100, 500, 1000, 2000]
arrayOfEXPLoRaCDdivisions = [6, 15, 25, 50]
arrayOfEXPLoRaCDdivisions_x = [3, 5, 5, 5]
arrayOfEXPLoRaCDdivisions_y = [2, 3, 5, 10]
#if the arrays are composed by 1 value, is like to run just 1 test on specific number of basestations and end-devices
arrayOfNumberOfBasestations = [100]
arrayOfNumberOfNodes = [10000]
#arrayOfEXPLoRaCDdivisions = [25]

for nodesNumber in arrayOfNumberOfNodes:
    for basestationsNumber in arrayOfNumberOfBasestations:

        nrBS = basestationsNumber
        nrNodes = nodesNumber

        for splitsNumber in arrayOfEXPLoRaCDdivisions:

            javaEXPLoRaCDdivision = splitsNumber
            print("Index of the splits x_y arrays: ", arrayOfEXPLoRaCDdivisions.index(splitsNumber))
            javaEXPLoRaCDdivision_x = arrayOfEXPLoRaCDdivisions_x[arrayOfEXPLoRaCDdivisions.index(splitsNumber)]
            javaEXPLoRaCDdivision_y = arrayOfEXPLoRaCDdivisions_y[arrayOfEXPLoRaCDdivisions.index(splitsNumber)]

            #arrays in which store the resultin DER
            pythonDERvalues = []
            javaDERvalues = []
            javaDistributedDERvalues = []
            javaGeoDistributedDERvalues = []

            print("BENCHMARK WITH "+str(nrNodes)+" NODES AND "+str(nrBS)+" BASE STATIONS AND "+str(javaEXPLoRaCDdivision)+" SPLITS ON "+str(iterationsNumber)+" ITERATIONS")
            for i in range(iterationsNumber):
                #print("Iteration "+str(i+1)+"\\"+str(iterationsNumber)+" ...")

                #then run the java version, so set the variables for the java version
                '''#nodes_file = str(nrNodes)+"-nodes-raw.txt"
                nodes_file = str(nrNodes)+"-nodes-raw-BwGw-12000-BwGN-12000-mygen.txt"
                javaPythonVersion = "java"
                powershellCommand = "python loraDirMulBSfading_uniformSF_collSF_v9_5.py "+str(nrNodes)+" "+str(avgSendTime)+" "+str(experiment)+" "+str(simtime)+" "+str(nrBS)+" "+str(full_collision)+" "+str(interfSF)+" "+str(fading)+" "+str(ssff)+" "+str(ccrr)+" "+str(bbww)+" "+str(eta)+" "+str(SF_input)+" "+str(max_dist_input)+" "+str(distanceBetweenGW)+" "+nodes_file+" "+javaPythonVersion
                run_return = run(powershellCommand)
                #print(str(run_return.stdout, "utf-8"))
                #check if the execution has been sucessfull
                if run_return.returncode < 0:
                    break
                else:
                    derValueBuffer = fromExecutionOutputToDerValue(run_return)
                    javaDERvalues.append(derValueBuffer)'''

                #last run the java distributed version, so set the variables for the java distributed version
                #nodes_file = str(nrNodes)+"-nodes-raw.txt"
                nodes_file = str(nrNodes)+"-nodes-raw-BwGw-12000-BwGN-12000-mygen.txt"
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


                #last run the java distributed version, so set the variables for the java distributed version
                #nodes_file = str(nrNodes)+"-nodes-raw.txt"
                nodes_file = str(nrNodes)+"-nodes-raw-BwGw-12000-BwGN-12000-mygen.txt"
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


            #check if an error is occurred or all are going well at each iteration 
            if run_return.returncode < 0:
                print('An error is occurred during the execution of the command "' + powershellCommand + '"')
                print("The error is: ", run_return.stderr)
            else:
                print("All the executions eded succefully !!!")
                #print("Python executions DER result: ", pythonDERvalues)
                #print("Java executions DER result: ", javaDERvalues)

                #make an average of all the resulting DER values
                pythonAVG = 0
                javaAVG = 0
                javaDistributedAVG = 0
                javaGeoDistributedAVG = 0
                for i in range(iterationsNumber):
                    '''pythonAVG += pythonDERvalues[i]
                    javaAVG += javaDERvalues[i]'''
                    javaDistributedAVG += javaDistributedDERvalues[i]
                    javaGeoDistributedAVG += javaGeoDistributedDERvalues[i]

                '''pythonAVG = pythonAVG/iterationsNumber
                javaAVG = javaAVG/iterationsNumber'''
                javaDistributedAVG = javaDistributedAVG/iterationsNumber
                javaGeoDistributedAVG = javaGeoDistributedAVG/iterationsNumber

                '''print("Python average DER on "+str(iterationsNumber)+" iterations: ", pythonAVG)
                print("Java average DER on "+str(iterationsNumber)+" iterations: ", javaAVG)'''
                print("Java distributed average DER on "+str(iterationsNumber)+" iterations: ", javaDistributedAVG)
                print("Java GeoDistributed average DER on "+str(iterationsNumber)+" iterations: ", javaGeoDistributedAVG)
                print("\n")

