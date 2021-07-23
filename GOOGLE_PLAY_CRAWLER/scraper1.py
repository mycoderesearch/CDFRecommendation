from google_play_scraper import app

result = app(
    'com.woolworths',
    lang='ar', # defaults to 'en'
    country='SA', # defaults to 'us'
)

print(result)
# import urllib.request
# import os
# import wget


# with urllib.request.urlopen('https://analytics.usa.gov/') as response:
#    html = response.read()
#    soup = BeautifulSoup(html, "lxml")
#    for link in soup.find_all('a'):
#    	print(link.get('herf'))

## RENAMING RESTRICTED FILES

# newname=""
# filename = "com9.callbackstaffing.app_review.txt"
# filename= filename.split('.')
# if filename[0]=="com1" or filename[0]=="com2" or filename[0]=="com9":
# 	filename[0]= "comX"
# for x in filename:
# 	newname=newname+str(x)+"."
# print(newname)

# path_apk_dir='C:\\Users\\mdkafiluddin\\Desktop\\'
# app_url = 'https://play.google.com/store/apps/details?id=com.canva.editor&hl=en&gl=us'

# wget.download(app_url,path_apk_dir)
