#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest
import pandas
import numpy as np
import csv
from pprint import pprint
from datetime import datetime
import matplotlib.pyplot as plt
from quadtree import Point, Rect, QuadTree
import pathlib



def reproject(latitude, longitude):
	"""Returns the x & y coordinates in meters using a sinusoidal projection"""
	from math import pi, cos, radians
	earth_radius = 6371009 # in meters
	lat_dist = pi * earth_radius / 180.0

	y = [lat * lat_dist for lat in latitude]
	x = [long * lat_dist * cos(radians(lat))
				for lat, long in zip(latitude, longitude)]
	return x, y


def dataAnalysis(nrNodes, fh, sqrt_number_cluster_x, sqrt_number_cluster_y, graphics, PATH_NAME_2):
	from os import fdopen, remove
	"""
	starttime	endtime	xbin	ybin	imsi	imei	mcc	mnc	tac	sv	startcellname	endcellname	lat	lon	par_dt
	"""
	print("dataAnalysis")

	# fh = '../../data/100000-nodes-raw-mygen.txt'
	#fh = 'simulation_files/10000-nodes-raw-mygen-header.csv'
	
	#fh = 'simulation_files/10000-nodes-raw-BwGw-12000-BwGN-12000-mygen.csv'
	#fh = 'simulation_files/clustered_on_position/100000-nodes-raw-BwGw-12000-BwGN-12000-cluster-position-format.txt'

	maxPoint = 100
	#sqrt_number_cluster = 4


	data = pandas.read_csv(fh, sep=',', quotechar = ',')
	#data = data.loc[:10000]
	#print(data[:2])
	#print("My Print", len(data.columns))
	print("Total rows number : " + str(len(data)))
	lenghtArray = len(data.columns)
	# print(lenghtArray)
	# col = data.columns
	# print(col)

	"""
	test
	"""

	# uniqueImei = np.unique(data.imei)
	# uniqueImeiNumber = len(uniqueImei)
	# print("Total imei : " + str(uniqueImeiNumber))

	# col = data.columns
	# print(col)

	# convert datatime
	# print(data[['starttime', 'endtime']].head())
	# data['datestart'] = pandas.to_datetime(data.starttime)
	# data['dateend'] = pandas.to_datetime(data.endtime)
	# dataSorted = data.sort_values('datestart')
	# dataSorted.reset_index(inplace=True, drop=True)

	# slotTime = np.unique(dataSorted.datestart)
	# slotTimeNumber = len(slotTime)
	# print("Total slot time : " + str(slotTimeNumber))

	############# QUADTREE #########################
	# coordinates_array_x, coordinates_array_y = reproject(stations_positions[:, 1], stations_positions[:, 0])
	'''AF_MODIFY this is for different file, for the txt use the one above '''
	coordinates_array = np.column_stack((data['posX'].values, data['posY'].values))
	
	cx = coordinates_array[:, 0].min() + ((coordinates_array[:, 0].max() - coordinates_array[:, 0].min()) / 2)
	cy = coordinates_array[:, 1].min() + ((coordinates_array[:, 1].max() - coordinates_array[:, 1].min()) / 2)
	width = coordinates_array[:, 0].max() - coordinates_array[:, 0].min() + ((coordinates_array[:, 0].max() - coordinates_array[:, 0].min()) * 0.1)
	height = coordinates_array[:, 1].max() - coordinates_array[:, 1].min() + ((coordinates_array[:, 1].max() - coordinates_array[:, 1].min()) * 0.1)

	print("cx:",cx,"cy:",cy,"width:",width,"height:",height)

	points = [Point(*coord) for coord in coordinates_array]
	domain = Rect(cx, cy, width, height)
	qtree = QuadTree(domain, domain, lenghtArray, maxPoint)
	

	for kk in range(len(points)):
		qtree.insert(points[kk], [0,0], kk)

	print('Number of points in the domain =', len(qtree))
	# print("{} - {} : {} : {}".format(str(processedDeviceNum), str(currentImsi), str(containSlotNumber), str(totalOccurrences) ))
	# writer.writerow({'userCount': processedDeviceNum, 'imsi': currentImsi, 'imei': localUniqueImei[0], 'inSlot': containSlotNumber, 'totalOccurrences':totalOccurrences, 'multipleImei': multipleImei, 'multipleImsi': multipleImsi})

	# DPI = 72
	if True:  # processedDeviceNum==2:
		# fig = plt.figure(figsize=(700 / DPI, 500 / DPI), dpi=DPI)
		fig = plt.figure(1)
		ax = plt.subplot()
		ax.set_xlim(-20000, 140000)
		ax.set_ylim(-80000, 100000)
		qtree.draw(ax)

		ax.scatter([p.x for p in points], [p.y for p in points], s=4)
		# ax.scatter(points[0].x, points[0].y, s=150, marker="*", c='black')
		annotate_index = 0
		# # for p in points:
		# for ii in range(0, len(points), 1):
		# 	# ax.scatter(locs_bici[int(kk), 0], locs_bici[int(kk), 1])
		# 	ax.annotate(str(ii), (points[ii].x, points[ii].y))
		# ax.set_xticks([])
		# ax.set_yticks([])

		width_step = ( coordinates_array[:, 0].max() - coordinates_array[:, 0].min() + ((coordinates_array[:, 0].max() - coordinates_array[:, 0].min()) * 0.1) ) / sqrt_number_cluster_x
		height_step = ( coordinates_array[:, 1].max() - coordinates_array[:, 1].min() + ((coordinates_array[:, 1].max() - coordinates_array[:, 1].min()) * 0.1) ) / sqrt_number_cluster_y
		# cx_query = coordinates_array[:, 0].min() - ((coordinates_array[:, 0].max() - coordinates_array[:, 0].min()) * 0.1) + width_step
		# cy_query = coordinates_array[:, 1].min() - ((coordinates_array[:, 1].max() - coordinates_array[:, 1].min()) * 0.1) + height_step
		print("width_step:",width_step,"height_step:",height_step)

		clusterNumber = 0
		totalFoundPointNumber = 0
		'''AF_MODIFY '''
		#cy_query = cy - (height_step/2) - (3*height_step)
		cy_query = cy - (height/2) + (height/(sqrt_number_cluster_y*2))
		print("cy_query:",cy_query)
		for ll in range(sqrt_number_cluster_y):
			'''AF_MODIFY '''
			#cx_query = cx - (width_step / 2) - (3 * width_step)
			cx_query = cx - (width/2) + (width/(sqrt_number_cluster_x*2))
			for mm in range(sqrt_number_cluster_x):
				ax.scatter(cx_query, cy_query, s=150, marker="*", c='black')

				west_edge, east_edge = cx_query - width_step / 2, cx_query + width_step / 2
				north_edge, south_edge = cy_query - height_step / 2, cy_query + height_step / 2
				x1, y1 = west_edge, north_edge
				x2, y2 = east_edge, south_edge
				ax.plot([x1, x2, x2, x1, x1], [y1, y1, y2, y2, y1], c='r', lw=3)

				region = Rect(cx_query, cy_query, width_step, height_step)

				print("Region: ", region)

				found_points = []
				found_geo_point = []
				found_point_id = []
				#print("DEBUG PRINT", region, "||", found_points, "||", found_geo_point, "||", found_point_id)
				qtree.query(region, found_points, found_geo_point, found_point_id)
				#print("DEBUG PRINT", region, "||", found_points, "||", found_geo_point, "||", found_point_id)
				print(ll, mm, 'Number of found points = ', len(found_points))
				totalFoundPointNumber += len(found_points)
				data.loc[found_point_id, 'clusterNumber'] = clusterNumber
				clusterNumber += 1
				#
				# ax.scatter([p.x for p in found_points], [p.y for p in found_points],
				# 		   facecolors='none', edgecolors='r', s=32)
				#
				# region.draw(ax, c='r')

				# ax.invert_yaxis()
				cx_query += width_step
			cy_query += height_step

		print(totalFoundPointNumber)
		print(data['clusterNumber'])
		data['clusterNumber'] = data['clusterNumber'].astype('int')

		plt.figure(2)
		dataClusterd = data.loc[data['clusterNumber']== 0]
		coordinates_array_2 = np.column_stack((dataClusterd['posX'].values, dataClusterd['posY'].values))
		ax = plt.subplot()  # ax.set_xlim(0, width)
		points_2 = [Point(*coord) for coord in coordinates_array_2]
		ax.scatter([p.x for p in points_2], [p.y for p in points_2], s=4)
		ax.set_xlim(-20000, 140000)
		ax.set_ylim(-80000, 100000)

		plt.tight_layout()
		# plt.savefig('search-quadtree.png', DPI=72)
		if graphics:
			plt.show()
	# sys.exit(1)
	'''AF_MODIFY
	# PATH_NAME_1 = '../../data/100000-nodes-raw-mygen-header-cluster-number.csv'
	# PATH_NAME_2 = '../../data/100000-nodes-raw-mygen-cluster-number.csv'
	'''
	#PATH_NAME_1 = 'simulation_files/clustered_on_position/10000-nodes-raw-BwGw-12000-BwGN-12000-header-cluster-number.txt'
	#PATH_NAME_2 = 'simulation_files/clustered_on_position/'+str(nrNodes)+'-nodes-raw-BwGw-12000-BwGN-12000-clustered.txt'

	#data.to_csv(PATH_NAME_1, index=False, header=True, float_format='%.14f')
	data.to_csv(PATH_NAME_2, index=False, header=False, float_format='%.14f',  sep=' ')


def plotBar():
	file_name = 'csv_data/generic-analysis/user-stats.csv'
	cols = ['userCount', 'imei', 'imsi', 'inSlot', 'totalOccurrences']
	currentData = pandas.read_csv(file_name, delimiter=',', usecols=cols)[cols]
	plt1 = plt.figure(1)



def editOteCsv():
	from os import fdopen, remove
	fh = 'D:\work\.csv'
	# # process fields names
	# rowIndex = 0
	# with open(fh,'w') as new_file:
	#     with open(file_path) as old_file:
	#         for line in old_file:
	#             # print(line)
	#             newLine = line.replace(',[', ',|[').replace('],', ']|,').replace(',{', ',|{').replace('},', '}|,')
	#             # print(newLine)
	#             new_file.write(newLine)
	#             rowIndex += 1
	#             # if rowIndex > 745:
	#             #     break#
	#             if rowIndex%10000==0:
	#                 print(rowIndex)

	# get information
	data = pandas.read_csv(fh, sep=',', quotechar='|')
	col = data.columns
	print(col)
	useIndex = data.imei
	print("Rows number : " + str(data.shape[0]))
	print("Users number : " + str(len(np.unique(useIndex))))

	return


#########################
cities = []
cities_dict = {}

def get_data_folder_path():
	current_folder = os.getcwd()
	return os.path.join(current_folder, 'data')

# def get_country_data_path():
#     return os.path.join(get_data_folder_path(), 'countryInfo.txt')

def parse_city_callback(line):
	city = City(line)
	#           {"location": {'type': 'Point', 'coordinates': [8, 47]}, "name": "Zurich", "type" : "city"}]
	# "city","city_ascii","lat","lng","country","iso2","iso3","admin_name","capital","population","id"
	# "Tokyo", "Tokyo", "35.6897", "139.6922", "Japan", "JP", "JPN", "T", "primary", "37977000", "1392685764"
	cities.append({'location': {'type': 'Point', 'coordinates': [float(city.lng), float(city.lat)]}, 'name': city.city, 'type' : 'city',
				   'country':city.country, 'city_ascii': city.city_ascii, 'id': int(city.id)})

def get_city_data_path():
	return os.path.join(get_data_folder_path(), 'worldcities.csv')

def get_poi_data_path():
	return os.path.join(get_data_folder_path(), 'worldcities.csv')

def read_csv_by_line(file_path, callback):
	with open(file_path) as file_to_parse:
		reader = csv.reader(file_to_parse, delimiter=',')
		next(reader, None)  # skip the headers
		for line in reader:
			if line and not line[0].startswith("#"):
				callback(line)

def parse_city():
	read_csv_by_line( get_city_data_path(), parse_city_callback
	)

def parse_poi():
	read_csv_by_line( get_city_data_path(), parse_city_callback
	)

ID = "_id"

def node_clustering_on_position(nrNodes, nrBs, distanceBetweenGW, row_column_size_x, row_column_size_y, graphic):
	print("node_clustering_on_position")
	'''AF_ADD
	Transform the nodes file from lorasim format to the one used by this clustering function
	In output the file will ahve the same format of the one 
	'''
	#distanceBetweenGW = 12000
	#nrNodes = 10000

	#row_column_size = 8

	#input_file_path = 'simulation_files/' + str(nrNodes) + '-nodes-raw-BwGw-' + str(int(distanceBetweenGW)) + '-BwGN-' + str(int(distanceBetweenGW)) + '-mygen.txt'
	input_file_path = 'simulation_files/' + str(nrNodes) + '-nodes-raw.txt'
	output_file_path = 'simulation_files/clustered_on_position/' + str(nrNodes) + '-nodes-raw-BwGw-' + str(int(distanceBetweenGW)) + '-BwGN-' + str(int(distanceBetweenGW)) + '-cluster-position-format.txt'
	PATH_NAME_2 = 'simulation_files/clustered_on_position/' + str(nrNodes)+ '-nodes-raw-BwGw-' + str(int(distanceBetweenGW)) + '-BwGN-' + str(int(distanceBetweenGW)) + '-clustered.txt'

	'''AF_ADD for the basestations split'''
	#input_file_path_bs = 'simulation_files/' + str(nrBs) + '-basestation-BwGw-' + str(int(distanceBetweenGW)) + '-BwGN-' + str(int(distanceBetweenGW)) + '-mygen.txt'
	#input_file_path_bs = 'simulation_files/basestation-' + str(int(distanceBetweenGW)) + '-mygen-' + str(int(nrNodes/1000)) + 'K-nodes.txt'
	input_file_path_bs = 'simulation_files/basestation-' + str(int(distanceBetweenGW)) + '.txt'
	output_file_path_bs = 'simulation_files/clustered_on_position/' + str(nrBs) + '-basestation-BwGw-' + str(int(distanceBetweenGW)) + '-BwGN-' + str(int(distanceBetweenGW)) + '-cluster-position-format.txt'
	PATH_NAME_2_bs = 'simulation_files/clustered_on_position/' + str(nrBs) + '-basestation-BwGw-' + str(int(distanceBetweenGW)) + '-BwGN-' + str(int(distanceBetweenGW)) + '-clustered.txt'

	header = "nodeID,posX,posY,"

	with open(output_file_path, 'w') as outputfile:
		with open(input_file_path, 'r') as nfile:
			for i in range(0, nrNodes):
				line = nfile.readline()
				tranformed_line = line.strip().replace(' ', ',')

				#At the first line count the number of existing basestations to create the header
				if(i==0):
					#print(tranformed_line)
					array_of_fields = tranformed_line.split(',')
					#print(array_of_fields)
					gateways_counter = 0
					for i in range(3, len(array_of_fields)):
						if(i%2==0):
							gateways_counter+=1
							header = header+"RSSI"+str(gateways_counter)+",SF"+str(gateways_counter)+","

					# print(header)
					# header = header.removesuffix(",")
					header = header[:-1]
					# pathlib.Path(header).with_suffix(",")
					# sys.exit()

					outputfile.write(header)
					outputfile.write("\n")
					print("The current file has "+str(gateways_counter)+" gateways")
				
				outputfile.write(tranformed_line)
				outputfile.write("\n")

	'''AF_ADD for the basestations split'''
	header_bs = "posX,posY,nodeID"

	with open(output_file_path_bs, 'w') as outputfile_bs:
		with open(input_file_path_bs, 'r') as nfile_bs:
			outputfile_bs.write(header_bs)
			outputfile_bs.write("\n")
			for i in range(0, nrBs):
				line = nfile_bs.readline()
				tranformed_line = line.strip().replace(' ', ',')
				outputfile_bs.write(tranformed_line)
				outputfile_bs.write("\n")

	dataAnalysis(nrNodes, output_file_path, row_column_size_x, row_column_size_y, graphic, PATH_NAME_2)
	'''AF_ADD for the basestations split, comment this to avoid the basestations split'''
	dataAnalysis(nrBs, output_file_path_bs, row_column_size_x, row_column_size_y, graphic, PATH_NAME_2_bs)

'''
arrayOfEXPLoRaCDdivisions_x = [3, 5, 5, 5]
arrayOfEXPLoRaCDdivisions_y = [2, 3, 5, 10]
'''
# || #Nodes || #Bsestations || Distance-bs-bs || x-split || y-split || graphic-flag ||
# node_clustering_on_position(500000, 1000, 12000, 2, 4, True)
node_clustering_on_position(1000, 200, 12000, 15, 15, True)