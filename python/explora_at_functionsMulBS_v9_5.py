#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function
import numpy as np
import itertools
import csv
import sys
import random
import math


# baseSF = [12, 11, 11, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 9, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, \
#           7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, \
#          12, 11, 11, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 9, 9, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, \
#           7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]

baseSF = [12, 11, 10, 9, 8, 7,
          11, 10, 9, 8, 7,
          10, 9, 8, 7,
          10, 9, 8, 7,
          9, 8, 7,
          9, 8, 7,
          9, 8, 7,
          8, 7,
          8, 7,
          8, 7,
          8, 7,
          8, 7,
          8, 7,
          8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
          12, 11, 10, 9, 8, 7,
          10, 9, 8, 7,
          10, 9, 8, 7,
          10, 9, 8, 7,
          9, 8, 7,
          9, 8, 7,
          9, 8, 7,
          9, 8, 7,
          8, 7,
          8, 7,
          8, 7,
          8, 7,
          8, 7,
          8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]

baseSFhigh = [12, 11, 10,
              11, 10,
              10,
              10,
              12, 11, 10,
              10,
              10,
              10, ]

baseSFlow = [9, 8, 7, \
             # baseSF = [9, 8, 7, \
             9, 8, 7, \
             9, 8, 7, \
             9, 8, 7, \
             9, 8, 7, \
             9, 8, 7, \
             9, 8, 7, \
             8, 7, \
             8, 7, \
             8, 7, \
             8, 7, \
             8, 7, \
             8, 7, \
             8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, \
             9, 8, 7, \
             9, 8, 7, \
             9, 8, 7, \
             9, 8, 7, \
             9, 8, 7, \
             9, 8, 7, \
             9, 8, 7, \
             9, 8, 7, \
             8, 7, \
             8, 7, \
             8, 7, \
             8, 7, \
             8, 7, \
             7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]


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

#AF_COMMENTS the parameter are used just to take the size of the arrays to create, then all the data are taken by the files and the RSSI matrix is calculated here
def explora_at_self_multi_dim(mat, SF_local, nrBS, BSat, nrNodes, SF_input, distanceBetweenGW, torreCanavese):

    global baseSF, baseSFhigh, baseSFlow

    print_log = 0  # 0 no log #1 low verbose #2 high verbose
    SF_set = np.array([7, 8, 9, 10, 11, 12])

    # create node matrix
    n = 3 + (nrBS * 2)
    nodeMatrix = np.empty(shape=[0, n])

    #AF_COMMENTS take the nodes from the file
    # get node info from file
    '''AF_MODIFY
    with open('simulation_files/' + str(nrNodes) + '-nodes-raw-mygen.txt', mode='r') as csv_file:
    with open('simulation_files/' + str(nrNodes) + '-nodes-raw-BwGw-' + str(int(distanceBetweenGW)) + '-BwGN-' + str(int(distanceBetweenGW)) + '-mygen.txt', mode='r') as csv_file:
    '''
    with open('simulation_files/' + str(nrNodes) + '-nodes-raw.txt', mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=' ')
        line_count = 1
        for row in csv_reader:
            currentRow = []
            if line_count == 0:
                pass
            else:
                currentRow.append(int(row[0]))
                currentRow.append(float(row[1]))
                currentRow.append(float(row[2]))
                for bs in range(0, nrBS):
                    currentRow.append(float(row[4 + ((bs*2)-1)]))
                    currentRow.append(float(row[4 + (bs*2)]))

            line_count += 1
            nodeMatrix = np.append(nodeMatrix, [np.array(currentRow)], axis=0)

    # sort node matrix according with rssi
    # col = 3 + (BSat*2)
    # nodeMatrix = nodeMatrix[np.argsort(nodeMatrix[:, col])]
    # nodeMatrix = nodeMatrix[::-1]

    # RSSImax = -50
    # RSSImin = -140
    # RSSIstep = abs(RSSImin - RSSImax)
    RSSImatrixArray = []
    # # for bs in range (0, nrBS):
    # #     RSSImatrixArray.append(RSSIstep)

    if print_log > 1:
        for row in nodeMatrix:
            print(str(row[0]) + " " + str(row[3 + (BSat*2)]) +
                  " " + str(row[4 + (BSat*2)]))
        raw_input(str(BSat) + ' [1] Press Enter to continue ...')

    # set SF according with rssi
    if not torreCanavese:
        sensi = np.array([-124.0, -127.0, -130.0, -133.0, -135.0, -137.0])

    if torreCanavese:
        sensi = np.array([-8.35, -10.7, -12.75, -15.5, -17.9, -23.4])

    #AF_COMMENTS calculate the famus RSSI matrix
    RSSImatrix = np.empty(shape=[0, 5], dtype=object)
    RSSImatrixIndex = 0
    '''             AF_ADD
    print("nodeMatrix: ",nodeMatrix)
    '''
    #AF_COMMENTS nodeMatrix is an array containing one array for each row in the nodes files, so each array has the form of the row in the file, so how specified in the write of the other file
    for row in nodeMatrix:
        nodeId = int(row[0])
        coverageGWlist = []
        currentRSSItarget = 0
        currentSFtarget = 0

        maxRSSI = sensi[5]
        referenceBS = -1
        currentRSSISumFlag = 0

        #AF_COMMENTS choose the spreading factor to assign to the node for each base station basing on the sensi range for each spreding factor
        for bs in range(0, nrBS):
            currentRSSI = row[3 + (bs*2)]
            currentSF = 13
            if (currentRSSI >= sensi[0]):
                currentSF = 7
            elif (currentRSSI >= sensi[1]) and (currentRSSI < sensi[0]):
                currentSF = 8
            elif (currentRSSI >= sensi[2]) and (currentRSSI < sensi[1]):
                currentSF = 9
            elif (currentRSSI >= sensi[3]) and (currentRSSI < sensi[2]):
                currentSF = 10
            elif (currentRSSI >= sensi[4]) and (currentRSSI < sensi[3]):
                currentSF = 11
            # elif (currentRSSI >= sensi[5]) and (currentRSSI < sensi[4]):
            else:
                currentSF = 12

            row[4 + (bs*2)] = currentSF
            #AF_COMMENTS insert in the list all the gateways of the current node
            if True:  # currentSF < 8:
                coverageGWlist.append(bs)

            # if currentRSSI > -120:
            #AF_COMMENTS count for how many basestations the current node has an RSSI greather that -112
            if currentRSSI > -112:
                currentRSSISumFlag += 1

            #AF_COMMENTS take the maximum RSSI value between all the basestation of the current node and keep that base station as reference for the current this node
            if currentRSSI > maxRSSI:
                maxRSSI = currentRSSI
                referenceBS = bs

            #AF_COMMENTS bufferize the RSSI of the current node for the first base station; BSat is 0 and is taken in input
            if bs == BSat:
                currentRSSItarget = currentRSSI
                currentSFtarget = currentSF

        # if (SF_input == 27) or (SF_input == 31) or ((currentSFtarget < 13) and (SF_local[nodeId] == 0)):
        #     if BSat == referenceBS:
        #         RSSImatrix = np.append (RSSImatrix, [np.array ([nodeId, currentRSSItarget, currentSFtarget, np.empty (shape=len (coverageGWlist), dtype=object), currentRSSISumFlag])], axis=0)
        #         if len (coverageGWlist) > 0:
        #             for idx, val in enumerate (coverageGWlist):
        #                 RSSImatrix[RSSImatrixIndex, 3][idx] = val
        #         print(RSSImatrix[RSSImatrixIndex])
        #         RSSImatrixIndex += 1
        # elif (SF_input == 28) or (SF_input == 29) or (SF_input == 30) or (SF_input == 13) : # or (SF_input == 31):
        #     RSSImatrix = np.append (RSSImatrix, [np.array ([nodeId, currentRSSItarget, currentSFtarget, np.empty (shape=len(coverageGWlist), dtype=object), currentRSSISumFlag])], axis=0)
        #     if len (coverageGWlist) > 0:
        #         for idx, val in enumerate (coverageGWlist):
        #             RSSImatrix[RSSImatrixIndex, 3][idx] = val
        #     RSSImatrixIndex += 1
            
        #AF_COMMENTS enter here only if the current node has as base station with maximum RSSI the base station for which i have runned the algorithm now
        if (BSat == referenceBS) or (SF_input == 13):
            '''             AF_ADD
            if RSSImatrixIndex-1>= 0:
                print("before: ", RSSImatrix[RSSImatrixIndex-1])
            '''
            #AF_COMMENTS so in this matrix there are only the nodes that have as maximum RSSI basestation the current basestation for which the algorithm has been started
            RSSImatrix = np.append(RSSImatrix, [np.array([nodeId, currentRSSItarget, currentSFtarget, np.empty(shape=len(coverageGWlist), dtype=object), currentRSSISumFlag])],
                                   axis=0)
            if len(coverageGWlist) > 0:
                for idx, val in enumerate(coverageGWlist):
                    RSSImatrix[RSSImatrixIndex, 3][idx] = val
            '''             AF_MODIFY   
            print("*****************************************")
            print(RSSImatrix[RSSImatrixIndex]) 
            print("*****************************************")
            '''
            RSSImatrixIndex += 1

    if print_log > 1:  # print_log:
        raw_input(' [1.0.0] Press Enter to continue ...')

    #AF_COMMENTS if the RSSI matrix has never been filled, menas that the starting spreding factors are good
    if len(RSSImatrix) == 0:
        return SF_local

    RSSImatrixTuple = tuple([len(RSSImatrix)])
    RSSImatrixLen = len(RSSImatrix)
    if SF_input != 22 and SF_input != 34:
        RSSImatrix = RSSImatrix[np.argsort(RSSImatrix[:, 1])]
        RSSImatrix = RSSImatrix[::-1]

    if print_log > 1:  # print_log:
        for tupleElement in np.ndindex(RSSImatrixTuple):
            print(RSSImatrix[tupleElement])
        raw_input(' [1.0.1] Press Enter to continue ...')

    exploraNodeNumber = RSSImatrixLen
    # set group percent
    #AF_COMMENTS these are the percentages of the spreding factors distribution used for EXPLoRa-C
    SF_perc = np.array([0.47004852, 0.25854953, 0.14357661, 0.07176894, 0.03588447, 0.02017192])
    # set group nodes number
    #AF_COMMENTS calculate the numebr of nodes to assign at each spreding factor this for just the current basestation for which the algorithm is running
    SF_group = SF_perc * exploraNodeNumber
    # init array with final nodes number group
    SF_group_int = np.empty(shape=[0, 1])
    SF_group_int_progressive = np.empty(shape=[0, 1])
    #AF_COMMENTS make the array of nodes for each SF an integer array
    #AF_COMMENTS if there is only one node in the matrix the resulting array is easy
    if exploraNodeNumber == 1:
        SF_group_int = [1, 0, 0, 0, 0, 0]
    else:
        consumedNodeNumber = 0
        # set SF_group_int and SF_group_delimiter: they are the theorical delimiter for the nodes
        for indexGroup in range(len(SF_group)):
            if indexGroup < len(SF_group) - 1:
                # print(int(SF_group[indexGroup]))
                SF_group_int = np.append(
                    SF_group_int, round(SF_group[indexGroup]))
                consumedNodeNumber += round(SF_group[indexGroup])
                SF_group_int_progressive = np.append(
                    SF_group_int_progressive, consumedNodeNumber)

            else:
                SF_group_int = np.append(
                    SF_group_int, [exploraNodeNumber - consumedNodeNumber], axis=0)
                SF_group_int_progressive = np.append(
                    SF_group_int_progressive, exploraNodeNumber)

    if print_log > 0:
        print("RSSImatrixLen : " + str(RSSImatrixLen))
        print(SF_group_int)
        print(SF_group_int_progressive)
        # raw_input (' [1.0.1] Press Enter to continue ...')

    allocatedSFCount = np.zeros(len(SF_set))

    if SF_input == 13:

        if nrBS == 1:
            SFGroup = np.full((6, 1), 0)
            averageNodeGroup = int(nrNodes / 6)
            for ii in range(5):
                SFGroup[ii] = averageNodeGroup
            SFGroup[5] = nrNodes - (averageNodeGroup * 5)

            indexSF = 0
            indexCurrentSF = 0
            for arrayIndex in range(RSSImatrixLen):
                if SF_local[int(RSSImatrix[arrayIndex, 0])] == 0:
                    if SF_set[indexSF] >= RSSImatrix[arrayIndex, 2]:
                        RSSImatrix[arrayIndex, 2] = SF_set[indexSF]
                        SF_local[int(RSSImatrix[arrayIndex, 0])
                                 ] = SF_set[indexSF]
                        allocatedSFCount[indexSF] += 1

                        indexCurrentSF += 1
                        if indexCurrentSF >= SFGroup[indexSF]:
                            indexSF += 1
                            indexCurrentSF = 0

                    else:
                        SF_local[int(RSSImatrix[arrayIndex, 0])
                                 ] = RSSImatrix[arrayIndex, 2]
                        allocatedSFCount[RSSImatrix[arrayIndex, 2] - 7] += 1

        else:
            for arrayIndex in range(RSSImatrixLen):
                if SF_local[int(RSSImatrix[arrayIndex, 0])] == 0:
                    indexSF = random.randint(0, 5)
                    RSSImatrix[arrayIndex, 2] = SF_set[indexSF]
                    SF_local[int(RSSImatrix[arrayIndex, 0])] = SF_set[indexSF]
                    allocatedSFCount[indexSF] += 1

        if print_log > 0:
            print("RSSImatrixLen : " + str(RSSImatrixLen))
            print(RSSImatrixLen)
            print(SF_group_int)
            print(allocatedSFCount)
            # raw_input (' [1.1.3] Press Enter to continue ... (SF_input : ' + str (SF_input))

    # elif (SF_input == 20 or SF_input == 22) and nrBS == 1:
    elif (SF_input == 20 or SF_input == 22):
        reallocNum = [4, 2, 2, 1, 1]
        indexSF = 0
        while indexSF < len(SF_set):

            if print_log > 0:
                # print (RSSImatrix)
                print(RSSImatrixLen)
                print(indexSF)
                print(SF_group_int)
                print(allocatedSFCount)
                raw_input(' [1.1.2] Press Enter to continue ...')

            # for arrayIndex in range (RSSImatrixLen):
            arrayIndex = 0
            while arrayIndex < RSSImatrixLen:
                if SF_local[int(RSSImatrix[arrayIndex, 0])] == 0:
                    if SF_set[indexSF] >= RSSImatrix[arrayIndex, 2]:
                        RSSImatrix[arrayIndex, 2] = SF_set[indexSF]
                        SF_local[int(RSSImatrix[arrayIndex, 0])
                                 ] = SF_set[indexSF]
                        allocatedSFCount[indexSF] += 1

                arrayIndex += 1
                if allocatedSFCount[indexSF] >= SF_group_int[indexSF]:
                    indexSF += 1
                    if indexSF >= len(SF_set):
                        break
                    else:
                        arrayIndex = 0

            if indexSF < len(SF_set):
                residueSF = SF_group_int[indexSF] - allocatedSFCount[indexSF]
                indexSF += 1
                indexSFLocal = indexSF
                indexRealloc = 0
                while residueSF > 0:
                    for ii in range(reallocNum[indexRealloc]):
                        SF_group_int[indexSFLocal] += 1
                        residueSF -= 1
                        if residueSF == 0:
                            break

                    indexRealloc += 1
                    if indexRealloc >= len(reallocNum):
                        indexRealloc = 0

                    indexSFLocal += 1
                    if indexSFLocal >= len(SF_set):
                        indexSFLocal = indexSF

        if print_log > 0:
            print(RSSImatrix)
            print(RSSImatrixLen)
            print(SF_group_int)
            print(allocatedSFCount)
            raw_input(' [1.1.3] Press Enter to continue ...')

    elif SF_input == 27:

        increaseSF7percent = 0.15
        increaseSFHighpercent = 0.05

        # if distanceBetweenGW - 5000 > 0:
        #     increaseSF7percent = 0.15 #0.15/7000 * (distanceBetweenGW - 5000)
        #     SF_group_int[8 - 7] = SF_group_int[8 - 7] - int(increaseSF7percent*nrNodes*0.3)
        #     SF_group_int[9 - 7] = SF_group_int[9 - 7] - int(increaseSF7percent*nrNodes*0.25)
        #     SF_group_int[10 - 7] = SF_group_int[10 - 7] - int(increaseSF7percent*nrNodes*0.2)
        #     SF_group_int[11 - 7] = SF_group_int[11 - 7] - int(increaseSF7percent*nrNodes*0.15)
        #     SF_group_int[12 - 7] = SF_group_int[12 - 7] - int(increaseSF7percent*nrNodes*0.1)
        #     SF_group_int[7 - 7] = nrNodes - np.sum(SF_group_int[1:7])
        #     if print_log > 0:
        #         print(SF_group_int)
        #         print(allocatedSFCount)
        #         raw_input (' [1.0.2] Press Enter to continue ...')

        usedSF7 = 0

        if nrBS == 3:

            baseSF = baseSFlow

            # ED coverd by unique gateway
            for arrayIndex in range(RSSImatrixLen-1, -1, -1):
                if len(RSSImatrix[arrayIndex, 3]) == 1:
                    if SF_set[0] >= RSSImatrix[arrayIndex, 2]:
                        SF_local[int(RSSImatrix[arrayIndex, 0])] = 7
                        RSSImatrix[arrayIndex, 2] = 7
                        allocatedSFCount[7 - 7] += 1
                        usedSF7 += 1

                if usedSF7 >= (SF_group_int[0]) + int(increaseSF7percent*RSSImatrixLen):
                    break

            RSSImatrix = RSSImatrix[np.argsort(RSSImatrix[:, 4])]
            RSSImatrix = RSSImatrix[::-1]

            baseSFIndex = 0
            baseSFHighLen = len(baseSFhigh)
            usedSFHigh = 0
            for nodeIndex in range(RSSImatrixLen):
                SF_local[int(RSSImatrix[nodeIndex, 0])
                         ] = baseSFhigh[baseSFIndex]
                RSSImatrix[nodeIndex, 2] = baseSFhigh[baseSFIndex]
                allocatedSFCount[int(baseSFhigh[baseSFIndex]) - 7] += 1

                baseSFIndex += 1
                if baseSFIndex >= baseSFHighLen:
                    baseSFIndex = 0

                usedSFHigh += 1
                # if usedSFHigh >= sum(SF_group_int[3:6])-int(increaseSFHighpercent*RSSImatrixLen):
                if usedSFHigh >= sum(SF_group_int[3:6]) - int(increaseSFHighpercent * RSSImatrixLen):
                    break

            # for tupleElement in np.ndindex (RSSImatrixTuple):
            #     print (RSSImatrix[tupleElement])
            # raw_input (' [1.0.0] Press Enter to continue ...')

            RSSImatrix = RSSImatrix[np.argsort(RSSImatrix[:, 1])]
            RSSImatrix = RSSImatrix[::-1]

            if print_log > 0:
                print(RSSImatrix)
                print(RSSImatrixLen)
                print(SF_group_int)
                print(allocatedSFCount)
                raw_input(' [1.1.2] Press Enter to continue ...')

            '''             AF_MODIFY
            print("--> " + str(usedSF7))
            usedSF7 = usedSF7 - int(increaseSF7percent*RSSImatrixLen)
            print("--> " + str(usedSF7))
            '''

        # if usedSF7 < (SF_group_int[0]):
        #     countLocalSF7 = 0
        #     rssiThreshold = 3
        #     oneDBlessIndex = RSSImatrixLen-1
        #     for arrayIndex in range(RSSImatrixLen-1,-1,-1):
        #         print(" {} {} {} {} ".format(arrayIndex, RSSImatrix[arrayIndex,1],  RSSImatrix[oneDBlessIndex,1], countLocalSF7))
            #
        #         if abs(RSSImatrix[arrayIndex,1] - RSSImatrix[oneDBlessIndex,1]) > rssiThreshold:
        #             oneDBlessIndex = arrayIndex
        #             countLocalSF7 = 0
            #
        #         if countLocalSF7 < 23:
        #             if SF_set[0] >= RSSImatrix[arrayIndex, 2]:
        #                 SF_local[int (RSSImatrix[arrayIndex, 0])] = 7
        #                 RSSImatrix[arrayIndex, 2] = 7
        #                 allocatedSFCount[7 - 7] += 1
        #                 usedSF7 += 1
        #                 countLocalSF7 += 1
            #
        #         if usedSF7 >= (SF_group_int[0]):
        #             break
            #
        #         # raw_input ('test')
            #
        # if print_log > 1:  # print_log:
        #     for tupleElement in np.ndindex (RSSImatrixTuple):
        #         print (RSSImatrix[tupleElement], SF_local[int (RSSImatrix[tupleElement, 0])])
        #     raw_input (' [1.0.0] Press Enter to continue ...')
            #
        # if print_log > 0:
        #     print ("RSSImatrixLen : " + str (RSSImatrixLen))
        #     print (usedSF7)
        #     print (RSSImatrixLen)
        #     print (SF_group_int)
        #     print (allocatedSFCount)
        #     raw_input (' [1.1.3] Press Enter to continue ...')

        if usedSF7 < (SF_group_int[0]):
            oneDBlessIndex = 0
            SF_local[int(RSSImatrix[0, 0])] = 7
            RSSImatrix[0, 2] = 7
            allocatedSFCount[7 - 7] += 1
            rssiThreshold = 3
            for arrayIndex in range(2, RSSImatrixLen-1):
                # print(" {} {} {} {} ".format(arrayIndex,RSSImatrix[arrayIndex,0], RSSImatrix[arrayIndex,1], oneDBlessIndex))

                # if abs(RSSImatrix[arrayIndex,1] - RSSImatrix[oneDBlessIndex,1]) > rssiThreshold:
                #     while abs(RSSImatrix[arrayIndex,1] - RSSImatrix[oneDBlessIndex,1]) > rssiThreshold:
                #         oneDBlessIndex += 1

                #AF_COMMENTS this is the first step of EXPLoRa-C, check the threshold 
                #AF_COMMENTS BUG?? this can be a bug because this check is done only between nodes that will have the same reference base station, the second pass of the algorithm check if the nodes
                #AF_COMMENTS are far away, but how it is possible if we take into account only nodes with the same base station of reference? The answare is taht the second pass check that there
                #AF_COMMENTS should be at least one basestation different in order to reach that base station
                #AF_COMMENTS BUG?? The bug can be also that even if the node has choosen one basestation as reference, the signal is received also by the other basestations, what ensure to me that the
                #AF_COMMENTS signal that this base station is sending to its reference basestation don't reach a different base station with an RSSI that is able to cover a signl of a node that
                #AF_COMMENTS has choosen this as its reference base station??
                #AF_COMMENTS ISSUE?? even if i ensure that i put a SF that is able to reach the other basestation, how can i be sure that in the future there is not a node that will choose the same basestation
                #AF_COMMENTS as reference and the RSSI of these two basestations will not interfer?? The idea in my case is to change the reference basestation in the node and run again the algorithm in order
                #AF_COMMENTS to take into account this node with the seconod choice of basestation as reference that should not interfer with other nodes
                if abs(RSSImatrix[arrayIndex, 1] - RSSImatrix[arrayIndex-1, 1]) > rssiThreshold:
                    # difference > 3dB --> put SF7
                    '''             AF_MODIFY
                    print("difference RSSI > 3dB --> put SF7")
                    print(" {} {} {} {} ".format(
                        arrayIndex-1, RSSImatrix[arrayIndex-1, 0], RSSImatrix[arrayIndex-1, 1], oneDBlessIndex))
                    print(" {} {} {} {} ".format(
                        arrayIndex, RSSImatrix[arrayIndex, 0], RSSImatrix[arrayIndex, 1], oneDBlessIndex))
                    '''
                    if SF_set[0] >= RSSImatrix[arrayIndex, 2]:
                        SF_local[int(RSSImatrix[arrayIndex, 0])] = 7
                        RSSImatrix[arrayIndex, 2] = 7
                        allocatedSFCount[7 - 7] += 1
                        usedSF7 += 1

                else:
                    differentGWLenCount = 0
                    # for forwardStep in range(arrayIndex-1,oneDBlessIndex-1,-1):
                    #     if len(RSSImatrix[arrayIndex,3]) != len(RSSImatrix[forwardStep,3]):
                    #         # different number of covered GW --> put SF7
                    #         differentGWLenCount += 1
                    #     else:
                    #         # different GW value --> put SF7
                    #         if not np.array_equal(np.sort(RSSImatrix[arrayIndex,3], axis=0), np.sort(RSSImatrix[forwardStep,3], axis=0)):
                    #             differentGWLenCount += 1

                    #AF_COMMENTS rememebr in the second phase to check that one of the basestation not in common between the two nodes, is covered by the spreading factor that you are assigning
                    #AF_COMMENTS in this second phase
                    if len(RSSImatrix[arrayIndex, 3]) != len(RSSImatrix[arrayIndex-1, 3]):
                        # different number of covered GW --> put SF7
                        differentGWLenCount += 1
                    else:
                        # different GW value --> put SF7
                        if not np.array_equal(np.sort(RSSImatrix[arrayIndex, 3], axis=0), np.sort(RSSImatrix[arrayIndex-1, 3], axis=0)):
                            differentGWLenCount += 1

                    # if differentGWLenCount==(arrayIndex-oneDBlessIndex):
                    if differentGWLenCount > 0:
                        '''             AF_MODIFY
                        print("different number of covered GW --> put SF7")
                        print(" {} {} {} {} ".format(
                            arrayIndex-1, RSSImatrix[arrayIndex-1, 0], RSSImatrix[arrayIndex-1, 1], oneDBlessIndex))
                        print(RSSImatrix[arrayIndex-1, 3])
                        print(" {} {} {} {} ".format(
                            arrayIndex, RSSImatrix[arrayIndex, 0], RSSImatrix[arrayIndex, 1], oneDBlessIndex))
                        print(RSSImatrix[arrayIndex, 3])
                        '''
                        if SF_set[0] >= RSSImatrix[arrayIndex, 2]:
                            SF_local[int(RSSImatrix[arrayIndex, 0])] = 7
                            RSSImatrix[arrayIndex, 2] = 7
                            allocatedSFCount[7 - 7] += 1
                            usedSF7 += 1

                #AF_COMMENTS breack if SF 7 ended
                if usedSF7 >= (SF_group_int[0]):
                    break

        if print_log > 0:
            # if True > 0:
            print("RSSImatrixLen : " + str(RSSImatrixLen))
            print(usedSF7)
            print(RSSImatrixLen)
            print(SF_group_int)
            print(allocatedSFCount)
            raw_input(' [1.1.4] Press Enter to continue ...')

        baseSFLen = len(baseSF)

        baseSFIndex = 0
        # baseSFIndex = baseSFLen-1

        for nodeIndex in range(RSSImatrixLen):
            if SF_local[int(RSSImatrix[nodeIndex, 0])] == 0:
                while baseSF[baseSFIndex] < RSSImatrix[nodeIndex, 2]:
                    baseSFIndex += 1
                    if baseSFIndex == baseSFLen:
                        baseSFIndex = 0

                    # baseSFIndex -= 1
                    # if baseSFIndex == 0:
                    #     baseSFIndex = baseSFLen-1

                SF_local[int(RSSImatrix[nodeIndex, 0])] = baseSF[baseSFIndex]
                RSSImatrix[nodeIndex, 2] = baseSF[baseSFIndex]
                allocatedSFCount[int(baseSF[baseSFIndex]) - 7] += 1

                baseSFIndex += 1
                if baseSFIndex == baseSFLen:
                    baseSFIndex = 0

                # baseSFIndex -= 1
                # if baseSFIndex == 0:
                #     baseSFIndex = baseSFLen - 1

                if usedSF7 > 0 and baseSFIndex < baseSFLen - 1:
                    while (baseSF[baseSFIndex] == 7) and (baseSF[baseSFIndex+1] == 7):
                        usedSF7 -= 1

                        baseSFIndex += 1
                        if baseSFIndex < baseSFLen:
                            baseSFIndex = 0
                            break

                        # baseSFIndex -= 1
                        # if baseSFIndex == 0:
                        #     baseSFIndex = baseSFLen - 1
                        #     break

                        if usedSF7 == 0:
                            break

        if print_log >= 1:
            print("RSSImatrixLen : " + str(RSSImatrixLen))
            print(RSSImatrixLen)
            print(SF_group_int)
            print(allocatedSFCount)
            raw_input(' [1.1.4] Press Enter to continue ...')

    elif (SF_input == 28 or SF_input == 29 or SF_input == 30):

        bs = BSat
        for row in nodeMatrix:
            SF_local[int(row[0])] = row[4 + (bs * 2)]
            if SF_local[int(row[0])] == 13:
                SF_local[int(row[0])] = 12

        baseSF = [12, 11, 10, 9, 8, 7,
                  11, 10, 9, 8, 7,
                  10, 9, 8, 7,
                  10, 9, 8, 7,
                  9, 8, 7,
                  9, 8, 7,
                  9, 8, 7,
                  8, 7,
                  8, 7,
                  8, 7,
                  8, 7,
                  8, 7,
                  8, 7,
                  8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
                  12, 11, 10, 9, 8, 7,
                  10, 9, 8, 7,
                  10, 9, 8, 7,
                  10, 9, 8, 7,
                  9, 8, 7,
                  9, 8, 7,
                  9, 8, 7,
                  9, 8, 7,
                  8, 7,
                  8, 7,
                  8, 7,
                  8, 7,
                  8, 7,
                  7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]

        baseSFLen = len(baseSF)
        baseSFIndex = 0
        unsedSF = np.empty(shape=[0])
        for ii in range(RSSImatrixLen-1, 0, -1):  # range(RSSIstep):
            unusedTest = False
            if len(unsedSF) > 0:
                # print("1!")
                # print(len (unsedSF))
                # print()
                # print(RSSIarray[ii][arrayIndex, 0])
                # print(SF_local[int (RSSIarray[ii][arrayIndex, 0])])
                # print(unsedSF[len (unsedSF) - 1])

                if (SF_local[RSSImatrix[ii, 0]] <= unsedSF[len(unsedSF) - 1]):
                    unusedTest = True

            if unusedTest:
                # print("2!")
                # print()

                SF_local[RSSImatrix[ii, 0]] = unsedSF[len(unsedSF) - 1]
                allocatedSFCount[int(unsedSF[len(unsedSF) - 1]) - 7] += 1
                unsedSF = np.delete(unsedSF, len(unsedSF) - 1)

            else:
                if SF_local[RSSImatrix[ii, 0]] > baseSF[baseSFIndex]:
                    while SF_local[RSSImatrix[ii, 0]] > baseSF[baseSFIndex]:
                        unsedSF = np.append(unsedSF, baseSF[baseSFIndex])
                        baseSFIndex += 1
                        if baseSFIndex == baseSFLen:
                            baseSFIndex = 0

                    SF_local[RSSImatrix[ii, 0]] = baseSF[baseSFIndex]
                    allocatedSFCount[int(baseSF[baseSFIndex]) - 7] += 1

                else:
                    SF_local[RSSImatrix[ii, 0]] = baseSF[baseSFIndex]
                    allocatedSFCount[int(baseSF[baseSFIndex]) - 7] += 1

                baseSFIndex += 1
                if baseSFIndex == baseSFLen:
                    baseSFIndex = 0

            # if len(unsedSF) > 0:
            #     print ()
            #     raw_input (' TEST')

        # print (allocatedSFCount)

        if print_log > 0:
            if len(unsedSF) > 0:
                print(unsedSF)
                print(len(unsedSF))
                raw_input(' ERROR! SF allocation finished and unusedSF len > 0')

        if print_log > 0:
            print(allocatedSFCount)
            print(RSSImatrixLen)
            print(SF_group_int)
            print(allocatedSFCount)
            raw_input(' [1.0.5] Press Enter to continue ...')

    elif SF_input == 31:
        for arrayIndex in range(RSSImatrixLen):
            if SF_local[int(RSSImatrix[arrayIndex, 0])] == 0:
                SF_local[int(RSSImatrix[arrayIndex, 0])
                         ] = RSSImatrix[arrayIndex, 2]

    elif SF_input == 34 and nrBS == 1:
        N = nrNodes
        nsf = np.zeros(6)
        ToA12 = airtime(12, 1, 20, 125)

        # SIR = -16.0 # -4;
        eta = 2.9  # 2.9
        # tableThreshold = [[-0.9, -6.2, -7.8, -8.8, -9.4, -11.9],
        #                   [-9.7, -0.5, -9.2, -10.9, -11.8, -12.4],
        #                   [-13.8, -12.6, -0.1, -12.2, -13.9, -14.8],
        #                   [-16.6, -16.7, -15.5, -0.2, -15.2, -17.0],
        #                   [-19.2, -19.6, -19.7, -18.4, -0.3, -18.3],
        #                   [-21.8, -22.1, -22.4, -22.6, -21.5, -0.4]]

        # tableThreshold = [[-1, -7.95, -10.8, -12.7, -14.3, -16.85],
        #                   [-7.95, -1, -10.9, -13.8, -15.7, -17.25],
        #                   [-10.8, -10.9, -1, -13.85, -16.8, -18.6],
        #                   [-12.7, -13.8, -13.85, -1, -16.8, -19.8],
        #                   [-14.3, -15.7, -16.8, -16.8, -1, -19.9],
        #                   [-16.85, -17.25, -18.6, -19.8, -19.9, -1, ]]
        rSIR = -16
        tableThreshold = [[-1, rSIR, rSIR, rSIR, rSIR, rSIR],
                          [rSIR, -1, rSIR, rSIR, rSIR, rSIR],
                          [rSIR, rSIR, -1, rSIR, rSIR, rSIR],
                          [rSIR, rSIR, rSIR, -1, rSIR, rSIR],
                          [rSIR, rSIR, rSIR, rSIR, -1, rSIR],
                          [rSIR, rSIR, rSIR, rSIR, rSIR, -1, ]]

        for sf in range(7, 13):
            ToAsf = airtime(sf, 1, 20, 125)

            sumT = 0
            for kk in range(7, 13):
                SIR = tableThreshold[sf-7][kk-7]
                # SIR = -16.0
                b = math.pow(10, (SIR / 10 / eta))
                ToAkk = airtime(kk, 1, 20, 125)
                # print(ToAkk)
                sumT = sumT + (math.pow(b, 2) * ((ToAsf / ToAkk) - 1))
                # print(sumT)

            sumT = (1/4)*N*(sumT+2)

            # print('sumT')
            # print(sumT)

            numeratore = N - sumT
            # print(numeratore)
            sumT = 0
            for kk in range(7, 13):
                ToAkk = airtime(kk, 1, 20, 125)
                SIR = tableThreshold[sf-7][kk-7]
                # SIR = -16.0
                b = math.pow(10, (SIR / 10 / eta))
                sumT = sumT + ((ToA12 / ToAkk) * (1 - (math.pow(b, 2) / 2)))
            denominatore = sumT
            # print(denominatore)
            nsf[sf - 7] = int((ToA12 / ToAsf) * (numeratore / denominatore))

            if sum(nsf) > N:
                if nsf[1] > N:
                    raw_input(
                        'ERROR!, wrang explora allocation in presence of inteference spreading factor')

                nsf[sf - 7] = N - sum(nsf[0:sf - 7])
                break

        if sum(nsf) < N:
            nsf[0] = nsf[0] + (N-sum(nsf))
        SF_group_int = nsf

        if print_log > 0:
            print(nsf)
            raw_input(' [1.1.3.1] Press Enter to continue ...')

            print(RSSImatrix)
            print(RSSImatrixLen)
            print(SF_group_int)
            print(allocatedSFCount)
            raw_input(' [1.1.3.2] Press Enter to continue ...')

        reallocNum = [4, 2, 2, 1, 1]
        indexSF = 0
        while indexSF < len(SF_set):

            if print_log > 0:
                # print (RSSImatrix)
                # print (RSSImatrixLen)
                print(indexSF)
                print(SF_group_int)
                print(allocatedSFCount)
                raw_input(' [1.1.2] Press Enter to continue ...')

            # for arrayIndex in range (RSSImatrixLen):
            arrayIndex = 0
            while arrayIndex < RSSImatrixLen:
                # print(arrayIndex)

                if SF_local[int(RSSImatrix[arrayIndex, 0])] == 0:
                    if SF_set[indexSF] >= RSSImatrix[arrayIndex, 2]:
                        RSSImatrix[arrayIndex, 2] = SF_set[indexSF]
                        SF_local[int(RSSImatrix[arrayIndex, 0])
                                 ] = SF_set[indexSF]
                        allocatedSFCount[indexSF] += 1

                arrayIndex += 1
                if allocatedSFCount[indexSF] >= SF_group_int[indexSF]:
                    # print (indexSF)
                    # print (SF_group_int)
                    # print (allocatedSFCount)
                    indexSF += 1
                    if indexSF >= len(SF_set):
                        break
                    else:
                        arrayIndex = 0

            if indexSF < len(SF_set):
                residueSF = SF_group_int[indexSF] - allocatedSFCount[indexSF]

                indexSF += 1
                indexSFLocal = indexSF
                indexRealloc = 0
                while residueSF > 0:
                    for ii in range(reallocNum[indexRealloc]):
                        SF_group_int[indexSFLocal] += 1
                        residueSF -= 1
                        if residueSF == 0:
                            break

                    indexRealloc += 1
                    if indexRealloc >= len(reallocNum):
                        indexRealloc = 0

                    indexSFLocal += 1
                    if indexSFLocal >= len(SF_set):
                        indexSFLocal = indexSF
                    # print (SF_group_int)

        if print_log > 0:
            print(RSSImatrix)
            print(RSSImatrixLen)
            print(SF_group_int)
            print(allocatedSFCount)
            raw_input(' [1.1.3] Press Enter to continue ...')

    else:
        print("ERROR! ADR not supported\n")
        raw_input('Press Enter to continue ...')

    return SF_local
