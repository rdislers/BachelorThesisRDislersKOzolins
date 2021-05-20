import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.datasets.samples_generator import make_blobs
from sklearn.cluster import KMeans
import os
import json
from tabulate import tabulate


####ARRAY SEQUENCES#####

#ArraySeq=['Java','JavaScript','Git','SQL','CSS','HTML','.NET','Cloud','React','Linux'] #Developers
#ArraySeq=['Microsoft Excel','SQL','Cloud','Linux','Microsoft Windows','Python','Azure','.NET','Java','Git'] #IT and Computer
#ArraySeq=['Microsoft Office','Microsoft Excel','Outlook','C#','SharePoint','SQL','VBA'] # Assistants
#ArraySeq=['Microsoft Office','Microsoft Excel','PHP','SAP','ERP','Confluence','.NET','SCM','CSS','HTML'] # Business Specialists
#ArraySeq=['Microsoft Office','SAP','Microsoft Excel','Cloud','ERP','Microsoft Windows','Linux','SAP ERP','DB2','Oracle']# Consultancy
#ArraySeq=['Microsoft Office','AutoCAD','Microsoft Excel','AutoDesk Revit','SOLIDWORKS','CAD','Python','CRM','Linux','JIRA']#Engineering
#ArraySeq=['Microsoft Office','Microsoft Excel','Facebook','CRM','Instagram','LinkedIn','Google Analytics','Photoshop','Google AdWords','HTML']#Marketing, Advertising and PR
#ArraySeq=['Microsoft Office','Microsoft Excel','AutoCAD','ERP','CAD','Facebook','CRM','AutoDesk Revit','SOLIDWORKS','Git'] # Middle Management
#ArraySeq=['Microsoft Office','Microsoft Excel','CRM','ERP','AutoCAD','Cloud','Outlook','SAP','Linux','Microsoft Windows'] # Sales and Procurement
ArraySeq=['Microsoft Excel','Microsoft Office','Spark','ERP','QlikView','SAP','Java','Scala','Microsoft Windows','SQL'] #Service


#X, y = make_blobs(n_samples=300, centers=4, cluster_std=0.60, random_state=0)
#arr = np.array([ [1, 2, 3, 4, 5] , [2,3,4,5,6] ])
#print(arr)
#plt.scatter(X[:,0], X[:,1])
#plt.show()


#Creating numpy array with each profile:
lstForArray=[]
for filename in os.listdir('C:/Users/hokej/Desktop/LinkedDataExtr/ClassifiedFoldersLinkedIn/Service'): #C:\Users\hokej\Desktop\LinkedDataExtr\ClassifiedFoldersLinkedIn\Developers
    filenamefull='C:/Users/hokej/Desktop/LinkedDataExtr/ClassifiedFoldersLinkedIn/Service/'+filename
    with open(filenamefull,encoding="utf8") as f:
        arraylst=[]
        content = json.load(f)
        TechSkillDict=content["TechSkills"]
    #    for skill in TechSkills:
    #        endorsment=SkillDict.get(skill,"Not Included")
    #        if endorsment=="Not Included":
    #            endorsment=0
    #        else:
    #            endorsment+=1
    #        TechSkillDict[skill]=endorsment
        for item in ArraySeq:
            arraylst.append(TechSkillDict.get(item,0))
        #print(arraylst)
        lstForArray.append(arraylst)

arr = np.array(lstForArray)
'''
wcss = []
for i in range(1, 16):
    kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
    kmeans.fit(arr)
    wcss.append(kmeans.inertia_)
plt.plot(range(1, 16), wcss)
plt.title('Elbow Method')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS')
plt.show()

'''
kmeans = KMeans(n_clusters=3, init='k-means++', max_iter=300, n_init=10, random_state=0)
pred_y = kmeans.fit_predict(arr)
tablist=[]
centers = kmeans.cluster_centers_







for i in centers:
    lst=i.tolist()
    newlst=[]
    for item in lst:
        newlst.append(int(item))
    tablist.append(newlst)
print(tabulate(tablist, headers=ArraySeq))


lst =kmeans.labels_.tolist()
cluster_0=0
cluster_1=0
cluster_2=0
cluster_3=0
cluster_4=0
cluster_5=0

for item in lst:
    if item==0:
        cluster_0+=1
    if item==1:
        cluster_1+=1
    if item==2:
        cluster_2+=1
    if item==3:
        cluster_3+=1
    if item==4:
        cluster_4+=1
    if item==5:
        cluster_5+=1

print(cluster_0,cluster_1,cluster_2,cluster_3,cluster_4,cluster_5)
