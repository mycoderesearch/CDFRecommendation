from google_play_scraper import app
import json
import csv
import os
from pathlib import Path
import sys
import shutil


# Get directory name
path_root_dir='..\\Research\\Dataset\\GooglePlay2020'

# Create directory for processing
def create_dir(path_dir):
	if not os.path.exists(path_dir):
		os.mkdir(path_dir)

def check_windows_reserve_names(app_name):
	newname=""
	# app_name = "com9.callbackstaffing.app_review.txt" (example app name)
	appname= app_name.split('.')
	# Need to check filename so that it does not fall in reserve names like COM1..COM9
	# https://social.technet.microsoft.com/Forums/windows/en-US/e22c021d-d188-4ff2-a4dd-b5d58d979c58/the-specified-device-name-is-invalid?forum=w7itprogeneral
	if appname[0]=="com1" or appname[0]=="com2" or appname[0]=="com3" or appname[0]=="com4" or appname[0]=="com5" or appname[0]=="com6" or appname[0]=="com7" or appname[0]=="com8" or appname[0]=="com9":
		appname[0]= "comX"
		for each_word in appname:
			newname=newname+str(each_word)+"."
			return newname
	else:
		return app_name


def save_reviews(review_file,result):
	with open(review_file, 'w+', encoding='utf-8', errors='ignore') as outfile:
		review_list = result['comments']
		for line in result['comments']:
			outfile.write("%s\n" % line)

def save_url(review_file,result):
	with open(review_file, 'w', encoding='utf-8', errors='ignore') as outfile:
		review_list = result['comments']
		for line in result['comments']:
			outfile.write("%s\n" % line)




def extract_appID(path_dir,filename):
	## For saving app List
	newfile=path_dir+'\\'+'allApp.txt'
	appList= open(newfile, 'w')

	## For saving app reviews
	review_dir=os.path.join(path_dir, "app_reviews") 
	create_dir(review_dir)
	
	## For saving all app url
	url_file = path_dir+'\\'+'app_url.csv'
	urlfile= open(url_file, 'w+', newline='', errors='ignore', encoding= 'utf-8')
	fieldnames = ['AppID', 'Title', 'Genre', 'URL']
	url_writer = csv.DictWriter(urlfile, fieldnames=fieldnames)
	url_writer.writeheader()

	## For saving all app description
	desc_file= path_dir+'\\'+'app_desc.csv'
	descfile= open(desc_file, 'w+', newline='', errors='ignore', encoding= 'utf-8')
	fieldnames = ['AppID', 'Title', 'Genre','Description', 'ReleasedDate', 'AndroidVersion', 'RecentChanges', 'LastUpdated', 'AppVersion', 'Price', 'Free', 'Size', 'ContainsAd', 'AdSupport', 'ContentRating', 'Developer', 'DeveloperEmail']
	desc_writer = csv.DictWriter(descfile, fieldnames=fieldnames)
	desc_writer.writeheader()

	## For saving all app popularity
	pop_file= path_dir+'\\'+'app_popularity.csv'
	popfile= open(pop_file, 'w+', newline='', errors='ignore', encoding= 'utf-8')
	fieldnames = ['AppID', 'Title', 'Genre','MinInstalls', 'AppRating', 'TotalRated', '1-Star', '2-Star', '3-Star', '4-Star', '5-Star', 'TotalReviews']
	pop_writer = csv.DictWriter(popfile, fieldnames=fieldnames)
	pop_writer.writeheader()

	count=0
	with open(filename, 'r', errors='ignore') as f:
		app_dict = json.load(f)

		for app_id in app_dict:
			try:
				result = app(app_id['appId'])
			except:
				result=None

			if result!= None:
				## Save Reviews per app
				app_name=check_windows_reserve_names(app_id['appId']) # Need to check filename so that it does not fall in reserve names like COM1..COM9
				review_file=review_dir+'\\'+app_name+'_review.txt'  
				save_reviews(review_file,result)

				## Write all URL
				url_writer.writerow({'AppID':result['appId'],'Title':result['title'], 'Genre':result['genre'], 'URL':result['url']})

				## Write all Description	
				desc_writer.writerow({'AppID':result['appId'],'Title':result['title'], 'Genre':result['genre'],'Description':result['description'], 'ReleasedDate':result['released'], 'AndroidVersion':result['androidVersion'], 'RecentChanges':result['recentChanges'], 'LastUpdated':result['updated'], 'AppVersion':result['version'], 'Price':result['price'], 'Free':result['free'], 'Size':result['size'], 'ContainsAd':result['containsAds'], 'AdSupport':result['adSupported'], 'ContentRating':result['contentRating'], 'Developer':result['developer'], 'DeveloperEmail':result['developerEmail']})
				
				## Write all Popularity Information
				if result['histogram']!= None:
					pop_writer.writerow({'AppID':result['appId'],'Title':result['title'], 'Genre':result['genre'],'MinInstalls':result['minInstalls'], 'AppRating':result['score'], 'TotalRated':result['ratings'], '1-Star':result['histogram'][0], '2-Star':result['histogram'][1], '3-Star':result['histogram'][2], '4-Star':result['histogram'][3], '5-Star':result['histogram'][4], 'TotalReviews':result['reviews']})	
				else:
					pop_writer.writerow({'AppID':result['appId'],'Title':result['title'], 'Genre':result['genre'],'MinInstalls':result['minInstalls'], 'AppRating':result['score'], 'TotalRated':result['ratings'], '1-Star':0, '2-Star':0, '3-Star':0, '4-Star':0, '5-Star':0, 'TotalReviews':result['reviews']})	

				#Write All the APP list in a seperate text file from the JSON file
				appList.write("%s\n" % app_id['appId'])

	appList.close()
	urlfile.close()
	descfile.close()
	popfile.close()



    		


# """ READ Entire FILES from THE DIRECTORY"""
# """+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"""

for category in os.listdir(path_root_dir):
	cat_dir= os.path.join(path_root_dir, category)            				#Check each category
	for collection in os.listdir(cat_dir):									#Check each collection type
		if collection.endswith(".json"):
			new_dir = collection.split('.')[0]								#Split file and take first part for directory
			path_dir= os.path.join(path_root_dir,category,new_dir)
			create_dir(path_dir)
			filename=os.path.join(path_root_dir,category,collection)
			extract_appID(path_dir,filename)
	print('+++++++++++++++++++++++')





# # csvfile= open(url_file, 'w+', newline='', errors='ignore', encoding= 'utf-8')
# # fieldnames = ['AppID', 'Title', 'Genre', 'URL']
# # writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
# # writer.writeheader()

# # desfile= open(desc_file, 'w+', newline='', errors='ignore', encoding= 'utf-8')
# # fieldnames = ['AppID', 'Title', 'Genre','Description', 'ReleasedDate', 'AndroidVersion', 'RecentChanges', 'LastUpdated', 'AppVersion', 'Price', 'Free', 'Size', 'ContainsAd', 'AdSupport', 'ContentRating', 'Developer', 'DeveloperEmail']
# # desc_writer = csv.DictWriter(desfile, fieldnames=fieldnames)
# # desc_writer.writeheader()

# popfile= open(pop_file, 'w+', newline='', errors='ignore', encoding= 'utf-8')
# fieldnames = ['AppID', 'Title', 'Genre','MinInstalls', 'AppRating', 'TotalRated', '1-Star', '2-Star', '3-Star', '4-Star', '5-Star', 'TotalReviews']
# pop_writer = csv.DictWriter(popfile, fieldnames=fieldnames)
# pop_writer.writeheader()


# with open(filename, 'r', errors='ignore') as f:
#         app_dict = json.load(f)

# for app_id in app_dict:
# 	# print(app_id['appId'])

# 	result = app(app_id['appId'],
# 	    # 'com.easybrain.block.puzzle.games',
# 	    lang='en', # defaults to 'en'
# 	    country='us' # defaults to 'us'
# 	)
# 	print("++++++++++++++++++++")
# 	# writer.writerow({'AppID':result['appId'],'Title':result['title'], 'Genre':result['genre'], 'URL':result['url']})
# 	# desc_writer.writerow({'AppID':result['appId'],'Title':result['title'], 'Genre':result['genre'],'Description':result['description'], 'ReleasedDate':result['released'], 'AndroidVersion':result['androidVersion'], 'RecentChanges':result['recentChanges'], 'LastUpdated':result['updated'], 'AppVersion':result['version'], 'Price':result['price'], 'Free':result['free'], 'Size':result['size'], 'ContainsAd':result['containsAds'], 'AdSupport':result['adSupported'], 'ContentRating':result['contentRating'], 'Developer':result['developer'], 'DeveloperEmail':result['developerEmail']})
# 	pop_writer.writerow({'AppID':result['appId'],'Title':result['title'], 'Genre':result['genre'],'MinInstalls':result['minInstalls'], 'AppRating':result['score'], 'TotalRated':result['ratings'], '1-Star':result['histogram'][0], '2-Star':result['histogram'][1], '3-Star':result['histogram'][2], '4-Star':result['histogram'][3], '5-Star':result['histogram'][4], 'TotalReviews':result['reviews']})


# 	print(result)
# 	print(count)
# 	count = count +1
# 	if count==3:
# 		break
