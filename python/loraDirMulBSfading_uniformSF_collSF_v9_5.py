#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
 LoRaSim: simulate collisions in LoRa - multiple base stations variant
 Copyright © 2016 Thiemo Voigt <thiemo@sics.se> and Martin Bor <m.bor@lancaster.ac.uk>

 This work is licensed under the Creative Commons Attribution 4.0
 International License. To view a copy of this license,
 visit http://creativecommons.org/licenses/by/4.0/.

 Do LoRa Low-Power Wide-Area Networks Scale? Martin Bor, Utz Roedig, Thiemo Voigt
 and Juan Alonso, MSWiM '16, http://dx.doi.org/10.1145/2988287.2989163

 $Date: 2016-10-17 13:23:52 +0100 (Mon, 17 Oct 2016) $
 $Revision: 218 $
"""

# loraDirMulBSfading_uniformSF_collSF.py

"""
 SYNOPSIS:
   ./loraDirMulBS.py <nodes> <avgsend> <experiment> <simtime> <basestation> [collision] [interfSF] [fading] [SF CR BW] [gamma]
 DESCRIPTION:
	nodes
		number of nodes to simulate
	avgsend
		average sending interval in milliseconds
"""


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
from explora_at_functionsMulBS_v9_5 import explora_at_self_multi_dim
'''AF_ADD '''
from py4j.java_gateway import JavaGateway
from node_clustering_on_position import node_clustering_on_position
import ast

#AF_COMMENTS 1=enable the spawn of the graphics 0=not
graphics = 0

# do the full collision check
full_collision = False
interfSF = False

# experiments:
# 0: packet with longest airtime, aloha-style experiment
# 0: one with 3 frequencies, 1 with 1 frequency
# 2: with shortest packets, still aloha-style
# 3: with shortest possible packets depending on distance

fading = 0
sqrt2 = math.sqrt(2)
ssff = 0
ccrr = 0
bbww = 0
eta = 0


#
# check for collisions at base station
# Note: called before a packet (or rather node) is inserted into the list
#
# conditions for collions:
#     1. same sf
#     2. frequency, see function below (Martins email, not implementet yet):
def checkcollision(packet):
    col = 0  # flag needed since there might be several collisions for packet
    # lost packets don't collide
    packet.faded = packet.Pout > random.random()
    if packet.lost or packet.faded:
        return 0
    if packetsAtBS[packet.bs][packet.sf - 6]:
        for i in range(7):
            for other in packetsAtBS[packet.bs][i]:  # [packet.sf - 6]:
                if other.id != packet.nodeid:
                    # simple collision
                    if frequencyCollision(packet, other.packet[packet.bs]):
                        if interfSF or sfCollision(packet, other.packet[packet.bs]):
                            if full_collision:
                                # timingCollision(packet, other.packet[packet.bs]):
                                if True:
                                    # check who collides in the power domain
                                    if sfCollision(packet, other.packet[packet.bs]):
                                        c = powerCollision(
                                            packet, other.packet[packet.bs])
                                    else:
                                        c = interSFpowerCollision(
                                            packet, other.packet[packet.bs])
                                    # mark all the collided packets
                                    # either this one, the other one, or both
                                    if c != None:
                                        for p in c:
                                            p.collided = 1
                                            if p == packet:
                                                col = 1
                                else:
                                    # no timing collision, all fine
                                    pass
                            else:
                                packet.collided = 1
                                # other also got lost, if it wasn't lost already
                                other.packet[packet.bs].collided = 1
                                col = 1
        return col
    return 0

#
# frequencyCollision, conditions
#
#        |f1-f2| <= 120 kHz if f1 or f2 has bw 500
#        |f1-f2| <= 60 kHz if f1 or f2 has bw 250
#        |f1-f2| <= 30 kHz if f1 or f2 has bw 125


def frequencyCollision(p1, p2):
    if (abs(p1.freq-p2.freq) <= 120 and (p1.bw == 500 or p2.freq == 500)):
        return True
    elif (abs(p1.freq-p2.freq) <= 60 and (p1.bw == 250 or p2.freq == 250)):
        return True
    else:
        if (abs(p1.freq-p2.freq) <= 30):
            return True
    return False


def sfCollision(p1, p2):
    if p1.sf == p2.sf:
        # p2 may have been lost too, will be marked by other checks
        return True
    return False


def powerCollision(p1, p2):
    # powerThreshold = 1.0 # dB
    # probabilityThr = 1.1
    # #    print "pwr: node {0.nodeid} SF{0.sf} {0.rssi:3.2f} dBm node {1.nodeid} SF{1.sf} {1.rssi:3.2f} dBm; diff {2:3.2f} dBm".format(p1, p2, round(p1.rssi - p2.rssi,2))
    # print "pwr: pkt {0.seqNr} SF{0.sf} {0.rssi:3.2f} dBm pkt {1.seqNr} SF{1.sf} {1.rssi:3.2f} dBm; diff {2:3.2f} dBm".format(p1, p2, round(p1.rssi - p2.rssi,2))
    # if abs(p1.rssi - p2.rssi) < powerThreshold:
    #     print("collision pwr both node {} and node {}".format(p1.nodeid, p2.nodeid))
    #     # packets are too close to each other, both collide
    #     # return both packets as casualties
    #     return (p1, p2)
    # elif p1.rssi - p2.rssi < powerThreshold:
    #     # p2 overpowered p1, return p1 as casualty
    #     print("p1 lost, p2 wins")
    #     if random.random() > probabilityThr:
    #         return (p1, p2)
    #     else:
    #         return (p1,)
    # # p2 was the weaker packet, return it as a casualty
    # if random.random() > probabilityThr:
    #     return (p1, p2)
    # else:
    #     print("p1 wins, p2 lost")
    #     return (p2,)

    powerThreshold_1 = 1.0  # 1.0 # dB
    powerThreshold_2 = 3.0  # 1.0 # dB
    powerThreshold_3 = 6.0  # 1.0 # dB
    '''AF_MODIFY delete the print for a faster execution in case of huge number of nodes
    print("pwr: pkt {0.seqNr} SF{0.sf} {0.rssi:3.2f} dBm pkt {1.seqNr} SF{1.sf} {1.rssi:3.2f} dBm; diff {2:3.2f} dBm".format(
        p1, p2, round(p1.rssi - p2.rssi, 2)))
    '''
    if abs(p1.rssi - p2.rssi) < powerThreshold_1:
        
        '''AF_MODIFY delete the print for a faster execution in case of huge number of nodes
        print("collision pwr both node {} and node {}".format(p1.nodeid, p2.nodeid))
        '''
        # packets are too close to each other, both collide
        # return both packets as casualties
        return (p1, p2)

    if abs(p1.rssi - p2.rssi) < powerThreshold_2:
        probabilityThr = 0.55
    elif abs(p1.rssi - p2.rssi) < powerThreshold_3:
        probabilityThr = 0.75
    else:
        probabilityThr = 1.1

    if p1.rssi - p2.rssi < 0:
        # p2 overpowered p1, return p1 as casualty
        '''AF_MODIFY delete the print for a faster execution in case of huge number of nodes
        print("p1 lost, p2 wins")
        '''
        if random.random() > probabilityThr:
            return (p1, p2)
        else:
            return (p1,)

    # p2 was the weaker packet, return it as a casualty
    if random.random() > probabilityThr:
        return (p1, p2)
    else:
        '''AF_MODIFY delete the print for a faster execution in case of huge number of nodes
        print("p1 wins, p2 lost")
        '''
        return (p2,)


def interSFpowerCollision(p1, p2):

    powerThreshold = 16.0  # 20.0 # 16.0 dB
    # tableThreshold = [  [0.9,	6.2,	7.8,	8.8,	9.4,	11.9],
    #                     [9.7,	0.5,	9.2,	10.9,	11.8,	12.4],
    #                     [13.8,	12.6,	0.1,	12.2,	13.9,	14.8],
    #                     [16.6,	16.7,	15.5,	0.2,	15.2,	17.0],
    #                     [19.2,	19.6,	19.7,	18.4,	0.3,	18.3],
    #                     [21.8,	22.1,	22.4,	22.6,	21.5,	0.4]]
    # # powerThreshold = tableThreshold[p2.sf-7][p1.sf-7]
    # powerThreshold = tableThreshold[p1.sf-7][p2.sf-7]

    # tableThreshold = [[0,	7.95,	10.8,	12.7,	14.3,	16.85],
    #                     [7.95,	0,	10.9,	13.8,	15.7,	17.25],
    #                     [10.8,	10.9,	0,	13.85,	16.8,	18.6],
    #                     [12.7,	13.8,	13.85,	0,	16.8,	19.8],
    #                     [14.3,	15.7,	16.8,	16.8,	0,	19.9],
    #                     [16.85,	17.25,	18.6,	19.8,	19.9,	0,]]
    # # powerThreshold = tableThreshold[p2.sf-7][p1.sf-7]
    # powerThreshold = tableThreshold[p1.sf-7][p2.sf-7]

    print("interSFpwr: pkt {0.seqNr} SF{0.sf} {0.rssi:3.2f} dBm pkt {1.seqNr} SF{1.sf} {1.rssi:3.2f} dBm; diff {2:3.2f} dBm".format(
        p1, p2, round(p1.rssi - p2.rssi, 2)))
    #    print "interSFpwr: node {0.nodeid} SF{0.sf} {0.rssi:3.2f} dBm node {1.nodeid} SF{1.sf} {1.rssi:3.2f} dBm; diff {2:3.2f} dBm".format(p1, p2, round(p1.rssi - p2.rssi,2))
    if abs(p1.rssi - p2.rssi) < powerThreshold:
        print("collision pwr None")
        # packets are too close to each other, none collide
        return None
    elif p1.rssi - p2.rssi < powerThreshold:
        # p2 overpowered p1, return p1 as casualty
        print("p1 lost, p2 wins")
        return (p1,)
    # p2 was the weaker packet, return it as a casualty
    print("p1 wins, p2 lost")
    return (p2,)


def timingCollision(p1, p2):
    # assuming p1 is the freshly arrived packet and this is the last check
    # we've already determined that p1 is a weak packet, so the only
    # way we can win is by being late enough (only the first n - 5 preamble symbols overlap)

    # assuming 8 preamble symbols
    Npream = 8

    # we can lose at most (Npream - 5) * Tsym of our preamble
    Tpreamb = 2**p1.sf/(1.0*p1.bw) * (Npream - 5)

    # check whether p2 ends in p1's critical section
    p2_end = p2.addTime + p2.rectime
    p1_cs = env.now + Tpreamb
    if p1_cs < p2_end:
        # p1 collided with p2 and lost
        return True
    return False

# this function computes the airtime of a packet
# according to LoraDesignGuide_STD.pdf
#


def airtime(sf, cr, pl, bw):
    '''
    n_ph=12.0;
    Ts=(2.0**sf)/bw;
    return n_ph*Ts + pl*8.0/sf*Ts/4.0*(cr+4);

    '''
    H = 0        # implicit header disabled (H=0) or not (H=1)
    DE = 0       # low data rate optimization enabled (=1) or not (=0)
    Npream = 8   # number of preamble symbol (12.25  from Utz paper)

    if bw == 125 and sf in [11, 12]:
        # low data rate optimization mandated for BW125 with SF11 and SF12
        DE = 1
    if sf == 6:
        # can only have implicit header with SF6
        H = 1

    Tsym = (2.0**sf)/bw
    Tpream = (Npream + 4.25)*Tsym
    # print "sf", sf, " cr", cr, "pl", pl, "bw", bw
    payloadSymbNB = 8 + \
        max(math.ceil((8.0*pl-4.0*sf+28+16-20*H)/(4.0*(sf-2*DE)))*(cr+4), 0)
    Tpayload = payloadSymbNB * Tsym
    return Tpream + Tpayload
#    '''


# this function update the SF for all the nodes,
# according with a specific ADR type
#
def run_ADR(nodes, sensi):
    global experiment
    global mat_rssi
    global SF_adr
    global all_rect_time
    global SF_input

    global nrBS
    global nrNodes
    global d0
    global var
    global Lpld0
    global gamma

    global fixed_sf7_ortho_percent
    global distanceBetweenGW
    
        
    global matrixCordinatesDimRow
    global matrixCordinatesDimCol

    '''AF_ADD '''
    global javaEXPLoRaCDdivision
    global javaEXPLoRaCDdivision_x
    global javaEXPLoRaCDdivision_y

    # Process ADR EXPLoRa --> EXPLoRa-SF
    print(SF_input)
    print("test0")
    if experiment == 6:

        count_special = 0
        SF_adr = np.full((nrNodes, 1), 12)
        SF_local = np.full((nrNodes, 1), 0)

        #AF_COMMENTS check the SF_input parameter taken as input to understand what ADR algorithm run     
        if SF_input == 13 or SF_input == 31:
            # if SF_input == 31:
            if nrBS == 1 or nrBS == 3:
                for ii in range(nrBS):
                    print("RAND-AT on BS : " + str(ii))
                    SF_local = explora_at_self_multi_dim(
                        mat_rssi, SF_local, nrBS, ii, nrNodes, SF_input, distanceBetweenGW, torreCanavese)
            else:
                if SF_input == 13:
                    SF_local = explora_at_self_multi_dim(
                        mat_rssi, SF_local, nrBS, 0, nrNodes, SF_input, distanceBetweenGW, torreCanavese)
                else:
                    for ii in range(nrBS):
                        print("RAND-AT on BS : " + str(ii))
                        SF_local = explora_at_self_multi_dim(
                            mat_rssi, SF_local, nrBS, ii, nrNodes, SF_input, distanceBetweenGW, torreCanavese)

            for ii in range(0, nrNodes):
                SF_adr[ii] = SF_local[ii]

        # elif SF_input == 13 :        #13 --> SF = random(7,12)
        #     # for ii in range(0, nrNodes):
        #     #     SF_adr[ii] = random.randint(7, 12)
        #     if not nodes_file:
        #         for ii in range(0, nrNodes):
        #             SF_adr[ii] = random.randint(7, 12)
        #     else:
        #         with open(nodes_file, 'r') as nfile:
        #             for ii in range(0, nrNodes):
        #                 line = nfile.readline()
        #                 print(line)
        #                 sfCurrent = float(line.strip().split(' ')[4])
        #                 print(sfCurrent)
        #                 SF_adr[ii] = sfCurrent #random.randint(7, 12)

        #AF_COMMENTS note the usefull values of SF_input to run the algorithms designed, it is passed to the function explora_at_self_multi_dim() 
        #AF_COMMENTS to make understand the algorithm to use from the other file
        # 20 --> EXPLoRa-AT # 22 --> EXPLoRa random position #27 --> EXPLoRa-C
        elif SF_input == 20 or SF_input == 22 or SF_input == 27 or SF_input == 34:
            print("************************************************************************EXPLoRa-C*************************************************************************************")
            print("************************************************************************EXPLoRa-C*************************************************************************************")
            print("************************************************************************EXPLoRa-C*************************************************************************************")
            print("************************************************************************EXPLoRa-C*************************************************************************************")

            #AF_COMMENTS check the parametere as input of this function, that are the parameters used for EXPLoRa-C algorithm
            #AF_COMMENTS || mat_rssi=empty not used but calculated in the other file || nrBS=number of base station || nrNodes=number of nodes || SF_input=ADR algorithm code || distanceBetweenGW ||
            #AF_COMMENTS || SF_local=ordered array of all the spreading factors assigned to all the nodes ||
            ''' AF_ADD 
            print("Before", SF_local)
            '''
            '''AF_MODIFY '''
            #AF_COMMENTS check if run the pyton version of explora or the java one, (the java one is only EXPLoRa-C, execution with no division per gateways)
            if javaPythonVersion == "python" or javaPythonVersion == None:
                print("EXECUTING PYTHON VERSION OF EXPLORA-C")
                if nrBS == 1:  # or nrBS == 3:
                    SF_local = explora_at_self_multi_dim(
                        mat_rssi, SF_local, nrBS, 0, nrNodes, SF_input, distanceBetweenGW, torreCanavese)
                else:
                    for ii in range(nrBS):
                        print("EXPLORA-C on BS : " + str(ii))
                        SF_local = explora_at_self_multi_dim(
                            mat_rssi, SF_local, nrBS, ii, nrNodes, SF_input, distanceBetweenGW, torreCanavese)
            elif javaPythonVersion == "java-start":
                print("EXECUTING JAVA VERSION OF EXPLORA-C")
                gateway = JavaGateway()
                resultingSFs = gateway.entry_point.EXPLoRa_C_py(nrNodes)
                for i in range(SF_local.size):
                    SF_local[i][0] = resultingSFs[i]
            elif javaPythonVersion == "java":
                print("EXECUTING JAVA FUNCTIONAL VERSION OF EXPLORA-C")
                gateway = JavaGateway()
                resultingSFs = gateway.entry_point.EXPLoRa_C_py_functional(nrNodes)
                for i in range(SF_local.size):
                    SF_local[i][0] = resultingSFs[i]
            elif javaPythonVersion == "java-cd-m1":
                print("EXECUTING JAVA VERSION OF EXPLORA-CD USING SPLIT MODE 1")
                gateway = JavaGateway()
                resultingSFs = gateway.entry_point.EXPLoRa_CD_py(nrNodes, nrBS, matrixCordinatesDimRow, matrixCordinatesDimCol, javaEXPLoRaCDdivision)
                for i in range(SF_local.size):
                    SF_local[i][0] = resultingSFs[i]
            elif javaPythonVersion == "java-cd-m2":
                print("EXECUTING JAVA VERSION OF EXPLORA-CD USING SPLIT MODE 2")
                gateway = JavaGateway()
                node_clustering_on_position(nrNodes, nrBS,distanceBetweenGW, javaEXPLoRaCDdivision_x, javaEXPLoRaCDdivision_y, False)
                resultingSFs = gateway.entry_point.EXPLoRa_CD_geoDivision_py(nrNodes, (javaEXPLoRaCDdivision_x*javaEXPLoRaCDdivision_y))
                for i in range(SF_local.size):
                    SF_local[i][0] = resultingSFs[i]
            elif javaPythonVersion == "java-cd-m2-splitVision":
                print("EXECUTING JAVA VERSION OF EXPLORA-CD USING SPLIT MODE 2 AND A SPLITTED VISION")
                gateway = JavaGateway()
                node_clustering_on_position(nrNodes, nrBS,distanceBetweenGW, javaEXPLoRaCDdivision_x, javaEXPLoRaCDdivision_y, False)
                resultingSFs = gateway.entry_point.EXPLoRa_CD_geoDivision_splitVision_py(nrNodes, nrBS, (javaEXPLoRaCDdivision_x*javaEXPLoRaCDdivision_y))
                for i in range(SF_local.size):
                    SF_local[i][0] = resultingSFs[i]
            else:
                print("EXECUTING JAVA VERSION OF EXPLORA-CD USING SPLIT MODE 1 AND A SPLITTED VISION")
                gateway = JavaGateway()
                resultingSFs = gateway.entry_point.EXPLoRa_CD_splitVision_py(nrNodes, nrBS, matrixCordinatesDimRow, matrixCordinatesDimCol, javaEXPLoRaCDdivision, -123.0 , "min")
                for i in range(SF_local.size):
                    SF_local[i][0] = resultingSFs[i]

            print(SF_local.shape)
            #print("After", SF_local)
            
            #AF_COMMENTS copy the array of all the assigned spreading factor into SF_adr
            for ii in range(0, nrNodes):
                SF_adr[ii] = SF_local[ii]
            
            print("************************************************************************EXPLoRa-C*************************************************************************************")
            print("************************************************************************EXPLoRa-C*************************************************************************************")
            print("************************************************************************EXPLoRa-C*************************************************************************************")
            print("************************************************************************EXPLoRa-C*************************************************************************************")

        elif SF_input == 28 or SF_input == 29 or SF_input == 30:

            if nrBS == 1:
                SF_local = explora_at_self(
                    mat_rssi, SF_local, nrBS, 0, nrNodes, SF_input)
            elif nrBS == 3:

                SF_local = explora_at_self_multi_dim(
                    mat_rssi, SF_local, nrBS, SF_input-28, nrNodes, SF_input, distanceBetweenGW, torreCanavese)
            else:
                SF_local = explora_at_self_multi_dim(
                    mat_rssi, SF_local, nrBS, 12, nrNodes, SF_input, distanceBetweenGW, torreCanavese)

            for ii in range(0, nrNodes):
                SF_adr[ii] = SF_local[ii]

        elif SF_input == 32:
            adrIndex = 0
            for node in nodes:
                SF_adr[adrIndex] = node.packet[0].externADR
                adrIndex += 1

        elif SF_input == 33:

            # SF_perc = np.array([0.47004852, 0.25854953, 0.14357661, 0.07176894, 0.03588447, 0.02017192])
            # # set group nodes number
            # SF_group = SF_perc * nrNodes
            # # init array with final nodes number group
            # SF_group_int = np.empty(shape=[0, 1])
            # SF_group_int_progressive = np.empty(shape=[0, 1])
            # consumedNodeNumber = 0
            # # set SF_group_int and SF_group_delimiter: they are the theorical delimiter for the nodes
            # for indexGroup in range(len(SF_group)):
            #     if indexGroup < len(SF_group) - 1:
            #         # print(int(SF_group[indexGroup]))
            #         SF_group_int = np.append(SF_group_int, round(SF_group[indexGroup]))
            #         consumedNodeNumber += round(SF_group[indexGroup])
            #         SF_group_int_progressive = np.append(SF_group_int_progressive, consumedNodeNumber)
            #
            #     else:
            #         SF_group_int = np.append(SF_group_int, [nrNodes - consumedNodeNumber], axis=0)
            #         SF_group_int_progressive = np.append(SF_group_int_progressive, nrNodes)

            adrIndex = 0
            indexSF = 0
            for node in nodes:
                # currentClusterSF = clusterMap[int(xyz[self.nodeid, 4])]

                SF_adr[adrIndex] = node.packet[0].externAdrCluster

                # allocatedSFCount[indexSF] += 1
                # if allocatedSFCount[indexSF] >= SF_group_int[indexSF]:
                adrIndex += 1

        else:
            print("ERROR! ADR not supported\n")
            input('Press Enter to continue ...')

        if graphics:
            nodeid = 0
            for node in nodes:
                sys.stdout.write(str(nodeid) + ":" + str(SF_adr[nodeid]) + " ")
                nodeid += 1
            print()
            input('Press Enter to continue ...')

        #AF_COMMENTS after the ADR algorithm is needed a cycle to adjust all the nodes objects
        nodeid = 0
        for node in nodes:
            # print(nodeid, "  -  ", SF_adr[nodeid])
            # print('After ADR - node %d' % node.id, "x", node.x, "y", node.y, "dist: ", node.dist)

            check_out_coverage = True
            count_one_coverage = 0
            for bs in range(0, nrBS):
                #AF_COMMENTS reset some parameters like the rate and the band for all the packets for each base station
                node.packet[bs].cr = 1
                node.packet[bs].bw = 125

                #AF_COMMENTS set all the new spreding factors calculated by the ADR algorithm and in the same order of the starting nodes
                node.packet[bs].sf = int(SF_adr[nodeid])
                node.packet[bs].symTime = (
                    2.0 ** node.packet[bs].sf) / node.packet[bs].bw
                node.packet[bs].arriveTime = 0

                # log-shadow
                #        Lpl = Lpld0 + 10*gamma*math.log(distance/d0)
                # Lpl = Lpld0 + 10*gamma*math.log10(distance/d0)
                # print Lpl
                # Prx = Ptx - GL - Lpl

                if not torreCanavese:
                    Prx = Lpld0 + 10 * gamma * math.log10(d0 / node.dist[bs])

                if torreCanavese:
                    Prx = xyz[node.id, 0]  # SNR

                node.packet[bs].rssi = Prx

                # frequencies: lower bound + number of 61 Hz steps
                node.packet[bs].freq = 860000000 + random.randint(0, 2622950)

                # for certain experiments override these and
                # choose some random frequences
                # DG2018 !!!!! setted according with EXPLoRa simulator
                # if node.packet.sf == 12 and node.packet.bw == 125:
                if experiment == 1:
                    node.packet[bs].freq = random.choice(
                        [860000000, 864000000, 868000000])
                else:
                    node.packet[bs].freq = 860000000

                node.packet[bs].rectime = airtime(
                    node.packet[bs].sf, node.packet[bs].cr, node.packet[bs].pl, node.packet[bs].bw)
                # all_rect_time.append(self.rectime)
                # denote if packet is collided
                node.packet[bs].collided = 0
                node.packet[bs].processed = 0
                node.packet[bs].faded = 0

                # mark the packet as lost when it's rssi is below the sensitivity
                row = np.argwhere(sensi == node.packet[bs].sf)
                if node.packet[bs].bw == 125 or node.packet[bs].bw == 250:
                    sf_bs_minsensi = sensi[row[0, 0],
                                           int(node.packet[bs].bw / 125)]
                elif node.packet[bs].bw == 500:
                    sf_bs_minsensi = sensi[row[0, 0], 3]

                # print(node.packet[bs].rssi)
                # print(sf_bs_minsensi)
                node.packet[bs].lost = node.packet[bs].rssi < sf_bs_minsensi
                '''AF_MODIFY delete the print of the packets loss or delivered becasue infinite with huge number of nodes
                print("node {} sf {} bs {} lost {}".format(
                    node.packet[bs].nodeid, node.packet[bs].sf, node.packet[bs].bs, node.packet[bs].lost))
                '''

                if node.packet[bs].lost == False:
                    check_out_coverage = False
                else:
                    count_one_coverage += 1

                if var > 0:
                    if node.packet[bs].lost == 0:
                        node.packet[bs].Pout = 0.5 * math.erfc(
                            (node.packet[bs].rssi - sf_bs_minsensi) / (sqrt2 * var))
                        # if bs==0:
                        #     print(node.id)
                        #     print(node.packet[bs].rssi)
                        #     print(node.packet[bs].Pout)

                    else:
                        node.packet[bs].Pout = 1
                else:
                    node.packet[bs].Pout = 0
                    # print "Pout {}".format(self.Pout)

            if check_out_coverage:
                print("ERROR: packet not covered")
                if not torreCanavese:
                    input('Press Enter to continue ...')

            if count_one_coverage == 2:
                count_special += 1
                node.ortho = 1
                # print("count special" + str(count_special))
                # input('Press Enter to continue ...')

            nodeid += 1


# 7276FF002E061431;Camilluccia-01;Kerlink V2;Omni 3dB;Omni 3dB;NULL;NULL;Unidata S.p.a.;Lazio;Via Casali di Santo Spirito, 00135 Roma RM, Italy;41.94322;12.45182;133 m;NULL;Area Urbana
# 7276FF002E061437;Montesacro-01;Kerlink V2;Omni 3dB;Omni 3dB;NULL;NULL;Roberto Monaldi;Lazio;Via Rodolfo Valentino, 29, 00139 Roma RM, Italy;41.95594;12.53434;88 m;NULL;Area Urbana
# 70B3D54B12020000;Montemario-02;;Kerlink V2;NULL;NULL;NULL;NULL;NULL;Lazio;Via Romeo Romei, 35, 00136 Roma RM, Italy;41.91739;12.45055;85 m;NULL;NULL
# 7276FF002E0613C7;CastroPretorio-01;Kerlink V2;Omni 8dB;Omni 8dB;NULL;NULL;Unidata S.p.a.;Lazio;Via S. Martino della Battaglia, 00185 Roma RM, Italy;41.90577;12.50523;99 m;NULL;Area Urbana
# 70B3D54B124D0000;Marconi-01;Kerlink V2;Omni 8dB;NULL;NULL;NULL;Stefano Grossi - Fast Impianti;Lazio;Via dei Prati dei Papa;41.86712;12.46728;72 m;NULL;Area Urbana

# 7276FF002E061431;Camilluccia-01;41.94322;12.45182;
# 7276FF002E061437;Montesacro-01;41.95594;12.53434;
# 70B3D54B12020000;Montemario-02;41.91739;12.45055;
# 7276FF002E0613C7;CastroPretorio-01;41.90577;12.50523;
# 70B3D54B124D0000;Marconi-01;41.86712;12.46728;
BSinfo_1 = np.array(["7276FF002E061431", "Camilluccia-01", 41.94322, 12.45182])
BSinfo_2 = np.array(["7276FF002E061437", "Montesacro-01", 41.95594, 12.53434])
BSinfo_3 = np.array(["70B3D54B12020000", "Montemario-02", 41.91739, 12.45055])
BSinfo_4 = np.array(["7276FF002E0613C7", "CastroPretorio-01", 41.90577, 12.50523])
BSinfo_5 = np.array(["70B3D54B124D0000", "Marconi-01", 41.86712, 12.46728])


# BSinfo_6 = np.array(["0000000000000000", "gateway1", 41.94322, 12.45182])
# BSinfo_7 = np.array(["0000000000000000", "gateway2", 41.52427, 12.36309])
# BSinfo_8 = np.array(["0000000000000000", "gateway3", 41.81079, 12.45833])

# 70B3D54B13020000, 42.572, 12.635
# 7276FF002E06143C, 41.932, 12.634
# 1C497BEFFECAB36D, 41.804, 12.33

# BSinfo = np.array([ BSinfo_1, BSinfo_2, BSinfo_3, BSinfo_4, BSinfo_5])
BSinfo = np.array([BSinfo_3, BSinfo_4, BSinfo_5, BSinfo_1, BSinfo_2])
# BSinfo = np.array([ BSinfo_6, BSinfo_7, BSinfo_8])


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

            # # coordnatesMatrixGW creation
            # baseCoordinatesY = Y
            # baseCoordinatesX = X
            # matrixCordinatesGW[0, 0, 0] = baseCoordinatesX
            # matrixCordinatesGW[0, 0, 1] = baseCoordinatesY
            #
            # matrixCordinatesGW[0, 1, 0] = baseCoordinatesX - 12000
            # matrixCordinatesGW[0, 1, 1] = baseCoordinatesY - 12000
            # matrixCordinatesGW[0, 2, 0] = baseCoordinatesX - 12000
            # matrixCordinatesGW[0, 2, 1] = baseCoordinatesY + 12000
            # matrixCordinatesGW[0, 3, 0] = baseCoordinatesX + 12000
            # matrixCordinatesGW[0, 3, 1] = baseCoordinatesY - 12000
            # matrixCordinatesGW[0, 4, 0] = baseCoordinatesX + 12000
            # matrixCordinatesGW[0, 4, 1] = baseCoordinatesY + 12000
            #
            # matrixCordinatesGW[0, 5, 0] = baseCoordinatesY - 0
            # matrixCordinatesGW[0, 5, 1] = baseCoordinatesX - 24000
            # matrixCordinatesGW[0, 6, 0] = baseCoordinatesY + 0
            # matrixCordinatesGW[0, 6, 1] = baseCoordinatesX + 24000
            # matrixCordinatesGW[0, 7, 0] = baseCoordinatesY - 24000
            # matrixCordinatesGW[0, 7, 1] = baseCoordinatesX + 0
            # matrixCordinatesGW[0, 8, 0] = baseCoordinatesY + 24000
            # matrixCordinatesGW[0, 8, 1] = baseCoordinatesY - 0
            #
            # # matrixCordinatesGW[0, 5, 0] = baseCoordinatesY - 12000
            # # matrixCordinatesGW[0, 5, 1] = baseCoordinatesX - 24000
            # # matrixCordinatesGW[0, 6, 0] = baseCoordinatesY - 24000
            # # matrixCordinatesGW[0, 6, 1] = baseCoordinatesX - 12000
            # # matrixCordinatesGW[0, 7, 0] = baseCoordinatesY + 12000
            # # matrixCordinatesGW[0, 7, 1] = baseCoordinatesX - 24000
            # # matrixCordinatesGW[0, 8, 0] = baseCoordinatesY + 24000
            # # matrixCordinatesGW[0, 8, 1] = baseCoordinatesY - 12000
            # # matrixCordinatesGW[0, 9, 0] = baseCoordinatesY + 12000
            # # matrixCordinatesGW[0, 9, 1] = baseCoordinatesX + 24000
            # # matrixCordinatesGW[0, 10, 0] = baseCoordinatesY + 24000
            # # matrixCordinatesGW[0, 10, 1] = baseCoordinatesX + 12000
            # # matrixCordinatesGW[0, 11, 0] = baseCoordinatesY - 12000
            # # matrixCordinatesGW[0, 11, 1] = baseCoordinatesX + 24000
            # # matrixCordinatesGW[0, 12, 0] = baseCoordinatesY - 24000
            # # matrixCordinatesGW[0, 12, 1] = baseCoordinatesY + 12000

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
            # XXX should be base station position
            '''AF_ADD ''' 
            plt.text(self.x, self.y, str(self.id), fontsize=12, color='red')
            ax.add_artist(plt.Circle((self.x, self.y),
                          600, fill=True, color='green'))
            ax.add_artist(plt.Circle((bsx, bsy), maxDist, fill=False, color='green'))
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
    def __init__(self, id, period, packetlen, xpos, ypos):
        global bs
        global nrBS
        global maxDist

        global mat_rssi
        global SF_vec

        global nodeAllocationCount
        global nodeAllocationArray

        self.id = id

        self.period = period

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

                if not torreCanavese:
                    b = random.random()
                else:
                    b = 0.5

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
                        dist = np.sqrt(((abs(n.x-posx))**2) +
                                       ((abs(n.y-posy))**2))
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

        rand_sf = 12
        currentArraySF = []
        for i in range(0, nrBS):
            d = np.sqrt((self.x-bs[i].x)*(self.x-bs[i].x) +
                        (self.y-bs[i].y)*(self.y-bs[i].y))
            self.dist.append(d)
            self.packet.append(
                myPacket(self.id, packetlen, self.dist[i], i, rand_sf))
            currentArraySF.append(rand_sf)
            # print("node {} sf {} bs {} lost {}".format(self.packet[i].nodeid, self.packet[i].sf, self.packet[i].bs, self.packet[i].lost))

        # print('node %d' %id, "x", self.x, "y", self.y, "dist: ", self.dist)
        # input("TEST")

        self.sent = 0
        self.collisions = 0
        self.lost = 0

        # graphics for node
        global graphics
        if (graphics == 1):
            global ax
            ax.add_artist(plt.Circle((self.x, self.y),
                          100, fill=True, color='blue'))
            ax.text(self.x, self.y, str(self.id), fontsize=10)

#
# this function creates a packet (associated with a node)
# it also sets all parameters, currently random
#


class myPacket():
    def __init__(self, nodeid, plen, distance, bs, rand_sf):
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
        if ssff == 0:
            # randomize configuration values
            self.sf = random.randint(6, 12)
            self.cr = random.randint(1, 4)
            self.bw = random.choice([125, 250, 500])

            # for certain experiments override these
            if experiment == 1 or experiment == 0:
                self.sf = 12
                self.cr = 4
                self.bw = 125

            # for certain experiments override these
            if experiment == 2:
                self.sf = 6
                self.cr = 1
                self.bw = 500

            # lorawan
            if experiment == 4:
                self.sf = 12
                self.cr = 1
                self.bw = 125
        else:
            self.sf = ssff
            self.cr = ccrr
            self.bw = bbww

        # for experiment 3 find the best setting
        # OBS, some hardcoded values
        Prx = Ptx  # zero path loss by default

        # log-shadow
        #        Lpl = Lpld0 + 10*gamma*math.log(distance/d0)
        # Lpl = Lpld0 + 10*gamma*math.log10(distance/d0)
        # print Lpl
        # Prx = Ptx - GL - Lpl
        if not torreCanavese:
            Prx = Lpld0 + 10*gamma*math.log10(d0/distance)

        if torreCanavese:
            Prx = xyz[self.nodeid, 0]  # SNR

        if (experiment == 3):
            minairtime = 9999
            minsf = 0
            minbw = 0

            for i in range(0, 6):
                for j in range(1, 4):
                    if (sensi[i, j] < Prx):
                        self.sf = sensi[i, 0]
                        if j == 1:
                            self.bw = 125
                        elif j == 2:
                            self.bw = 250
                        else:
                            self.bw = 500
                        at = airtime(self.sf, 4, 20, self.bw)
                        if at < minairtime:
                            minairtime = at
                            minsf = self.sf
                            minbw = self.bw

            self.rectime = minairtime
            self.sf = minsf
            self.bw = minbw
            if (minairtime == 9999):
                print("does not reach base station")
                exit(-1)

        # transmission range, needs update XXX
        self.transRange = 150
        self.pl = plen
        self.symTime = (2.0**self.sf)/self.bw
        self.arriveTime = 0
        #	self.seqNr = -1;
        self.rssi = Prx

        if torreCanavese:
            # SNR, ERROR_RATE, SF, RSSI, CLUSTER, DEV_EUI, PKT_NUM
            self.snr = xyz[self.nodeid, 0]
            self.rssis = xyz[self.nodeid, 3]
            self.devEui = deviceInfo[self.nodeid][5]
            self.externADR = int(xyz[self.nodeid, 2])
            self.externAdrCluster = clusterMap[int(xyz[self.nodeid, 4])]

        # frequencies: lower bound + number of 61 Hz steps
        #self.freq = 860000000 + random.randint(0,2622950)
        self.freq = 860000000

        # for certain experiments override these and
        # choose some random frequences
        if experiment == 1:
            self.freq = random.choice([860000000, 864000000, 868000000])
        else:
            self.freq = 860000000

        # if interfSF:
        #     self.sf = rand_sf

        self.rectime = airtime(self.sf, self.cr, self.pl, self.bw)
        # denote if packet is collided
        self.collided = 0
        self.processed = 0
        self.faded = 0
        # mark the packet as lost when it's rssi is below the sensitivity
        # don't do this for experiment 3, as it requires a bit more work
        if experiment != 3:
            global minsensi
            self.lost = self.rssi < minsensi
            # print "node {} bs {} lost {}".format(self.nodeid, self.bs, self.lost)
            if var > 0:
                if self.lost == 0:
                    self.Pout = 0.5*math.erfc((self.rssi-minsensi)/(sqrt2*var))
                else:
                    self.Pout = 1
            else:
                self.Pout = 0
            # print "Pout {}".format(self.Pout)


#
# main discrete event loop, runs for each node
# a global list of packet being processed at the gateway
# is maintained
#
#AF_COMMENTS no that all the calculations on the packet sent (loss, reach, RSSI, gateway, ..) are done in this function
def transmit(env, node):
    while True:
        #AF_COMMENTS this is like a wait so that a message will be transmitted only at specified amount of time, in particular in the parameter there is something like and Average of the period
        yield env.timeout(random.expovariate(1.0/float(node.period)))

        # time sending and receiving
        # packet arrives -> add to base station
        #        print "tstamp", env.now

        #AF_COMMENTS sum of the packets sent by just this node
        node.sent = node.sent + 1

        #AF_COMMENTS sum of the packets sent by all the nodes
        global packetSeq
        packetSeq = packetSeq + 1
        global pseq
        pseq[node.packet[0].sf - 6] = pseq[node.packet[0].sf - 6] + 1

        #AF_COMMENTS verify if the packets has reched all the gateways
        global nrBS
        for bs in range(0, nrBS):

            if (node in packetsAtBS[bs][node.packet[0].sf - 6]):
                print("ERROR: packet already in")
                input('Press Enter to continue ...')

            else:
                #AF_COMMENTS bring the packet in air for an amount of time to understand if it has collided with some other packets in air
                node.packet[bs].addTime = env.now
                node.packet[bs].seqNr = packetSeq
                packetsAtBS[bs][node.packet[bs].sf - 6].append(node)

                # print "Sent pkt {} with SF{}".format(node.packet[bs].seqNr, node.packet[bs].sf)

                #AF_COMMENTS check if the packet has collided in the same time it is started, if yes set the flag to 1, 0 otherwise
                if (checkcollision(node.packet[bs]) == 1):
                    node.packet[bs].collided = 1
                else:
                    node.packet[bs].collided = 0

        # take first packet rectime
        #AF_COMMENTS set a wait equal to the time on air of the packet so that later you can check if is has collided
        yield env.timeout(node.packet[0].rectime)

        # complete packet has been received by base station
        # can remove it
        for bs in range(0, nrBS):
            if (node in packetsAtBS[bs][node.packet[bs].sf - 6]):
                packetsAtBS[bs][node.packet[bs].sf - 6].remove(node)

        # if packet did not collide, add it in list of received packets
        # unless it is already in
        #AF_COMMENTS check if the packet is collided or is lost for the fading effect or is arrived at destination 
        collisionDetected = 0
        for bs in range(0, nrBS):
            if node.packet[bs].lost or node.packet[bs].faded:
                #[node.packet[bs].sf - 6].append(node.packet[bs].seqNr)
                lostPackets[node.packet[bs].sf -
                            6].append(node.packet[bs].seqNr)
                node.lost = node.lost + 1
            else:

                if node.packet[bs].collided == 0:

                    global nrReceived
                    nrReceived = nrReceived + 1  # it can not be considered with more bs

                    packetsRecBS[bs][node.packet[bs].sf -
                                     6].append(node.packet[bs].seqNr)

                    if (len(recPackets[node.packet[bs].sf - 6])):
                        if (recPackets[node.packet[bs].sf - 6][-1] != node.packet[bs].seqNr):
                            #recPackets[node.packet[bs].sf - 6].append(node.packet[bs].seqNr)
                            recPackets[node.packet[bs].sf -
                                       6].append(node.packet[bs].seqNr)
                    else:
                        #recPackets[node.packet[bs].sf - 6].append(node.packet[bs].seqNr)
                        recPackets[node.packet[bs].sf -
                                   6].append(node.packet[bs].seqNr)
                else:

                    if not collisionDetected:
                        global nrCollisions
                        nrCollisions = nrCollisions + 1
                        node.collisions = node.collisions + 1
                        collisionDetected = 1

                    # XXX only for debugging
                    #[node.packet[bs].sf - 6].append(node.packet[bs].seqNr)
                    # print "SFF:", node.packet[bs].sf, len(collidedPackets[node.packet[bs].sf - 6]), collidedPackets, node.packet[bs].seqNr
                    collidedPackets[node.packet[bs].sf -
                                    6].append(node.packet[bs].seqNr)
                #	for bs in range(0, nrBS):
                #		print "End pkt {} with SF{}".format(node.packet[bs].seqNr, node.packet[bs].sf)
                #        print "recpackets: ", [recPackets[j] for j in range(7)]
                #        print "collidedPackets: ", [collidedPackets[j] for j in range(7)]
                #        print "lostPackets: ", [lostPackets[j] for j in range(7)]
                #        print [packetsAtBS[bs][j] for j in range(7)]

        # complete packet has been received by base station
        # can remove it
        for bs in range(0, nrBS):
            # reset the packet
            node.packet[bs].collided = 0
            node.packet[bs].processed = 0

#                       **************************************************************************************************************************************************************************
# "main" program		**************************************************************************************************************************************************************************
#                       **************************************************************************************************************************************************************************


SF_input = 13
nodes_file = None
nrNodes = 0
fixed_sf7_ortho_percent = 1.0
distanceBetweenGW = 12000
nodeAllocationCount = 0
nodeAllocationArray = [0, 1, 2, 6, 7, 11]
torreCanavese = False
'''AF_ADD '''
javaPythonVersion = None
javaEXPLoRaCDdivision = 15
javaEXPLoRaCDdivision_x = 1
javaEXPLoRaCDdivision_y = 2

# get arguments
if len(sys.argv) >= 6:
    #AF_COMMENTS parameter number of nodes to spawn
    nrNodes = int(sys.argv[1])
    #AF_COMMENTS parameter time between messages for each node
    avgSendTime = int(sys.argv[2])
    #AF_COMMENTS parameter experiment to run
    experiment = int(sys.argv[3])
    #AF_COMMENTS parameter total time of the running experiment
    simtime = int(sys.argv[4])
    #AF_COMMENTS parameter number of base station to spawn
    nrBS = int(sys.argv[5])
    #AF_COMMENTS parameter flag to enable to allow the half of collision in the cases foreseen by the Capture effect, if not enabled count as collided both the packets
    if len(sys.argv) > 6:
        full_collision = bool(int(sys.argv[6]))
    #AF_COMMENTS parameter inter spreading factors interference, given that the SFs are not perfectly orthogonals, if enabled count the interference between SFs with SNR under a threshold
    if len(sys.argv) > 7:
        interfSF = bool(int(sys.argv[7]))
    #AF_COMMENTS parameter flag to enable to allow the fading effect (variable power signal at the same distance or at different distances)
    if len(sys.argv) > 8:
        fading = int(sys.argv[8])
    if len(sys.argv) > 9:
        #AF_COMMENTS parameter starter spreding factor of the devices
        ssff = int(sys.argv[9])
        #AF_COMMENTS parameter rate of the device
        ccrr = int(sys.argv[10])
        #AF_COMMENTS parameter bandwidth of the devices
        bbww = int(sys.argv[11])
    #AF_COMMENTS parameter exponent with which the power is attenuated, higher is the exponent, higher is the attenuation effect
    if len(sys.argv) > 12:
        eta = float(sys.argv[12])
    #AF_COMMENTS parameter that specify the ADR algorithm to run
    if len(sys.argv) > 13:
        SF_input = int(sys.argv[13])
    if len(sys.argv) > 14:
         #AF_COMMENTS parameter that specify the maximum distance at which the nodes can be placed far away from the base station at which they are assigned (the assignment is 1 node for each base station at iteration)
        max_dist_input = int(sys.argv[14])
         #AF_COMMENTS parameter that specify distance between the base stations
        distanceBetweenGW = float(sys.argv[15])
    if len(sys.argv) > 16:
        nodes_file = str(sys.argv[16])
        '''AF_MODIFY '''
        if(nodes_file == "None"): 
            nodes_file=None
    '''AF_ADD '''
    #AF_COMMENTS use "python" to run the professor code, use "java" to run my code in default (None) the python version is runned
    if len(sys.argv) > 17:
        javaPythonVersion = str(sys.argv[17])
    if len(sys.argv) > 18:
        javaEXPLoRaCDdivision = int(sys.argv[18])
    if len(sys.argv) > 19:
        javaEXPLoRaCDdivision_x = int(sys.argv[19])
    if len(sys.argv) > 20:
        javaEXPLoRaCDdivision_y = int(sys.argv[20])



    print("Nodes:", nrNodes)
    print("AvgSendTime (exp. distributed):", avgSendTime)
    print("Experiment: ", experiment)
    print("Simtime: ", simtime)
    print("nrBS: ", nrBS)

    '''AF_MODIFY
    if (nrBS > 36):
        print("too many base stations, max 36 base stations")
        exit(-1)
    '''

    print("Full Collision: ", full_collision)
    print("Non orthogonal SFs: ", interfSF)
    print("Fading: ", fading)
    print("eta: ", eta)
    '''AF_ADD '''
    print("Node file name", nodes_file)
    print("Java/Python version", javaPythonVersion)

else:
    print(
        "usage: ./loraDir nrNodes avgSendTime experimentNr simtime nrBS [full_collision] [interfSF] [fading] [SF CR BW] [gamma]")
    print("experiment 0 and 1 use 1 frequency only")
    exit(-1)


# this is an array with measured values for sensitivity
# see paper, Table 3
# sf7 = np.array([7,-126.5,-124.25,-120.75])
# sf8 = np.array([8,-127.25,-126.75,-124.0])
# sf9 = np.array([9,-131.25,-128.25,-127.5])
# sf10 = np.array([10,-132.75,-130.25,-128.75])
# sf11 = np.array([11,-134.5,-132.75,-128.75])
# sf12 = np.array([12,-133.25,-132.25,-132.25])

#AF_COMMENTS make attention that LoRa define the modulation of the signal, LoRaWAN tells "you can use these bandwidth"
#AF_COMMENTS the difference between different SFs is that the higher is the SF the robust it is, and a more robust SF can be demodulated with a lower signal noice ration
#               in this matrix are reported the threshold values of RSSI at which is possible to demodulate a signal coming with each spreding factor
#               is possible to see that with SF 12 is possible to demudulate signals with an RSSI lower than signal coming at SF 7
#               the three values refers to the different bandwidth, in particula are thresholds for band of 125 kHz, 250 kHz, 500 kHz
#               the most robust condition is at bandwidth 125 kHz and spreading factor 12 becasue is possible to demodulate a packet until -137 dBm of RSSI
#               so at SF 7 you can have more speed becasue the packets have lower life in the air
if not torreCanavese:
    sf7 = np.array([7, -124.0, -122.0, -116.0])
    sf8 = np.array([8, -127.0, -125.0, -119.0])
    sf9 = np.array([9, -130.0, -128.0, -122.0])
    sf10 = np.array([10, -133.0, -130.0, -125.0])
    sf11 = np.array([11, -135.0, -132.0, -128.0])
    sf12 = np.array([12, -137.0, -135.0, -129.0])
    sensi = np.array([sf7, sf8, sf9, sf10, sf11, sf12])

    clusterMap = [12, 12, 12, 12, 12, 12, 12, 12, 12]


# global stuff
nodes = []
#packetsAtBS = []
env = simpy.Environment()


mat_rssi = np.array([])

SF_adr = None
all_rect_time = []
SF_adr_global_final = np.empty(shape=[0, 3])
# matrixCordinatesDimRow = 13
# matrixCordinatesDimCol = 13
'''AF_MODIFY
matrixCordinatesDimRow = 5
matrixCordinatesDimCol = 5
'''
#This is the size of the matrix in which distribute the gateways
matrixCordinatesDimRow = 5 #10 5 15
matrixCordinatesDimCol = 5 #10 5 15
matrixCordinatesGW = np.empty(
    shape=[matrixCordinatesDimRow, matrixCordinatesDimCol, 2])


# max distance: 300m in city, 3000 m outside (5 km Utz experiment)
# also more unit-disc like according to Utz
nrCollisions = 0
nrReceived = 0
nrProcessed = 0

# global value of packet sequence numbers
packetSeq = 0
pseq = np.array([0, 0, 0, 0, 0, 0, 0])

# list of received packets
recPackets = [[] for i in range(7)]
collidedPackets = [[] for i in range(7)]
lostPackets = [[] for i in range(7)]

# Ptx = 14
Ptx = 14

gamma = eta if eta > 0 else 2.08
d0 = 40  # 53 #40.0
var = fading if fading > 0 else 0
Lpld0 = -52  # Ptx-127.41 #-70.6 #-52 #127.41
GL = 0


# figure out the minimal sensitivity for the given experiment
#AF_COMMENTS given the choosen bandwidth and the choosen experiment
minsensi = -200.0
if ssff == 0:
    if experiment in [0, 1, 4]:
        minsensi = sensi[5, 2]  # 5th row is SF12, 2nd column is BW125
    elif experiment == 2:
        minsensi = -112.0   # no experiments, so value from datasheet
    elif experiment == 3:
        # Experiment 3 can use any setting, so take minimum
        minsensi = np.amin(sensi)
else:
    print("SF {} CR {} BW {}".format(ssff, ccrr, bbww))
    if ssff == 6:
        minsensi = -112.0   # no experiments, so value from datasheet
    else:
        row = np.argwhere(sensi == ssff)
        if bbww == 125 or bbww == 250:
            minsensi = sensi[row[0, 0], int(bbww/125)]
        elif bbww == 500:
            minsensi = sensi[row[0, 0], 3]
        else:
            exit(-1)

# Lpl = Ptx - minsensi
# print "amin", minsensi, "Lpl", Lpl
# #maxDist = 37 #185 #111 #74 #37 #d0*(math.e**((Lpl-Lpld0)/(10.0*gamma)))
# maxDist = d0*(10.0**((Lpl-Lpld0)/(10.0*gamma)))

Lpl = minsensi  # Ptx - minsensi

# d0 / (10^((Pr_d - Pr_d0) / (10 * eta)))
# maxDist = d0 / (10.0**((Lpl-Lpld0)/(10.0*gamma)))
maxDist = max_dist_input

print("maxDist:", maxDist)
# input("TEST DISTANCE -...")

#AF_COMMENTS calculate the distances at which the gateways can listen the nodes with the minimun (7) and the maximum (12) spreading factors
all_Dist = []
all_minsensi = []
for ii in range(0, 6):
    minsensi_temp = sensi[ii, 1]  # 5th row is SF12, 2nd column is BW125
    all_minsensi.append(minsensi_temp)
    Lpl_temp = minsensi_temp
    all_Dist.append(round(d0 / (10.0**((Lpl_temp-Lpld0)/(10.0*gamma))), 2))
print(all_Dist)


# base station placement
bsx = maxDist+20
bsy = maxDist+20
# plot_xmax = (bsx + maxDist + 20) * 2
# plot_ymax = (bsy + maxDist + 20) * 2
plot_xmax = 100000
plot_ymax = 100000

# maxX = 2 * maxDist * math.sin(60*(math.pi/180)) # == sqrt(3) * maxDist
# maxX = math.sqrt(2) * maxDist
maxX = 20000
# maxY = 2 * maxDist * math.sin(30*(math.pi/180)) # == maxdist
# maxY = math.sqrt(2) * maxDist
maxY = 20000
print("maxX ", maxX)
print("maxY", maxY)


# maximum number of packets the BS can receive at the same time
maxBSReceives = 8


# prepare graphics and add sink
if (graphics == 1):
    plt.ion()
    plt.figure()
    ax = plt.gcf().gca()
    # ax.add_patch(Rectangle((0, 0), maxX, maxY, fill=None, alpha=1))


# list of base stations
bs = []

# list of packets at each base station, init with 0 packets
packetsAtBS = [[] for i in range(0, nrBS)]
packetsRecBS = [[] for i in range(0, nrBS)]
#AF_COMMENTS populate the array with all the base station
for i in range(0, nrBS):
    b = myBS(i)
    bs.append(b)
    packetsAtBS[i] = [[] for j in range(7)]
    packetsRecBS[i] = [[] for j in range(7)]

#AF_COMMENTS populate the array with all the end devices nodes
if not nodes_file:
    for i in range(0, nrNodes):
        # myNode takes period (in ms), base station id packetlen (in Bytes)
        # 1000000 = 16 min
        #AF_COMMENTS 20 is the size of the packets
        node = myNode(i, avgSendTime, 20, 0, 0)
        '''AF_ADD '''
        if(i<1000 and i%100==0):
            print("Node " + str(i) + " created")
        elif(i<10000 and i%1000==0):
            print("Node " + str(i) + " created")
        elif(i%10000==0):
            print("Node " + str(i) + " created")
            
        nodes.append(node)
        #AF_COMMENTS create a runnable with the function transmit dor the current node, this is done by the "env" library and wil be started later
        #AF_COMMENTS note that the transmit() function should have a infinite loop and it end when the thread is stopped
        env.process(transmit(env, node))
else:
    with open('simulation_files/' + nodes_file, 'r') as nfile:
        for i in range(0, nrNodes):
            line = nfile.readline()
            split = line.strip().split(' ')
            id = int(split[0])
            xpos = float(split[1])
            ypos = float(split[2])
            node = myNode(id, avgSendTime, 20, xpos, ypos)
            nodes.append(node)
            env.process(transmit(env, node))


# prepare show
#AF_COMMENTS all the if (graphics == 1) before are just the built of the final graph that is shown here
if (graphics == 1):
    plt.xlim([-7000, plot_xmax + 1000])
    plt.ylim([-7000, plot_ymax + 1000])
    plt.draw()
    plt.show()
    input('Press Enter to continue ...')

# store nodes and basestation locations
# with open('nodes.txt', 'w') as nfile:
#     for node in nodes:
#         nfile.write('{x} {y} {id}\n'.format(**vars(node)))
#
#AF_COMMENTS before to tun the ADR algorithm store base stations in a file with the format of the basestation structure   ROW: || X | Y | ID ||
'''AF_ADD if i insert the file with the node, i already have the file with the basestations'''
if not nodes_file:
    with open('simulation_files/basestation-' + str(int(distanceBetweenGW)) + '.txt', 'w') as bfile:
        for basestation in bs:
            bfile.write('{x} {y} {id}\n'.format(**vars(basestation)))

#AF_COMMENTS before to tun the ADR algorithm store nodes in a file with the format   ROW: || ID | X | Y | (RSSI | SF)_bs1 | (RSSI | SF)_bs2 | .... | (RSSI | SF)_bsn ||
if not nodes_file:
    with open('simulation_files/' +str(nrNodes) + '-nodes-raw.txt', 'w') as nfile:
        for n in nodes:
            # nfile.write("{} {} {} {} {}\n".format(n.nodeid, n.x, n.y, n.packet.rssi, n.packet.sf[0]))
            nfile.write("{} {} {}".format(n.id, n.x, n.y))
            for bs in range(0, nrBS):
                nfile.write(" {} {}".format(
                    n.packet[bs].rssi, n.packet[bs].sf))
            nfile.write("\n")


#AF_COMMENTS the experiment parameter is taken to input and specify the kind of experiment
if experiment == 6:
    # print(all_Dist)
    # print(all_minsensi)
    #AF_COMMENTS the run_ADR function takes as paramenters the array of end devices nodes objects and the matrix of the sensibilities to set the transmission parameters
    #AF_COMMENTS in the reality the algorithm takes the nodes from the file
    run_ADR(nodes, sensi)
    # sys.exit(1)
elif experiment == 5:
    SF_adr = np.full((nrNodes, 1), ssff)
    SF_local = np.full((nrNodes, 1), ssff)

#AF_CPMMENTS this will save the output of the ADR algorithm but only if there is no node file as input ???
if not nodes_file:
    # if True:
    #fname = "exp" + str(experiment) + "BS" + str(nrBS) + "fading" + str(fading) + "_sf" + str(ssff) + "_cr" + str(ccrr) + "_bw" + str(bbww) + "_eta" + str(eta) + ".dat"
    with open('simulation_files/' + str(nrNodes) + '-nodes-raw-final-sfinput-' + str(SF_input) + '-full-' + str(full_collision) + '-' + str(int(distanceBetweenGW)) + '.txt', 'w') as nfile:
        for n in nodes:
            # nfile.write("{} {} {} {} {}\n".format(n.nodeid, n.x, n.y, n.packet.rssi, n.packet.sf[0]))
            #nfile.write ("{} {} {}".format(n.id, n.x, n.y))
            nfile.write("{} {} {}".format(n.id, n.x, n.y))
            for bs in range(0, nrBS):
                nfile.write(" {} {}".format(
                    n.packet[bs].rssi, n.packet[bs].sf))
            # nfile.write (" {} {} {}".format (n.r, n.thd, n.thr))
            nfile.write("\n")


# start simulation
#AF_COMMENTS this will start all the threads with the transimt function for all the devices already created, and the execution run until the end of the time
env.run(until=simtime)

# print stats and save into file
# print "nrCollisions ", nrCollisions
# print list of received packets
# print recPackets
# differenciated by SF
print("nr received packets", len(recPackets[6 - 6]), len(recPackets[7 - 6]), len(recPackets[8 - 6]), len(
    recPackets[9 - 6]), len(recPackets[10 - 6]), len(recPackets[11 - 6]), len(recPackets[12 - 6]))
print("nr collided packets", len(collidedPackets[6 - 6]), len(collidedPackets[7 - 6]), len(collidedPackets[8 - 6]), len(
    collidedPackets[9 - 6]), len(collidedPackets[10 - 6]), len(collidedPackets[11 - 6]), len(collidedPackets[12 - 6]))
print("nr lost packets", len(lostPackets[6 - 6]), len(lostPackets[7 - 6]), len(lostPackets[8 - 6]), len(
    lostPackets[9 - 6]), len(lostPackets[10 - 6]), len(lostPackets[11 - 6]), len(lostPackets[12 - 6]))

# print "sent packets: ", sent
# print "sent packets-collisions: ", sent-nrCollisions
for i in range(0, nrBS):
    print("packets at BS", i, ":", [len(packetsRecBS[i][j]) for j in range(7)])
print("sent packets: ", packetSeq)

# data extraction rate
der = sum([len(i) for i in recPackets])/float(packetSeq)
# if interfSF:
#     print "DER:", der,  [len(recPackets[i])/np.float64(pseq[i]) for i in range(7)]
# else:
#     print "DER:", der
print("DER:", der)
#der = (nrReceived)/float(sent)
# print "DER method 2:", der

# this can be done to keep graphics visible
if (graphics == 1):
    input('Press Enter to continue ...')


# save experiment data into a dat file that can be read by e.g. gnuplot
# name of file would be:  exp0.dat for experiment 0
if ssff == 0:
    fname = "exp" + str(experiment) + "BS" + str(nrBS) + \
        "fading" + str(fading) + ".dat"
else:
    fname = "exp" + str(experiment) + "BS" + str(nrBS) + "fading" + str(fading) + "_sf" + \
        str(ssff) + "_cr" + str(ccrr) + "_bw" + \
        str(bbww) + "_eta" + str(eta) + ".dat"
print(fname)


SF_adr_group = []  # number of ED for each SF group
for ii in range(0, 6):
    # node.packet[bs].sf = int(np.min(SF_adr[nodeid]))
    # SF_adr_group.append( np.count_nonzero( SF_adr_global_final[:, 1] == sensi[ii, 0] ))
    SF_adr_group.append(np.count_nonzero(SF_adr[:] == sensi[ii, 0]))
print(SF_adr_group)


SF_set = np.array([7, 8, 9, 10, 11, 12])
sent_group = np.zeros(len(SF_set))
collision_group = np.zeros(len(SF_set))
for node_index in range(0, nrNodes):
    sent_group[np.where(SF_set == nodes[node_index].packet[0].sf)[
        0][0]] += nodes[node_index].sent
    collision_group[np.where(SF_set == nodes[node_index].packet[0].sf)[
        0][0]] += nodes[node_index].collisions

print("sent packet : " + str(sent_group))
print("collision packet : " + str(collision_group))

print(clusterMap)

# if interfSF:
#     if os.path.isfile(fname):
#         res = "\n" + str(nrNodes) + " " + str(avgSendTime) + " " + str(der) + " " + str([len(recPackets[i])/np.float64(pseq[i]) for i in range(7)])
#     else:
#         res = "# nrNodes lambda(ms) DER\n" + str(nrNodes) + " " + str(avgSendTime) + " " + str(der) + " " + str([len(recPackets[i])/np.float64(pseq[i]) for i in range(7)])
# else:
#     if os.path.isfile(fname):
#         res = "\n" + str(nrNodes) + " " + str(avgSendTime) + " " + str(der)
#     else:
#         res = "# nrNodes lambda(ms) DER\n" + str(nrNodes) + " " + str(avgSendTime) + " " + str(der)
# with open(fname, "a") as myfile:
#     myfile.write(res)
# myfile.close()


# compute energy
energy = 0.0
mA = 90    # current draw for TX = 17 dBm
V = 3     # voltage XXX
sent = 0
# for i in range(0,nrNodes):
#     #    print "sent ", nodes[i].sent
#     sent = sent + nodes[i].sent
#     energy = (energy + nodes[i].packet.rectime * mA * V * nodes[i].sent)/1000.0
# print "energy (in mJ): ", energy
# print "sent: ", sent


if os.path.isfile(fname):
    res = "\n" + str(nrNodes) + " " + str(nrCollisions) + " " + str(packetSeq) + \
        " " + str(energy) + " " + str(nrReceived) + " " + str(der)
else:
    res = "#nrNodes nrCollisions nrTransmissions OverallEnergy nrReceived\n" + str(nrNodes) + " " + str(
        nrCollisions) + " " + str(packetSeq) + " " + str(energy) + " " + str(nrReceived) + " " + str(der)

for ii in range(0, 6):
    res = res + " " + str(SF_adr_group[ii])

for ii in range(0, 6):
    res = res + " " + str(int(sent_group[ii]))

for ii in range(0, 6):
    res = res + " " + str(int(collision_group[ii]))

for ii in range(1, 7):
    if nrBS == 25:
        res = res + " " + str(int(len(packetsRecBS[12][ii])))
    else:
        res = res + " " + str(int(len(packetsRecBS[0][ii])))

res = res + " " + str(maxDist)

with open('simulation_files/' + fname, "a") as myfile:
    myfile.write(res)

myfile.close()


# with open('nodes-adr.txt','w') as nfile:
with open('simulation_files/nodes-adr-' + str(SF_input) + '-' + str(nrBS) + '-' + str(nrNodes) + '-' + str(full_collision) + '.txt', 'w') as nfile:
    for n in nodes:
        nfile.write("{} {} {} {} {} {} {} {} {} {}\n".format(n.id, n.x, n.y, n.r,
                    n.packet[0].rssi, n.packet[0].sf, n.sent, n.collisions, n.lost, round(n.packet[0].Pout, 4)))


exit(-1)
# below not updated
