from math import*

file_path_appA='C:/Users/mdkafiluddin/Desktop/Research/[1]DATASET_v1/Category/COMMUNICATION/Experiment_1/Five_Apps/com.viber.voip/Features/Resource/com.viber.voip_resource_features.txt'
file_path_appB='C:/Users/mdkafiluddin/Desktop/Research/[1]DATASET_v1/Category/COMMUNICATION/Experiment_1/Five_Apps/com.whatsapp/Features//Resource/com.whatsapp_resource_features.txt'

f_read_appA=open(file_path_appA, 'r')
f_read_appB=open(file_path_appB, 'r')

contents_appA=f_read_appA.readlines()
contents_appB=f_read_appB.readlines()

# print(contents_appA)




def jaccard_similarity(x,y):
 
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    return intersection_cardinality/float(union_cardinality)
 
print(jaccard_similarity(contents_appA,contents_appB))
# print(jaccard_similarity([0,1,2,5,6],[0,2,3,5,7,9]))





f_read_appA.close()
f_read_appB.close()