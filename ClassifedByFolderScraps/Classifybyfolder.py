import os
import json
import shortuuid





for filename in os.listdir('C:/Users/hokej/Desktop/ai-job-title-area-classification-master/TestDestination'):
    filenamefull='C:/Users/hokej/Desktop/ai-job-title-area-classification-master/TestDestination/'+filename
    with open(filenamefull,encoding="utf8") as f:
        content = json.load(f)
        department=content["Department2"]
        name = content["Title"].translate({ord(c): None for c in '!@#$\/"'}).strip()[:35]+" "+shortuuid.uuid()+".json"
        #print(name)
        jsonname='C:/Users/hokej/Desktop/ai-job-title-area-classification-master/ClassfiedFolders/'+department+'/'+name
        with open(jsonname, 'w',encoding='utf-8') as file:
            json.dump(content,file)
