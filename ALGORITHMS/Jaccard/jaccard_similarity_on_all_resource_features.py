from math import*
import os
from pathlib import Path
import sys
import shutil
import csv



# Get directory name
path_apk_dir='C:\\Users\\mdkafiluddin\\Desktop\\Research\\[1]DATASET_v1\\Category\\COMMUNICATION\\Experiment_2\\All_APK_Manifest\\All_Resource_Features'
# path_apk_manifest_dir='C:\\Users\\mdkafiluddin\\Desktop\\Research\\[1]DATASET_v1\\Category\\COMMUNICATION\\Experiment_2\\All_APK_Manifest'
# path_temp_dir ='C:\\Users\\mdkafiluddin\\Desktop\\Research\\[1]DATASET_v1\\Category\\COMMUNICATION\\Experiment_2\\temp'


#Check if the directory exists of not create NEW directory
if not os.path.exists(path_apk_dir):
	write_dir=os.mkdir(path_apk_dir)

#Check if the directory exists of not create NEW directory
# if not os.path.exists(path_apk_manifest_dir):
# 	write_dir=os.mkdir(path_apk_manifest_dir)

#Check if the directory exists of not create NEW directory
# if not os.path.exists(path_temp_dir):
# 	write_dir=os.mkdir(path_temp_dir)




file_path_appA='C:\\Users\\mdkafiluddin\\Desktop\\Research\\[1]DATASET_v1\\Category\\COMMUNICATION\\Experiment_2\\All_APK_Manifest\\All_Resource_Features\\com.facebook.orca_resource_features.txt'
# file_path_appB='C:/Users/mdkafiluddin/Desktop/Research/[1]DATASET_v1/Category/COMMUNICATION/Experiment_1/Five_Apps/com.whatsapp/Features//Resource/com.whatsapp_resource_features.txt'

# f_read_appA=open(file_path_appA, 'r')
# f_read_appB=open(file_path_appB, 'r')

# contents_appA=f_read_appA.readlines()
# contents_appB=f_read_appB.readlines()

# print(contents_appA)




def jaccard_similarity(x,y):
 
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    return intersection_cardinality/float(union_cardinality)
 

# print(jaccard_similarity([0,1,2,5,6],[0,2,3,5,7,9]))





# f_read_appA.close()
# f_read_appB.close()











# def read_and_download_all_comm_app_apk_url():
# 	f_csv = csv.reader(open('C:/Users/mdkafiluddin/Desktop/Research/[1]DATASET_v1/Category/COMMUNICATION/Experiment_2/all_communication_apk_url.csv', 'r', encoding="unicode_escape"))
# 	count=0		#ignore first line
# 	for line in f_csv:
# 		if count==1:
# 			app_url=line[3]
# 			wget.download(app_url,path_apk_dir)
# 			print(app_url)
# 		count=1

# read_and_download_all_comm_app_apk_url()

# Execute CMD command to RUN apktool
def run_cmd_to_extract_apk(_apk_file_name):
	# create_temp_dir()
	path_apk_file= os.path.join(path_apk_dir, _apk_file_name)
	# print(path_apk_file)
	f_read_appA=open(file_path_appA, 'r')
	f_read_appB=open(path_apk_file, 'r')

	contents_appA=f_read_appA.readlines()
	contents_appB=f_read_appB.readlines()
	print(jaccard_similarity(contents_appA,contents_appB))


# Try to remove Temporary directory tree; if failed show an error using try...except on screen
# def remove_temp_directory():
# 	try:
# 	    shutil.rmtree(path_temp_dir)
# 	except OSError as e:
# 	    print ("Error: %s - %s." % (e.filename, e.strerror))


# run_cmd_to_extract_apk("com.tomasperez.dictionary.pkg-4.apk")

# """ READ Entire FILES from THE DIRECTORY"""
# """+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"""

for apk_file in os.listdir(path_apk_dir):
	print(apk_file)
	run_cmd_to_extract_apk(apk_file)
	print('+++++++++++++++++++++++')