distanceBetweenGW = 12000
nrNodes = 100000

input_file_path = 'simulation_files/' + str(nrNodes) + '-nodes-raw-BwGw-' + str(int(distanceBetweenGW)) + '-BwGN-' + str(int(distanceBetweenGW)) + '-mygen.txt'
output_file_path = 'simulation_files/clustered_on_position/' + str(nrNodes) + '-nodes-raw-BwGw-' + str(int(distanceBetweenGW)) + '-BwGN-' + str(int(distanceBetweenGW)) + '-cluster-position-format.txt'

header = "nodeID,posX,posY,"

with open(output_file_path, 'w') as outputfile:
    with open(input_file_path, 'r') as nfile:
        for i in range(0, nrNodes):
            line = nfile.readline()
            tranformed_line = line.strip().replace(' ', ',')

            #At the first line count the number of existing basestations to create the header
            if(i==0):
                print(tranformed_line)
                array_of_fields = tranformed_line.split(',')
                print(array_of_fields)
                gateways_counter = 0
                for i in range(3, len(array_of_fields)):
                    if(i%2==0):
                        gateways_counter+=1
                        header = header+"RSSI"+str(gateways_counter)+",SF"+str(gateways_counter)+","
                header = header.removesuffix(",")
                outputfile.write(header)
                outputfile.write("\n")
                print("The current file has "+str(gateways_counter)+" gateways")
            
            outputfile.write(tranformed_line)
            outputfile.write("\n")


