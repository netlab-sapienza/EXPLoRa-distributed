# turn on/off graphics
import simpy
import random
import numpy as np
import math
import sys
import matplotlib.pyplot as plt
import os
from matplotlib.patches import Rectangle
import utm
from datetime import timedelta
import datetime
'''AF_ADD '''
from py4j.java_gateway import JavaGateway
import ast

#
# this function creates a BS
#
class myBS():
    def __init__(self, id):
        self.id = id
        self.x = 0
        self.y = 0

        # This is a hack for now
        global nrBS
        global distanceBetweenGW
        global matrixCordinatesGW
        global matrixCordinatesDimRow
        global matrixCordinatesDimCol
        global maxDist
        global maxX
        global maxY

        if self.id == 0:

            GWDist = distanceBetweenGW / np.sqrt(3)
            theta = (1.0 / 3.0) * (self.id % 3) + (1.0 / 12.0)
            X = GWDist * math.cos(2 * math.pi * theta)
            Y = GWDist * math.sin(2 * math.pi * theta)
            X = X + 2 * GWDist
            Y = Y + 2 * GWDist

            # coordnatesMatrixGW creation
            baseCoordinatesY = Y + (distanceBetweenGW * np.sqrt(5))*2
            for xx in range(matrixCordinatesDimRow):
                baseCoordinatesX = X - distanceBetweenGW - \
                    ((xx % 2) * distanceBetweenGW / 2)
                for yy in range(matrixCordinatesDimCol):
                    matrixCordinatesGW[xx, yy, 0] = baseCoordinatesX
                    matrixCordinatesGW[xx, yy, 1] = baseCoordinatesY
                    baseCoordinatesX += distanceBetweenGW
                baseCoordinatesY -= distanceBetweenGW * np.sqrt(5) / 2


        if nrBS == 3 and self.id == 2:
            self.x = matrixCordinatesGW[6 % matrixCordinatesDimRow, int(
                6 / matrixCordinatesDimRow), 0]
            self.y = matrixCordinatesGW[6 % matrixCordinatesDimRow, int(
                6 / matrixCordinatesDimRow), 1]
        else:
            # print(self.id%matrixCordinatesDimRow)
            # print(self.id/matrixCordinatesDimRow)
            self.x = matrixCordinatesGW[self.id % matrixCordinatesDimRow, int(
                self.id / matrixCordinatesDimRow), 0]
            self.y = matrixCordinatesGW[self.id % matrixCordinatesDimRow, int(
                self.id / matrixCordinatesDimRow), 1]
            # self.x = matrixCordinatesGW[0, self.id, 0]
            # self.y = matrixCordinatesGW[0, self.id, 1]
            # print "BSx:", self.x, "BSy:", self.y
            # input ("TEST")

        
        global graphics
        # if (graphics):
        #     global ax
        #     # XXX should be base station position
        #     ax.add_artist(plt.Circle((self.x, self.y), 300, fill=True, color='green'))
        #     ax.add_artist(plt.Circle((self.x, self.y), maxDist, fill=False, color='green'))

        # prepare graphics and add sink
        if (graphics == 1):
            global ax
            #Add also the gateways id to understand how to divide
            plt.text(self.x, self.y, str(self.id), fontsize=12, color='red')
            # XXX should be base station position
            ax.add_artist(plt.Circle((self.x, self.y),
                          600, fill=True, color='green'))
            # ax.add_artist(plt.Circle((bsx, bsy), maxDist, fill=False, color='green'))
            color = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1),
                     (1, 0, 1), (0, 1, 1), (1, 1, 0)]
            all_color = []
            for (r, g, b) in color:
                all_color.append('#%02x%02x%02x' %
                                 (int(r * 255), int(g * 255), int(b * 255)))
            for ii in [0, 5]:
                ax.add_artist(plt.Circle((self.x, self.y),
                              all_Dist[ii], fill=False, color=all_color[ii]))
                # print(all_Dist[ii])
            for ii in [5]:
                if self.id in [6, 8, 16, 18]:
                    ax.add_artist(plt.Circle(
                        (self.x, self.y), all_Dist[ii], fill=False, color=all_color[ii]))
        

#
# this function creates a node
#

class myNode():
    def __init__(self, id, xpos, ypos):
        global bs
        global nrBS
        global maxDist

        global mat_rssi
        global SF_vec

        global nodeAllocationCount
        global nodeAllocationArray

        self.id = id


        self.x = 0
        self.y = 0
        self.packet = []
        self.dist = []
        self.ortho = 0

        # currentBS = nodeAllocationArray[nodeAllocationCount]
        # nodeAllocationCount += 1
        # if nodeAllocationCount >= len (nodeAllocationArray):
        #     nodeAllocationCount = 0
        currentBS = self.id % nrBS

        # this is very complex prodecure for placing nodes
        # and ensure minimum distance between each pair of nodes
        if xpos == 0 and ypos == 0:
            found = 0
            rounds = 0
            global nodes
            while (found == 0 and rounds < 100):
                global maxX
                global maxY

                # original placement
                # posx = random.randint(0,int(maxX))
                # posy = random.randint(0,int(maxY))

                a = random.random()
                b = random.random()

                if b < a:
                    a, b = b, a
                # posx = b * maxDist * math.cos(2 * math.pi * a / b) + bs[0].x
                # posy = b * maxDist * math.sin(2 * math.pi * a / b) + bs[0].y
                

                posx = b * maxDist * \
                    math.cos(2 * math.pi * a / b) + bs[currentBS].x
                posy = b * maxDist * \
                    math.sin(2 * math.pi * a / b) + bs[currentBS].y

                # posx = b * maxDist * math.cos(2 * math.pi * a ) + bs[currentBS].x
                # posy = b * maxDist * math.sin(2 * math.pi * a ) + bs[currentBS].y

                # circularRangeDistance = [ 0, int(maxDist/6), int(maxDist/6)*2, int(maxDist/6)*3, int(maxDist/6)*4, int(maxDist/6)*5]
                # posx = ( circularRangeDistance[int(self.id/int(nrNodes/6))] + (b * int(maxDist/6))) * math.cos(2 * math.pi * a ) + bs[currentBS].x
                # posy = ( circularRangeDistance[int(self.id/int(nrNodes/6))] + (b * int(maxDist/6))) * math.sin(2 * math.pi * a ) + bs[currentBS].y

                # a = random.triangular ()
                # b = random.triangular (0,maxDist)
                # #random.triangular (low, high, mode)
                # #random.triangular (low, high, mode)
                # posx = b * math.cos(2 * math.pi * a) + bs[currentBS].x
                # posy = b * math.sin(2 * math.pi * a) + bs[currentBS].y

                if len(nodes) > 0:
                    for index, n in enumerate(nodes):
                        dist = np.sqrt(((abs(n[0]-posx))**2) +
                                       ((abs(n[1]-posy))**2))
                        if dist >= 1:
                            found = 1
                            self.x = posx
                            self.y = posy
                            self.r = b * maxDist
                        else:
                            rounds = rounds + 1
                            if rounds == 100:
                                print("could not place new node, giving up")
                                exit(-2)
                else:
                    print("first node")
                    self.x = posx
                    self.y = posy
                    self.r = b * maxDist
                    found = 1
        else:
            self.x = xpos
            self.y = ypos
            self.r = 0

        for i in range(0, nrBS):
            d = np.sqrt((self.x-bs[i].x)*(self.x-bs[i].x) +
                        (self.y-bs[i].y)*(self.y-bs[i].y))
            self.dist.append(d)
            self.packet.append(
                myPacket(self.id, self.dist[i], i))
            # print("node {} sf {} bs {} lost {}".format(self.packet[i].nodeid, self.packet[i].sf, self.packet[i].bs, self.packet[i].lost))


        
        # graphics for node
        global graphics
        '''AF_MODIFY 
        if (False):
        '''
        if (graphics == 1):
            global ax
            #Add also the nodes id to understand how to divide
            plt.text(self.x, self.y, str(self.id), fontsize=9, color='green')
            ax.add_artist(plt.Circle((self.x, self.y),
                          100, fill=True, color='blue'))
            # ax.text(self.x, self.y, str(self.id), fontsize=10)
        

class myPacket():
    def __init__(self, nodeid, distance, bs):
        global experiment
        global Ptx
        global gamma
        global d0
        global var
        global Lpld0
        global GL

        # new: base station ID
        self.bs = bs
        self.nodeid = nodeid
        
        #set the parameters of the packte sf, bw, cr
        self.sf = ssff
        self.cr = ccrr
        self.bw = bbww

        
        Prx = Lpld0 + 10*gamma*math.log10(d0/distance)


        # transmission range, needs update XX
        self.rssi = Prx


        # frequencies: lower bound + number of 61 Hz steps
        #self.freq = 860000000 + random.randint(0,2622950)
        self.freq = 860000000

        # for certain experiments override these and
        # choose some random frequences
        self.freq = 860000000





nrBS = 3 #100 200 9 5 500 1000 80 300 10
nrNodes = 50 #10000  100000 100 250000 500000 50000 150000
maxDist = 12000
distanceBetweenGW = 12000

#graphic
graphics = 1

# list of nodes
nodes = []

# list of base stations
bs = []

# base station placement
bsx = maxDist+20
bsy = maxDist+20
plot_xmax = 100000
plot_ymax = 100000
maxX = 100000 #20000
maxY = 100000 #20000

#these are the mx colums and rows of the matrix on which distribute the basestation
matrixCordinatesDimRow = 5 #15 50 3 10 23 32 9 18
matrixCordinatesDimCol = 5 #15 35 3 10 23 32 9 18
matrixCordinatesGW = np.empty(shape=[matrixCordinatesDimRow, matrixCordinatesDimCol, 2])

#after how many nodes is possible to empty the nodes array? this should be the double of the nodes that fits in one row of basestations
afterNodes = 100000 #50000 #20000 #15000

#packets parameters
ssff = 7
ccrr = 1
bbww = 125

eta = 2.9
fading = 7

#values for the RSSI of each packet
gamma = eta if eta > 0 else 2.08
d0 = 40  # 53 #40.0
var = fading if fading > 0 else 0
Lpld0 = -52  # Ptx-127.41 #-70.6 #-52 #127.41
GL = 0

#sensitivity matrix
sf7 = np.array([7, -124.0, -122.0, -116.0])
sf8 = np.array([8, -127.0, -125.0, -119.0])
sf9 = np.array([9, -130.0, -128.0, -122.0])
sf10 = np.array([10, -133.0, -130.0, -125.0])
sf11 = np.array([11, -135.0, -132.0, -128.0])
sf12 = np.array([12, -137.0, -135.0, -129.0])
sensi = np.array([sf7, sf8, sf9, sf10, sf11, sf12])

#AF_COMMENTS calculate the distances at which the gateways can listen the nodes with the minimun (7) and the maximum (12) spreading factors
all_Dist = []
all_minsensi = []
for ii in range(0, 6):
    minsensi_temp = sensi[ii, 1]  # 5th row is SF12, 2nd column is BW125
    all_minsensi.append(minsensi_temp)
    Lpl_temp = minsensi_temp
    all_Dist.append(round(d0 / (10.0**((Lpl_temp-Lpld0)/(10.0*gamma))), 2))
print(all_Dist)





# prepare graphics and add sink
if (graphics == 1):
    plt.ion()
    plt.figure()
    ax = plt.gcf().gca()
    # ax.add_patch(Rectangle((0, 0), maxX, maxY, fill=None, alpha=1))

#AF_COMMENTS populate the array with all the base station
for i in range(0, nrBS):
    b = myBS(i)
    bs.append(b)
    
#AF_COMMENTS before to tun the ADR algorithm store base stations in a file with the format of the basestation structure   ROW: || X | Y | ID ||
with open('simulation_files/' + str(nrBS) + '-basestation-BwGw-' + str(int(distanceBetweenGW)) + '-BwGN-' + str(maxDist) + '-mygen.txt', 'w') as bfile:
    for basestation in bs:
        bfile.write('{x} {y} {id}\n'.format(**vars(basestation)))


#create the nodes without usigng a buffer but directly write on a file and speed up the creation process
flag_alternation = False
with open('simulation_files/' + str(nrNodes) + '-nodes-raw-BwGw-' + str(int(distanceBetweenGW)) + '-BwGN-' + str(maxDist) + '-mygen.txt', 'w') as nfile:
    for i in range(0, nrNodes):

        #create the node in the space
        node = myNode(i, 0, 0)

        '''AF_ADD '''
        if(i<1000 and i%100==0):
            print("Node " + str(i) + " created")
        elif(i<10000 and i%1000==0):
            print("Node " + str(i) + " created")
        elif(i%10000==0):
            print("Node " + str(i) + " created")

        nodes.append((node.x, node.y))

        #After a nuber of nodes, is possible to delete the initial ones becasue not usefull in the computation, in this way the algorithm that check for place the nodes should not check ALL the nodes
        #This is not correct after a check, the nodes are spowned one for each basestation, so the only way to full exploit the maximization of the distance between nodes is to take into account all the nodes
        #An alternative could be to change the spown order, so that the first assumption will be true and is possible to delete the nodes going over in the spown
        '''So for now just take in memory all the nodes positions 
        if(len(nodes)%afterNodes==0):
            nodes = nodes[int(afterNodes/2)::]
        '''
        #wtite the node on a file
        nfile.write("{} {} {}".format(node.id, node.x, node.y))
        for base in range(0, nrBS):
            nfile.write(" {} {}".format(
                node.packet[base].rssi, node.packet[base].sf))
        nfile.write("\n")
            

#graphic
if (graphics == 1):
    plt.xlim([-7000, plot_xmax + 1000])
    plt.ylim([-7000, plot_ymax + 1000])
    plt.draw()
    plt.show()
    input('Press Enter to continue ...')