import requests
import json
import os

fp=os.getcwd()+'/'+'testUseCase/supportdata/'+'irisNN.pmml'
fp2=os.getcwd()+'/'+'testUseCase/expandable/'+'irisNN.pmml'
pmmlRead=open(fp,'r').read()

ppp="'dataUrl':'" + os.getcwd()+'/'+'testUseCase/supportdata/iris_new.csv'+"'"
ppp=ppp.replace('\\','/')
print (ppp)
pmmlRead=pmmlRead.replace("'dataUrl': ''",ppp)

with open(fp2,'w') as fi:
    fi.write(pmmlRead)


def nnTrain():
    url2='http://localhost:8000/api/v1/trainNNModel'
    payload={"batchSize":15,
            "epoch":10,
            "stepPerEpoch":10,
            "learningRate":0.001,
            "loss":"categorical_crossentropy",
            "metrics":["accuracy"],
            "optimizer":"Adam",
            "testSize":0.3,
            "scriptOutput":"NA",
            "problemType":"classification",
            "filePath":fp2,
            "tensorboardLogFolder":os.getcwd()+'/'+'testUseCase/expandable/',
            "tensorboardUrl":'',
            'dataFolder':''}

    jj2=requests.post(url2,data=json.dumps(payload))
    return jj2


def checkStatusOfTraining(idForData):
    url3='http://localhost:8000/api/v1/runningTasks/'+idForData
    res3=requests.get(url3)
    tempro=json.loads(res3.text)
    return tempro

print('\n\n:::::::::::::::: Test for DNN :::::::::::::::: \n\n')

resp = nnTrain()
idforData = json.loads(resp.text)['idforData']



print('>>>> Training is in progress')

respp = checkStatusOfTraining(idforData)
import time, sys
while(respp['status'] != 'PMML file Successfully Saved'):
    time.sleep(15)
    respp = checkStatusOfTraining(idforData)
    if respp['status'] == 'Training Failed':
        print('>>>> Training Failed')
        print(respp)
        sys.exit(1)
    else:
        print('>>>> ',respp['status'],)
    time.sleep(2)

