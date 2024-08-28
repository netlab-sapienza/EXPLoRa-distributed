import subprocess as sb
import sys
import pandas as pd

def run(cmd):
    completed = sb.run(["powershell", "-Command", cmd], capture_output=True)
    return completed


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
#name of the file with the nodes, if "None" it generate the new node file scenario
nodes_file = "None" #str(nrNodes)+"-nodes-raw.txt"
#use "python" to run the professor code, use "java" to run my code in default (None) the python version is runned
javaPythonVersion = "python" #"java-start" #"java" #"java-cd-m1" #"java-cd-m1-splitVision" #"java-cd-m2" #"java-cd-m2-splitVision"
#these are the number of different slices that you would obtain with de division methods
#in particular the firts division method (RSSI based) takes just the first of this three parameters
#instead the second division method (geometry based) takes all the three parameters becasue in addition to the number of slices, the number of columns and rows of the splitting grid
javaEXPLoRaCDdivision = 0 #2
javaEXPLoRaCDdivision_x = "" #2
javaEXPLoRaCDdivision_y = "" #1



#LORASIM PARAMETERS
powershellCommand =     "python loraDirMulBSfading_uniformSF_collSF_v9_5.py "
powershellCommand +=    str(nrNodes)+" "
powershellCommand +=    str(avgSendTime)+" "
powershellCommand +=    str(experiment)+" "
powershellCommand +=    str(simtime)+" "
powershellCommand +=    str(nrBS)+" "
powershellCommand +=    str(full_collision)+" "
powershellCommand +=    str(interfSF)+" "
powershellCommand +=    str(fading)+" "
powershellCommand +=    str(ssff)+" "
powershellCommand +=    str(ccrr)+" "
powershellCommand +=    str(bbww)+" "
powershellCommand +=    str(eta)+" "
powershellCommand +=    str(SF_input)+" "
powershellCommand +=    str(max_dist_input)+" "
powershellCommand +=    str(distanceBetweenGW)+" "
powershellCommand +=    nodes_file+" "
#NEW EXPLORA-DISTRIBUTED PARAMETERS
powershellCommand +=    javaPythonVersion+" "
if javaEXPLoRaCDdivision != 0:
    powershellCommand +=    str(javaEXPLoRaCDdivision)+" "
    powershellCommand +=    str(javaEXPLoRaCDdivision_x)+" "
    powershellCommand +=    str(javaEXPLoRaCDdivision_y)


#RUN THE POWERSHELL COMMAND LINE AND CAPTURE THE OUTPUT IN THE RUN RETURN VARIABLE
run_return = run(powershellCommand)

#CHECK IF THE EXECUTION IS DONE SUCCESFULLY
if run_return.returncode < 0:
    print("THERE IS AN ERROR IN THE EXECUTION")
    print("THE ERROR IS: ", run_return.stderr)
else:
    print("THE EXECUTION HAS DONE SUCCEFULLY")
    print("THE ERROR IS: ", str(run_return.stderr, "utf-8"))
    print(str(run_return.stdout, "utf-8"))
    #derValueBuffer = fromExecutionOutputToDerValue(run_return)
    #javaDistributedSplitVisionDERvalues.append(derValueBuffer)
