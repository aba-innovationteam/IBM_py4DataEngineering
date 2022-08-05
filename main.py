#%%

# IMPORT LIBRARIES
import pandas as pd
import glob
import xml.etree.ElementTree as ET
from datetime import datetime
import zipfile as z
import requests
import os.path



#%%

# DOWNLOAD THE FILE
url = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-PY0221EN-SkillsNetwork/labs/module%206/Lab%20-%20Extract%20Transform%20Load/data/source.zip'
r = requests.get(url, allow_redirects=True)
print(r.headers.get('content-type'))

#%%

# SAVE THE ZIP FILE
save_path = 'data/raw/'
file_name = "source.zip"
complete_name = os.path.join(save_path, file_name)

open(complete_name, "wb").write(r.content)

#%%

# UNZIP THE FILE
root = z.ZipFile(complete_name)
root.extractall('data/extracted/')
root.close()
#%%

# SET PATHS
tmpfile = "temp.tmp"               # file used to store all extracted data
logfile = "logfile.txt"            # all event logs will be stored in this file
targetfile = "data/ETL/transformed_data.csv"   # file where transformed data is stored
#%%

# CSV EXTRACT FUNCTION
def extract_from_csv(file_to_process):
    dataframe = pd.read_csv(file_to_process)
    return dataframe

# JSON EXTRACT FUNCTION
def extract_from_json(file_to_process):
    dataframe = pd.read_json(file_to_process,lines=True)
    return dataframe

# XML EXTRACT FUNCTION
def extract_from_xml(file_to_process):
    dataframe = pd.DataFrame(columns=["name", "height", "weight"])
    tree = ET.parse(file_to_process)
    root = tree.getroot()
    for person in root:
        name = person.find("name").text
        height = float(person.find("height").text)
        weight = float(person.find("weight").text)
        dataframe = dataframe.append({"name":name, "height":height, "weight":weight}, ignore_index=True)
    return dataframe
#%%

def extract():
    extracted_data = pd.DataFrame(columns=['name','height','weight']) # create an empty data frame to hold extracted data

    #process all csv files
    for csvfile in glob.glob("data/extracted/*.csv"):
        extracted_data = extracted_data.append(extract_from_csv(csvfile), ignore_index=True)

    #process all json files
    for jsonfile in glob.glob("data/extracted/*.json"):
        extracted_data = extracted_data.append(extract_from_json(jsonfile), ignore_index=True)

    #process all xml files
    for xmlfile in glob.glob("data/extracted/*.xml"):
        extracted_data = extracted_data.append(extract_from_xml(xmlfile), ignore_index=True)

    return extracted_data
#%%

# TRANSFORM
def transform(data):
        #Convert height which is in inches to millimeter
        #Convert the datatype of the column into float
        #data.height = data.height.astype(float)
        #Convert inches to meters and round off to two decimals(one inch is 0.0254 meters)
        data['height'] = round(data.height * 0.0254,2)

        #Convert weight which is in pounds to kilograms
        #Convert the datatype of the column into float
        #data.weight = data.weight.astype(float)
        #Convert pounds to kilograms and round off to two decimals(one pound is 0.45359237 kilograms)
        data['weight'] = round(data.weight * 0.45359237,2)
        return data
#%%

#%%
# LOADING
def load(targetfile, data_to_load):
    data_to_load.to_csv(targetfile)

# LOGGING
def log(message):
    timestamp_format = '%Y-%h-%d-%H:%M:%S' # Year-Monthname-Day-Hour-Minute-Second
    now = datetime.now() # get current timestamp
    timestamp = now.strftime(timestamp_format)
    with open("data/ETL/logfile.txt","a") as f:
        f.write(timestamp + ',' + message + '\n')

#%%
log("ETL Job Started")
log("Extract phase Started")
extracted_data = extract()
log("Extract phase Ended")
extracted_data
#%%
#%%

log("Transform phase Started")
transformed_data = transform(extracted_data)
log("Transform phase Ended")
transformed_data
#%%
#%%
log("Load phase Started")
load(targetfile, transformed_data)
log("Load phase Ended")

log("ETL Job Ended")
#%%
