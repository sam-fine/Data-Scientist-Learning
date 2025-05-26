---
attachments: [Clipboard_2023-06-13-16-39-24.png, Clipboard_2023-06-13-16-48-19.png]
tags: [Machine Learning Algorithms]
title: K-Means (Clustering)
created: '2023-06-13T08:28:50.429Z'
modified: '2024-01-02T10:02:24.473Z'
---

# K-Means (Clustering)

* Aimed to find a structure to a dataset by finding clusters.
* K refers to the pre-defined parameter informing us on the number of clusters.

## Theory
1. First step is to identify two random points which we will define as the centre of the clusters. These are the centroids.
![](C:\Users\sfine\Documents\Notes\attachments\k_means_images\first_step.png)       
2. We identify which centroid each data point is closest to, and label the points accordingly:     
![](C:\Users\sfine\Documents\Notes\attachments\k_means_images\second_step.png)      
3. We adjust the locations of the centroids to the centre of each cluster:
![](C:\Users\sfine\Documents\Notes\attachments\k_means_images\third_step.png)
4. Repeat until none of the data points change the locations of the clusters:
![](C:\Users\sfine\Documents\Notes\attachments\k_means_images\final.png)
## What K value to use?
* Sometimes we have many dimensions and it is hard to visualise how many clusters we want.
* We use the 'Elbow Method'
Start with a value of k, e.g. 2 and we calculate the Sum of Squared Errors (SSE), also referred to as the inertia, for each cluster.
<center>$SSE_1 = \displaystyle\sum_{i=0}^n dist(x_i-c_1)^2$</center>
Where $c_1$ is the location of the centroid in cluster 1.

Total Sum of Squared Errors:
<center>$SSE = SSE_1 + SSE_2 + ... + SSE_k$</center>


Note: we square distances just to negate negative values.\
* Then we draw the SSE values:

![](C:\Users\sfine\Documents\Notes\attachments\k_means_images\elbow_method_k_eleven.png)

* Here there is k=11 clusters.
* As k increases, the error decreases.
* Find where the 'elbow' is, i.e. where the graphs gradient changes noticably. Here it is k=4

## Coding
We have data for the salary income with respective ages:
```python
from sklearn.cluster import KMeans
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from matplotlib import pyplot as plt

income = pd.read_csv('income_data.csv')
income.head()
```
| |Name|Age|Income($)|
| ----------- | ----------- | ----------- |----------- |
|0|Rob|27	|70000|
|1|Michael|29|90000|
|2|Mohan|29|61000|
|3|Ismail|28|60000|
|4|Kory|42|150000|
```python
plt.scatter(income['Age'], income['Income($)'])
plt.show()
```
![](C:\Users\sfine\Documents\Notes\attachments\k_means_images\initial_scatter.png)
We can visually see 3 clusters so k=3
```python
km = KMeans(n_clusters=3) #Initialise the algorithm
predicted_cluster = km.fit_predict(income[['Age','Income($)']])
```
array([2, 2, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0])

We have run k-means algorithm on the income data and assigned a cluster to each point.
Visualise this array:
```python
income['cluster'] = predicted_cluster
income.head()
```
| |Name|Age|Income($)|Cluster|
| ----------- | ----------- | ----------- |----------- |----------- |
|0|Rob|27	|70000|2|
|1|Michael|29|90000|2|
|2|Mohan|29|61000|0|
|3|Ismail|28|60000|0|
|4|Kory|42|150000|1|
```python
df1 = income[income.cluster==0]
df2 = income[income.cluster==1]
df3 = income[income.cluster==2]
plt.scatter(df1['Age'], df1['Income($)'], color='green')
plt.scatter(df2['Age'], df2['Income($)'], color='red')
plt.scatter(df3['Age'], df3['Income($)'], color='black')
plt.xlabel('Age')
plt.ylabel('Income($)')
```
![](C:\Users\sfine\Documents\Notes\attachments\k_means_images\scale_wrong.png)
* We can clearly see from the graph that they are not grouped well. The black and green dots are not grouped together. 
* This is due to the scale on the axis. (range on both are very different)
**Scaling**
```python
scaler = MinMaxScaler() # will make scale between 0 and 1
scaler.fit(income[['Income($)']])
income['Income($)']=scaler.transform(income[['Income($)']])

scaler.fit(income[['Age']])
income['Age']=scaler.transform(income[['Age']])
income.head()
```
| |Name|Age|Income($)|Cluster|
| ----------- | ----------- | ----------- |----------- |----------- |
|0|Rob|0.058824		|0.213675|2|
|1|Michael|0.176471|0.384615|2|
|2|Mohan|0.176471|0.136752|0|
|3|Ismail|0.117647|0.128205|0|
|4|Kory|0.941176|0.897436|1|

Re-evaluate our k-means algorithm:
```python
km = KMeans(n_clusters=3) #Initialise the algorithm
predicted_cluster = km.fit_predict(income[['Age','Income($)']])
income['cluster'] = predicted_cluster
df1 = income[income.cluster==0]
df2 = income[income.cluster==1]
df3 = income[income.cluster==2]
plt.scatter(df1['Age'], df1['Income($)'], color='green')
plt.scatter(df2['Age'], df2['Income($)'], color='red')
plt.scatter(df3['Age'], df3['Income($)'], color='black')
plt.xlabel('Age')
plt.ylabel('Income($)')
```
![](C:\Users\sfine\Documents\Notes\attachments\k_means_images\scale_correct.png)
**Plot Centroids**
```python
centroid_loc = km.cluster_centers_
```
array([[0.72268908, 0.8974359 ],
       [0.1372549 , 0.11633428],
       [0.85294118, 0.2022792 ]])

```python
km = KMeans(n_clusters=3) #Initialise the algorithm
predicted_cluster = km.fit_predict(income[['Age','Income($)']])
income['cluster'] = predicted_cluster
df1 = income[income.cluster==0]
df2 = income[income.cluster==1]
df3 = income[income.cluster==2]
plt.scatter(df1['Age'], df1['Income($)'], color='green')
plt.scatter(df2['Age'], df2['Income($)'], color='red')
plt.scatter(df3['Age'], df3['Income($)'], color='black')
plt.scatter(centroid_loc[:,0], centroid_loc[:,1], color = 'purple')
plt.xlabel('Age')
plt.ylabel('Income($)')
```
![](C:\Users\sfine\Documents\Notes\attachments\k_means_images\plot_with_centroids.png)

**Using Elbow Plot**
When it is not obvious how many clusters to use, we calculate the SSE values and work out for which value of k the 'elbow' occurs.
```python
k_range = range(1,10)
sse=[]
for k in k_range:
  km = KMeans(n_clusters=k)
  km.fit(income[['Age','Income($)']])
  sse.append(km.inertia_)
plt.xlabel('K')
plt.ylabel('SSE')
plt.plot(k_range, sse)
```
![](C:\Users\sfine\Documents\Notes\attachments\k_means_images\elbow.png)
We can see the elbow is at 3.

Source: 
[https://www.youtube.com/watch?v=EItlUEPCIzM]



