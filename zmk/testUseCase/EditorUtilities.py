import requests
import json
import os
import random
import string


mainUrl=None

def generateId():
     id = ''.join(random.choices(population=string.ascii_letters,k=6))
     return id

def getListOfLayers():
     url=mainUrl+'api/v1/listOfLayers'
     jj=requests.get(url)
     outputfromAPI=jj.json()
     firstLayer = [i['name'] for i in outputfromAPI['layerinfo'][0]['layers']][0]
     return firstLayer

def getGlobalMemory():
     url2=mainUrl+'api/v1/pmml/getGlobal/memory'
     res6=requests.get(url2)
     tempJson=json.loads(res6.text)
     return tempJson

def prepareSamplePmml(filePath):
     ffOld = None
     with open('sampleEmpty.pmml') as ff:
          ffOld = ff.read()
     with open(filePath,'w') as fp:
          fp.write(ffOld)

def addArchitecture(projectId,filePath):
     # prepareSamplePmml(filePath)
     url2=mainUrl+'api/v1/pmml/'+projectId
     para={'filePath':filePath}
     res4=requests.post(url2,data=para)
     kaka=res4.text
     return kaka

def addTemplate(projectId,template):
     url2=mainUrl+'api/v1/pmml/'+projectId+'/layer'
     reqa={'projectID':projectId,'layerToUpdate':template}
     res4=requests.put(url2,json=reqa)
     kaka=res4.text
     return kaka

def addLayerOrSection(projectId,info):
     url2=mainUrl+'api/v1/pmml/'+projectId+'/layer'
     reqa={'layerToUpdate':info}
     res4=requests.put(url2,json=reqa)
     kaka=res4.text
     return kaka

def deleteLayerOrSection(projectId,info):
     url2=mainUrl+'api/v1/pmml/'+projectId+'/layer'
     reqa={'layerDelete':info}
     res6=requests.delete(url2,json=reqa)
     return(res6.text)