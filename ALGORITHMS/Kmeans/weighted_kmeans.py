# k_means.py
# k-means clustering demo
# Anaconda 4.1.1
#https://visualstudiomagazine.com/articles/2018/03/27/clustering-with-k-means-using-python.aspx

import numpy as np

def mm_normalize(data):
  # min-max
  (rows, cols) = data.shape  # (20,4) for demo
  mins = np.zeros(shape=(cols), dtype=np.float32)
  maxs = np.zeros(shape=(cols), dtype=np.float32)
  for j in range(cols):
    mins[j] = np.min(data[:,j])
    maxs[j] = np.max(data[:,j])

  result = np.copy(data)
  for i in range(rows):
    for j in range(cols):
      result[i,j] = (data[i,j] - mins[j]) / (maxs[j] - mins[j])
  return (result, mins, maxs)

def distance(item, mean):
  # Euclidean distance from a data item to a mean
  sum = 0.0
  w1=0.60#Functional_simi - Products Offered 60%
  w2=0.39#Resource_simi- Resource used 39%
  w3=0.39#Sentiments - Customer Perception of the firm 39%
  w4=0.39#Ratings-Customer Perception of the firm 39%
  w5=0.28#Downloads - Competitor Size 28%
  #When you need to put weight in its all dimensions: total 5 dimensions [0-4]
  sum += w1*((item[0] - mean[0]) ** 2) + w2*((item[1] - mean[1]) ** 2)+ w3*((item[2] - mean[2]) ** 2)+ w4*((item[3] - mean[3]) ** 2)+ w5*((item[4] - mean[4]) ** 2)
  # sum += w1*((item[0] - mean[0]) ** 2) + w2*(((item[1] - mean[1]) ** 2)+ ((item[2] - mean[2]) ** 2)+ ((item[3] - mean[3]) ** 2)+ ((item[4] - mean[4]) ** 2))
  
  #When you do not need to put weight-Its for plain K-means
 
  # dim = len(item)
  # for j in range(dim):
  #   sum += (item[j] - mean[j]) ** 2
  

  return np.sqrt(sum)

def update_clustering(norm_data, clustering, means):
  # given a (new) set of means, assign new clustering
  # return False if no change or bad clustering
  n = len(norm_data)
  k = len(means)

  new_clustering = np.copy(clustering)  # proposed new clustering
  distances = np.zeros(shape=(k), dtype=np.float32)  # from item to each mean

  for i in range(n):  # walk thru each data item
    for kk in range(k):
      distances[kk] = distance(norm_data[i], means[kk])  
    new_id = np.argmin(distances)
    new_clustering[i] = new_id
  
  if np.array_equal(clustering, new_clustering):  # no change so done
    return False

  # make sure that no cluster counts have gone to zero
  counts = np.zeros(shape=(k), dtype=np.int)
  for i in range(n):
    c_id = clustering[i]
    counts[c_id] += 1
  
  for kk in range(k):  # could use np.count_nonzero
    if counts[kk] == 0:  # bad clustering
      return False

  # there was a change, and no counts have gone 0
  for i in range(n):
   clustering[i] = new_clustering[i]  # update by ref
  return True

def update_means(norm_data, clustering, means):
  # given a (new) clustering, compute new means
  # assumes update_clustering has just been called
  # to guarantee no 0-count clusters
  (n, dim) = norm_data.shape
  k = len(means)
  counts = np.zeros(shape=(k), dtype=np.int)
  new_means = np.zeros(shape=means.shape, dtype=np.float32)  # k x dim
  for i in range(n):  # walk thru each data item
    c_id = clustering[i]
    counts[c_id] += 1
    for j in range(dim):
      new_means[c_id,j] += norm_data[i,j]  # accumulate sum

  for kk in range(k):  # each mean
    for j in range(dim):
      new_means[kk,j] /= counts[kk]  # assumes not zero

  for kk in range(k):  # each mean
    for j in range(dim):
      means[kk,j] = new_means[kk,j]  # update by ref

def initialize(norm_data, k):
  (n, dim) = norm_data.shape
  clustering = np.zeros(shape=(n), dtype=np.int)  # index = item, val = cluster ID
  for i in range(k):
    clustering[i] = i
  for i in range(k, n):
    clustering[i] = np.random.randint(0, k) 

  means = np.zeros(shape=(k,dim), dtype=np.float32)
  update_means(norm_data, clustering, means)
  return(clustering, means) 
  
def cluster(norm_data, k):
  (clustering, means) = initialize(norm_data, k)

  ok = True  # if a change was made and no bad clustering
  max_iter = 100
  sanity_ct = 1
  while sanity_ct <= max_iter:
    ok = update_clustering(norm_data, clustering, means)  # use new means
    if ok == False:
      break  # done
    update_means(norm_data, clustering, means)  # use new clustering
    sanity_ct += 1

  return clustering

def display(raw_data, clustering, k):
  (n, dim) = raw_data.shape
  print("-------------------")
  for kk in range(k):  # group by cluster ID
    for i in range(n):  # scan the raw data
      c_id = clustering[i]  # cluster ID of curr item
      if c_id == kk:  # curr item belongs to curr cluster so . . 
        print("%4d " % i, end=""); print(raw_data[i])
    print("-------------------")  

def main():
  print("\nBegin k-means clustering\n")
  np.set_printoptions(precision=4, suppress=True)
  np.random.seed(2)

  # raw_data = np.loadtxt("C:/Users/mdkafiluddin/Desktop/test/kmeans1.csv", dtype=np.float32,
  #   delimiter=",", skiprows=0, usecols=[0,1,2,3,4])
  raw_data = np.loadtxt("C:/Users/mdkafiluddin/Desktop/test/kmeans1.csv", dtype=np.float32,
    delimiter=",", usecols=[0,1,2,3,4])
  (n, dim) = raw_data.shape
  print("The dimension of data-Matrix:",dim)

  print("Raw data:")
  for i in range(n):
    print("%4d " % i, end=""); print(raw_data[i])  

  (norm_data, mins, maxs) = mm_normalize(raw_data)
 
  k = 3
  print("\nClustering normalized data with k=" + str(k))
  clustering = cluster(norm_data, k)

  print("\nDone. Clustering:")
  print(clustering)

  print("\nRaw data grouped by cluster: ")
  display(raw_data, clustering, k)

  print("\nEnd k-means")

if __name__ == "__main__":
  main()
