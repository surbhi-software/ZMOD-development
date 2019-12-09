import requests
import json
import os
import sys
mainUrl = 'http://localhost:8000/api/v1'

def loadModelToZmk(filePath):
    url=mainUrl+'/models'
    param={'filePath':filePath}
    res=requests.post(url,param)
    res=json.loads(res.text)
    return res

def scoreData(idForData, filePath):
    url=mainUrl+'/models/'+idForData+'/score'
    param={'filePath':filePath}
    res=requests.post(url,param)
    res=json.loads(res.text)
    return res

print('\nTest for DNN model\n')

filePath =  os.getcwd()+'/'+'testUseCase/supportdata/' +'WeldModelGen.pmml'
print('Loading model for scoring....')
resp = loadModelToZmk(filePath)
print(resp)
if not resp['keytoModel']:
    print('>>>> Model load failed')
    sys.exit(1)
print('>>>> Model load successful')

idForData = resp['keytoModel']
print('Key to the model is : ',idForData,'')
dataPath = os.getcwd()+'/'+'testUseCase/supportdata/'+'TwoBadwithpins103.png'
dataPath2 = os.getcwd()+'/'+'testUseCase/supportdata/'+'TwoBadwithpins105.png'
print('Scoring first data')
resp2=scoreData(idForData, dataPath)
print('Response is : ',resp2,'')
print('Scoring second data')
resp3=scoreData(idForData,dataPath2)
print('Response is : ',resp3,'')


print('\nTest for sklearn model\n')

filePath = os.getcwd()+'/'+'testUseCase/supportdata/'+'from_sklearn.pmml'
print('Loading model for scoring....')
resp = loadModelToZmk(filePath)
print(resp)
if not resp['keytoModel']:
    print('>>>> Model load failed')
    sys.exit(1)
print('>>>> Model load successful')

idForData = resp['keytoModel']
print('Key to the model is : ',idForData,'')
dataPath = os.getcwd()+'/'+'testUseCase/supportdata/'+'irisTest.csv'
print('Scoring first data')
resp2=scoreData(idForData, dataPath)
print('Response is : ',resp2,'')

