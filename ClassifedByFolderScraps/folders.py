import os
import pandas as pd



df = pd.read_excel('C:/Users/hokej/Desktop/ai-job-title-area-classification-master/ClassfiedFolders/JobDepartments.xlsx',engine='openpyxl')

for index, row in df.iterrows():
    os.mkdir(row["department"])
