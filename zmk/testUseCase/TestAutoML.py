import requests
import json
import os

def autoMlSendData(filePath):
    url='http://localhost:8000/api/v1/trainAutoMLModel'
    param={'filePath':filePath}
    res=requests.get(url,param)
    kk=res.text
    tempa=json.loads(kk)
    return tempa


def autoMlTrain(filePath, idForData):
    url2='http://localhost:8000/api/v1/trainAutoMLModel'
    true=True
    false=False
    dataPreprocessingsteps={"data":[{"position":1,"variable":"mpg","dtype":"float64","missing_val":0,"changedataType":"Continuous","imputation_method":"None","data_transformation_step":"None","use_for_model":true},
    {"position":2,"variable":"cylinders","dtype":"int64","missing_val":0,"changedataType":"Continuous","imputation_method":"None","data_transformation_step":"None","use_for_model":true},
    {"position":3,"variable":"displacement","dtype":"float64","missing_val":0,"changedataType":"Continuous","imputation_method":"None","data_transformation_step":"None","use_for_model":true},
    {"position":4,"variable":"horsepower","dtype":"float64","missing_val":6,"changedataType":"Continuous","imputation_method":"Mean","data_transformation_step":"None","use_for_model":true},
    {"position":5,"variable":"weight","dtype":"int64","missing_val":0,"changedataType":"Continuous","imputation_method":"None","data_transformation_step":"None","use_for_model":true},
    {"position":6,"variable":"acceleration","dtype":"float64","missing_val":0,"changedataType":"Continuous","imputation_method":"None","data_transformation_step":"None","use_for_model":true},
    {"position":7,"variable":"model year","dtype":"int64","missing_val":0,"changedataType":"Categorical","imputation_method":"None","data_transformation_step":"None","use_for_model":true},
    {"position":8,"variable":"origin","dtype":"int64","missing_val":0,"changedataType":"Categorical","imputation_method":"None","data_transformation_step":"One Hot Encoding","use_for_model":true},
    {"position":9,"variable":"car name","dtype":"object","missing_val":0,"changedataType":"Categorical","imputation_method":"None","data_transformation_step":"None","use_for_model":false}
    ],"problem_type":"Regression","target_variable":"mpg","idforData":idForData,'newPMMLFileName':'xyz.pmml','filePath':filePath,"parameters": []}
    headers = {'content-type': 'application/json'}
    res2=requests.post(url2,headers=headers,json=dataPreprocessingsteps)


def checkStatusOfTraining(idForData):
    url3='http://localhost:8000/api/v1/runningTasks/'+idForData
    res3=requests.get(url3)
    tempro=json.loads(res3.text)
    return tempro

print('\n\n:::::::::::::::: Test for AutoML :::::::::::::::: \n\n')

path = os.getcwd()+'/'+'testUseCase/supportdata/' 
path = path+'/'+'mpg_data_example.csv'
resp = autoMlSendData(path)
idforData = resp['idforData']

print('>>>> Data sent Sucessfully')

autoMlTrain(path, idforData)

print('>>>> Auto training is in progress')

respp = checkStatusOfTraining(idforData)
import time, sys
while(respp['status'] != 'Complete'):
    time.sleep(15)
    respp = checkStatusOfTraining(idforData)
    if respp['status'] == 'Training Failed':
        print('>>>> Training Failed')
        print(respp)
        sys.exit(1)
    else:
        print('>>>> ',respp['status'],'')
    time.sleep(2)

