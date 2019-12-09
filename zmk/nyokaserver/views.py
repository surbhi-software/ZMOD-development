from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import View
import json

from datetime import datetime
from multiprocessing import Lock, Process

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view,schema

import requests, json,sys,subprocess, typing

from nyokaserver import nyokaUtilities,nyokaPMMLUtilities
from nyokaBase import PMML43Ext as pml
from nyokaserver.nyokaServerClass import NyokaServer


class PMMLView(APIView):
	http_method_names=['get']

	def dispatch(self,requests):
		if requests.method=='GET':
			result=self.get(requests)
		else:
			return JsonResponse({},status=405)
		return result

	def get(self,requests):
		try:
			filePath=requests.GET['filePath']
			if not filePath:
				raise Exception("Invalid Request Parameter")
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		return NyokaServer.getDetailsOfPMML(filePath)


class PMMLGlobalView(APIView):
	http_method_names=['get']

	def dispatch(self,requests):
		if requests.method=='GET':
			result=self.get(requests)
		else:
			return JsonResponse({},status=405)
		return result

	def get(self,requests):
		return NyokaServer.getGlobalObject()


class PMMLOpeartionView(APIView):
	http_method_names=['post']

	def diapatch(self,requests,projectID):
		if requests.mehtod=='POST':
			result=self.post(requests,projectID)
		else:
			return JsonResponse({},status=405)
		return result

	def post(self,requests,projectID):
		try:
			filePath=requests.POST.get('filePath')
			if not filePath:
				raise Exception("Invalid Request Parameter")
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		return NyokaServer.addArchitectureToGlobalMemoryDict(projectID,filePath)


class PMMLLayerView(APIView):
	http_method_names=['put','delete']

	def dispatch(self,requests,projectID):
		if requests.method=='PUT':
			result=self.put(requests,projectID)
		elif requests.method=='DELETE':
			result=self.delete(requests,projectID)
		else:
			return JsonResponse({},status=405)
		return result

	def delete(self,requests,projectID):
		userInput = json.loads(requests.body)
		try:
			payload=userInput['layerDelete']
			if not payload:
				raise Exception("Invalid Request Parameter")
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		
		if 'modelType' in payload:
			if payload['modelType']== 'Workflow':
				return NyokaServer.deleteWorkflowlayer(userInput,projectID)
		else:
			return NyokaServer.deletelayer(userInput,projectID)

	def put(self,requests,projectID):
		userInput = json.loads(requests.body)
		try:
			payload=userInput['layerToUpdate']
			if not payload:
				raise Exception("Invalid Request Parameter")
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		if 'modelType' in payload:
			if payload['modelType']== 'Workflow':
				return NyokaServer.updatetoWorkflow(payload,projectID)
		else:
			return NyokaServer.updatetoArchitecture(payload,projectID)


			





# from SwaggerSchema.schemas import (
# 	addArchitectureSwagger,
# 	updateLayerSwagger,
# 	deleteLayerSwagger,
# 	getDetailsOfPMMLswagger)

# nyokaUtilities = nyokaUtilities.NyokaUtilities()
# nyokaPMMLUtilities = nyokaPMMLUtilities.NyokaPMMLUtilities()
# global lockForPMML

# lockForPMML = None


# def create_lock():
#     global lockForPMML
#     lockForPMML = Lock()
#     print(lockForPMML.__dir__())

# settingFilePath='./settingFiles/'
# savedModels='./SavedModels/'

# global MEMORY_DICT_ARCHITECTURE,MEMORY_OF_LAYERS

# MEMORY_DICT_ARCHITECTURE={}
# MEMORY_OF_LAYERS={}

# layerDetail=open(settingFilePath+'listOflayers.json','r')
# MEMORY_OF_LAYERS=json.loads(layerDetail.read())

# class NyokaServer:


# 	@csrf_exempt
# 	@api_view(['GET'])
# 	def listOfLayers(requests):
# 		global MEMORY_OF_LAYERS
# 		print('response sent')
# 		return JsonResponse(MEMORY_OF_LAYERS,safe=False)

# 	@csrf_exempt
# 	@api_view(['POST'])
# 	@schema(addArchitectureSwagger)
# 	def addArchitectureToGlobalMemoryDict(requests):
# 		global MEMORY_DICT_ARCHITECTURE
# 		projectID=requests.POST.get('projectID')
# 		filePath=requests.POST.get('filePath')
# 		try:
# 			MEMORY_DICT_ARCHITECTURE[projectID]
# 		except:
# 			MEMORY_DICT_ARCHITECTURE[projectID]={}
# 			try:
# 				print ('filePath >>>> ',filePath)
# 				archFromPMML=nyokaUtilities.pmmlToJson(filePath)
# 				print ('pass')
# 				MEMORY_DICT_ARCHITECTURE[projectID]['architecture']=archFromPMML
# 			except:
# 				MEMORY_DICT_ARCHITECTURE[projectID]['architecture']=[]
# 			#######################################################
# 			MEMORY_DICT_ARCHITECTURE[projectID]['filePath']=filePath
# 			MEMORY_DICT_ARCHITECTURE[projectID]['projectID']=projectID
# 			# print(MEMORY_DICT_ARCHITECTURE)
# 		print('response sent')
# 		return JsonResponse(MEMORY_DICT_ARCHITECTURE[projectID])


# 	def selectArchitecture(checkTemplateID):
# 		if checkTemplateID=='mobilenetArch':
# 			pmmlObj = pml.parse(open(settingFilePath+'MobilenetArch.pmml','r'), silence=True)
# 			templateArch=nyokaUtilities.pmmlToJson(settingFilePath+'MobilenetArch.pmml')
# 		elif checkTemplateID=='vgg16Arch':
# 			pmmlObj = pml.parse(open(settingFilePath+'vGG16Arch.pmml','r'), silence=True)
# 			templateArch=nyokaUtilities.pmmlToJson(settingFilePath+'vGG16Arch.pmml')
# 		elif checkTemplateID=='vgg19Arch':
# 			pmmlObj = pml.parse(open(settingFilePath+'vGG19Arch.pmml','r'), silence=True)
# 			templateArch=nyokaUtilities.pmmlToJson(settingFilePath+'vGG19Arch.pmml')
# 		return templateArch,pmmlObj

# 	@csrf_exempt
# 	@api_view(["POST"])
# 	@schema(updateLayerSwagger)
# 	def updatetoArchitecture(requests):
# 		global lockForPMML
# 		print ('#######################################################################')
# 		global MEMORY_DICT_ARCHITECTURE, lockForPMML
# 		userInput=requests.body
# 		userInput=json.loads(userInput)
# 		payload=userInput['layerToUpdate']
# 		print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",type(payload))

# 		tempGlobal=MEMORY_DICT_ARCHITECTURE[userInput['projectID']]
# 		filetoSave=tempGlobal['filePath']

# 		existingArch=tempGlobal['architecture']
# 		oldLenOfArchitecture = len(existingArch)
# 		####################################
# 		try:
# 			lockForPMML.acquire()
# 			existingPmmlObj=pml.parse(filetoSave,silence=True)
# 		except Exception as e:
# 			print('>>>>>>>>>>>>>>>>> ', str(e))
# 			existingPmmlObj=None
# 		finally:
# 			lockForPMML.release()

# 		newPmmlObj=None
# 		templatePmml=None
# 		if payload['itemType'] in ['FOLDING','DATA','CODE','TEMPLATE']:
# 			processTheInput=payload
# 		else:
# 			try:
# 				processTheInput=nyokaUtilities.addLayertoJson(payload)
# 			except:
# 				processTheInput=payload

# 		# print ('Ouput which we got >>>>>>>>>>> ',processTheInput)
# 		newArch=[]

# 		listOFIDS,listOFIndices,listOFIdIndex,listOfSectionID,listOFSectionIdIndex,listOFSectionIdAndId=nyokaUtilities.detailsofExistingArch(existingArch)
# 		listOfAllIDinSections=[]
# 		for j in existingArch:
# 			if j['itemType']=='FOLDING':
# 				for num,k in enumerate(j['children']):
# 					listOfAllIDinSections.append(k['id'])
# 		indexInObj=nyokaUtilities.checkIndexOfInput(processTheInput)
# 		idInObj=nyokaUtilities.getIdOfInput(processTheInput)
# 		itemTypeofObj=processTheInput['itemType']
# 		print ('Ouput itemTypeofObj we got >>>>>>>>>>> ',itemTypeofObj)
# 		# print ('nyokaUtilities.checkAboutLayer(processTheInput)',nyokaUtilities.checkAboutLayer(processTheInput))

# 		if len(existingArch) ==0:
# 			if nyokaUtilities.checkAboutLayer(processTheInput) == 'TEMPLATE':
# 				print ('B1 Given input is of Type Template')
# 				checkTemplateID=processTheInput['templateId']
# 				# $update$
# 				templateArch,templatePmml=self.selectArchitecture(checkTemplateID)
# 				if indexInObj not in listOFIndices:
# 					existingArch=existingArch+templateArch
# 				else:
# 					existingArch=existingArch[:indexInObj]+templateArch+existingArch[indexInObj:]
# 			else:
# 				print ('A1 len of existingArch is 0')
# 				newArch.append(processTheInput.copy())
# 				existingArch=newArch.copy()
# 		elif len(existingArch)>0:
# 			#######################################################################################################################
# 		    if nyokaUtilities.checkAboutLayer(processTheInput) == 'Section':
# 		        print ('A2 Given input is of Type Section')
# 		        sectionIdOfInput=nyokaUtilities.getIdOfSection(processTheInput)
# 		        tupleOFindexSect=[(i['layerIndex'],i['sectionId']) for i in existingArch if i['itemType']=='FOLDING']
# 		        print ('>>>>>>>>>>>>>>>>>>> ',tupleOFindexSect)
# 		        print ('<<<<<<<<<<<<<<<<<<<< ',indexInObj,sectionIdOfInput)
# 		        if ((indexInObj,sectionIdOfInput) in tupleOFindexSect) & (nyokaUtilities.checkChildren(processTheInput) ==True):
# 		        	print ('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$Came here')
# 		        	existingArch[indexInObj]=payload.copy()
# 		        elif (sectionIdOfInput in listOfSectionID) and (sectionIdOfInput != None):
# 		            print ('A3 Section Id exist ',sectionIdOfInput )
# 		            listOfIDSwheretomove=[j['id'] for j in [i for i in existingArch if i['itemType']=='FOLDING' if i['sectionId']==sectionIdOfInput][0]['children']]
# 		            indexOfObject=existingArch.index([j for j in [i for i in existingArch if nyokaUtilities.checkExistForSectionFilter(i)] if j['sectionId']==sectionIdOfInput][0])
# 		            tempSection=existingArch[indexOfObject]
# 		            sectionArch=tempSection['children']

# 		            if idInObj in listOFIDS:
# 		            	try:
# 		            		toRem=[i['id'] for i in existingArch].index(idInObj)
# 		            		existingArch.remove(existingArch[toRem])
# 		            	except:
# 		            		pass
# 		            # print ('$$$$$$$$$$$$',[i['id'] for i in existingArch])

# 		            tempSectionArch=[]
# 		            if len(sectionArch)==0:
# 		                print ('A4 Section Id exist and No elment in children hence adding',sectionIdOfInput,idInObj )
# 		                tempSectionArch.append(processTheInput.copy())
# 		                tempSection['children']=tempSectionArch
# 		            elif len(sectionArch)>0:
# 		                sectionListOFIDS,sectionListOFIndices,sectionListOFIdIndex=nyokaUtilities.detailsofSectionArch(tempSection)                    
# 		                print ('A5 Section Id exist there are element in children hence checking What to do',sectionIdOfInput,idInObj )
# 		                if idInObj in listOFIDS:
# 		                    print ('A6_0 element Id exist',idInObj )
# 		                    if (sectionIdOfInput,indexInObj,idInObj) in listOFSectionIdIndex:
# 		                        print ('A6 Section Id Index and object Id matched just update',sectionIdOfInput,indexInObj,idInObj )
# 		                        existingArch[indexOfObject]['children'][indexInObj]=processTheInput.copy()
		                        
# 		                    elif (sectionIdOfInput,idInObj) in listOFSectionIdAndId:
# 		                        if indexInObj in sectionListOFIndices:
# 		                            print ('A7 Index {} exist  alrady need to swap and reorder'.format(indexInObj))

# 		                            tempIndExist=[j['id'] for j in sectionArch].index(idInObj)
# 		                            del sectionArch[tempIndExist]
# 		                            sectionArch.insert(indexInObj,processTheInput.copy())
# 		                            for num,lay in enumerate(sectionArch):
# 		                                lay['layerIndex']=num
# 		                                newArch.append(lay)
# 		                            existingArch[indexOfObject]['children']=newArch.copy()
# 		                    elif idInObj not in listOfAllIDinSections:
# 		                    	print ('A70 Index exist but not in section need to add')
# 		                    	# print (idInObj,[i['id'] for i in existingArch])
# 		                    	if idInObj in [i['id'] for i in existingArch]:
# 		                    		print ('A701 Index exist but not in section probably section is empty')
# 		                    		toDel=[i['id'] for i in existingArch].index(idInObj)
# 		                    		existingArch.remove(existingArch[toDel])
# 		                    		newSecArch=nyokaUtilities.makeModification(sectionArch,processTheInput)
# 		                    		sectionArch=newSecArch.copy()
# 		                    	else:
# 		                    		# print (listOFSectionIdAndId)
# 		                    		toremoveFromSection=[j[0] for j in listOFSectionIdAndId if j[0]==sectionIdOfInput][0]
# 		                    		indexOfsectionInArch=existingArch.index([j for j in existingArch if j['itemType']=='FOLDING' if j['sectionId']==toremoveFromSection][0])
# 		                    		# toDel=[i['id'] for i in existingArch].index(idInObj)
# 		                    		# existingArch.remove(existingArch[toDel])
# 		                    		print ('A702 Index section not empty')
# 		                    		if indexInObj in [i['layerIndex'] for i in sectionArch]:
		                    			
# 		                    			print ('A703 Index section not empty')
# 		                    			sectionArch.insert(processTheInput.copy(),indexInObj)
# 		                    		else:
# 		                    			print ('A704 Index section not empty')
# 		                    			sectionArch.append(processTheInput.copy())
# 		                    			print ([i['id'] for i in sectionArch])

# 		                    		existingArch[indexOfsectionInArch]['children']=sectionArch
# 		                    		# print ([i['id'] for i in existingArch])


# 		                    elif idInObj not in listOfIDSwheretomove:
# 		                        print ('A7_1 the id exist but not in section so deleting and appending')
# 		                        toremoveFromSection=[j[0] for j in listOFSectionIdAndId if j[1]==idInObj][0]
# 		                        indexOfsectionInArch=existingArch.index([j for j in existingArch if j['itemType']=='FOLDING' if j['sectionId']==toremoveFromSection][0])
# 		                        indexOfObjecttoremove=[j['id'] for j in existingArch[indexOfsectionInArch]['children']].index(idInObj)

# 		                        toremoveFromSection,indexOfsectionInArch,indexOfObjecttoremove
# 		                        del existingArch[indexOfsectionInArch]['children'][indexOfObjecttoremove]

# 		                        tempStrucOfChildList=[]
# 		                        for num,elem in enumerate(existingArch[indexOfsectionInArch]['children']):
# 		                            tempStrucOfChild=elem.copy()
# 		                            tempStrucOfChild['layerIndex']=num
# 		                            tempStrucOfChildList.append(tempStrucOfChild)

# 		                        existingArch[indexOfsectionInArch]['children']=tempStrucOfChildList.copy()
# 		                        newArch=nyokaUtilities.makeModification(sectionArch,processTheInput)
# 		                        existingArch[indexOfObject]['children']=newArch
		                        
		                    
		                        
# 		                else:
# 		                    print ('A8 Section Id exist there are element and new element has came figure out the place',sectionIdOfInput,idInObj )
# 		                    if indexInObj in sectionListOFIndices:
# 		                        print ('>>>>>>>>>> Section Id exist > 0 but ID is not fiund but Index has ben found',sectionIdOfInput,idInObj )
# 		                        newArch=nyokaUtilities.makeModification(sectionArch,processTheInput)
# 		                        existingArch[indexOfObject]['children']=newArch.copy()
# 		                    else:
# 		                        sectionArch.append(processTheInput)
# 		                        existingArch[indexOfObject]['children']=sectionArch.copy()
		                
# 			#3####################################################################################################################            
# 		        else:
# 		            print ('A9 Id does not exist ',idInObj )
# 		            if indexInObj in listOFIndices:
# 		                print ('A10 Index {} exist  alrady'.format(indexInObj))
# 		                newArch=nyokaUtilities.makeModification(existingArch,processTheInput)
# 		                existingArch=newArch.copy()
# 		            else:
# 		                print ('A11 Id does not exist nor the index ',idInObj )
# 		                existingArch.append(processTheInput.copy())
# 		    elif nyokaUtilities.checkAboutLayer(processTheInput) == 'TEMPLATE':
# 		    	print ('B1 Given input is of Type Template')
# 		    	checkTemplateID=processTheInput['templateId']
# 		    	templateArch, templatePmml=self.selectArchitecture(checkTemplateID)

# 		    	if indexInObj not in listOFIndices:
# 		    		existingArch=existingArch+templateArch
# 		    	else:
# 		    		existingArch=existingArch[:indexInObj]+templateArch+existingArch[indexInObj:]

# 		    else:
# 		        print ('A11 Given input is of Type Layer')
# 		        print ('A12 len of existingArch is > 0')
# 		        if idInObj in listOFIDS:
# 		            print ('A13 Id exist ',idInObj )
# 		            if (indexInObj,idInObj) in listOFIdIndex:
# 		                print ('The layer already exist and index also matches and just needed to be updated')
# 		                for lay in existingArch:
# 		                    indexLay=nyokaUtilities.checkIndexOfInput(lay)
# 		                    idInLay=nyokaUtilities.getIdOfInput(lay)
# 		                    if (indexInObj,idInObj) ==(indexLay,idInLay):
# 		                    	print ('A13 Id exist processTheInput')
# 		                    	newArch.append(processTheInput.copy())
# 		                    else:
# 		                        newArch.append(lay)
# 		                existingArch=newArch.copy()
# 		            else:
# 		                print ('The layer already exist but index has changed needed to be restructre')
# 		                print ('listOFIndices',listOFIndices)
# 		                print ('indexInObj',indexInObj)
# 		                if indexInObj in listOFIndices:
# 		                    print ('A14 Index {} exist  alrady need to swap and reorder'.format(indexInObj))

# 		                    tempIndExist=[j['id'] for j in existingArch].index(idInObj)
# 		                    del existingArch[tempIndExist]
# 		                    print (len(existingArch))
# 		                    existingArch.insert(indexInObj,processTheInput.copy())
# 		                    for num,lay in enumerate(existingArch):
# 		                        lay['layerIndex']=num
# 		                        newArch.append(lay)
# 		                    existingArch=newArch.copy()
# 		                else:
# 		                	groupwithID=[]
# 		                	for j in existingArch:
# 		                		if j['itemType']=='FOLDING':
# 		                			for num,k in enumerate(j['children']):
# 		                				groupwithID.append((j['id'],k['id'],num))
# 		                	sectionToRemove=[j for j in groupwithID if j[1]==idInObj][0]
# 		                	indexOfSectoDel=[i['id'] for i in existingArch].index(sectionToRemove[0])
# 		                	tempSecToremoveFrom=existingArch[indexOfSectoDel]['children'].copy()
# 		                	for tem in tempSecToremoveFrom:
# 		                		if tem['id']==idInObj:
# 		                			tempSecToremoveFrom.remove(tem)

# 		                	for numa,tem2 in enumerate(tempSecToremoveFrom):
# 		                		tem2['layerIndex']=numa

# 		                	existingArch[indexOfSectoDel]['children']=tempSecToremoveFrom
# 		                	existingArch.append(processTheInput.copy())


# 		        else:
# 		            print ('A15 Id does not exist ',idInObj )
# 		            if indexInObj in listOFIndices:
# 		                print ('A16 Index {} exist  alrady'.format(indexInObj))
# 		                newArch=nyokaUtilities.makeModification(existingArch,processTheInput)
# 		                existingArch=newArch.copy()
# 		            else:
# 		                existingArch.append(processTheInput.copy())


# 		for num,coco in enumerate(existingArch):
# 			if coco['itemType']=='FOLDING':
# 				for num2,k in enumerate(coco['children']):
# 					k['layerIndex']=num2
# 					coco['layerIndex']=num
# 			else:
# 				coco['layerIndex']=num
	            
# 		tempGlobal['architecture']=existingArch

# 		indexToUpdate = payload['layerIndex']

# 		indexInPmml = 0
# 		foundTheLayer = False
# 		if not existingPmmlObj or len(existingPmmlObj.DeepNetwork[0].NetworkLayer)==0:
# 			indexInPmml = 0
# 		else:
# 			prevId = ''
# 			import ast
# 			for idx,layer in enumerate(existingPmmlObj.DeepNetwork[0].NetworkLayer):
# 				if indexInPmml == indexToUpdate:
# 					indexInPmml = idx
# 					foundTheLayer = True
# 					break
# 				if not layer.Extension:
# 					indexInPmml += 1
# 				else:
# 					secId = ast.literal_eval(layer.Extension[0].value)['sectionId']
# 					if secId != prevId:
# 						indexInPmml += 1
# 						prevId = secId
# 		if not foundTheLayer:
# 			indexInPmml = len(existingPmmlObj.DeepNetwork[0].NetworkLayer)
# 		else:
# 			if existingPmmlObj.Header.Extension:
# 				indexInPmml -= 1
# 			if existingPmmlObj.script:
# 				indexInPmml -= 1

# 		print('$$$$$$$$$$$$$$$$$',indexInPmml)
# 		# create the PMML for the newly updated architecture
# 		newPmmlObj = nyokaPMMLUtilities.getPmml(existingArch)

# 		# if template is picked then check if existing pmml already has some layers or not
# 		if templatePmml:
# 			if len(templatePmml.DeepNetwork[0].NetworkLayer) == len(newPmmlObj.DeepNetwork[0].NetworkLayer):
# 				for idx,lay in enumerate(newPmmlObj.DeepNetwork[0].NetworkLayer):
# 					templatePmml.DeepNetwork[0].NetworkLayer[idx].Extension = lay.Extension
# 			else:
# 				diff = len(newPmmlObj.DeepNetwork[0].NetworkLayer) - len(templatePmml.DeepNetwork[0].NetworkLayer)
# 				for idx in range(len(templatePmml.DeepNetwork[0].NetworkLayer)):
# 					templatePmml.DeepNetwork[0].NetworkLayer[idx].Extension = newPmmlObj.DeepNetwork[0].NetworkLayer[idx+diff].Extension
# 			newPmmlObj.DeepNetwork = templatePmml.DeepNetwork

# 		layerIdsInPmml = list()
# 		for lay in existingPmmlObj.DeepNetwork[0].NetworkLayer:
# 			layerIdsInPmml.append(lay.layerId)

# 		# print(payload['itemType'], payload['layerId'], layerIdsInPmml)

# 		# if the update is for code or data then do not change the deep network
# 		if payload['itemType'] in ['DATA','CODE']:
# 			pass
# 		# if updated layer is already present then update the layer only
# 		elif str(payload['layerId']) in layerIdsInPmml:
# 			indexInPmml = layerIdsInPmml.index(str(payload['layerId']))
# 			print(indexInPmml)
# 			print(existingPmmlObj.DeepNetwork[0].NetworkLayer[indexInPmml].__dict__)
# 			existingPmmlObj.DeepNetwork[0].NetworkLayer[indexInPmml] = newPmmlObj.DeepNetwork[0].NetworkLayer[indexInPmml]
# 		# if new layer and index is out of bound then add to the last
# 		elif indexInPmml >= len(newPmmlObj.DeepNetwork[0].NetworkLayer):
# 			if existingPmmlObj:
# 				existingPmmlObj.DeepNetwork[0].NetworkLayer = existingPmmlObj.DeepNetwork[0].NetworkLayer+\
# 				newPmmlObj.DeepNetwork[0].NetworkLayer[indexInPmml:]
# 			else:
# 				existingPmmlObj = newPmmlObj
# 		# if new layer and within index range then insert it there
# 		else:
# 			if templatePmml:
# 				existingPmmlObj.DeepNetwork[0].NetworkLayer = existingPmmlObj.DeepNetwork[0].NetworkLayer[:indexInPmml]+\
# 				newPmmlObj.DeepNetwork[0].NetworkLayer+existingPmmlObj.DeepNetwork[0].NetworkLayer[indexInPmml:]
# 			else:
# 				existingPmmlObj.DeepNetwork[0].NetworkLayer = existingPmmlObj.DeepNetwork[0].NetworkLayer[:indexInPmml]+\
# 				[newPmmlObj.DeepNetwork[0].NetworkLayer[indexInPmml]]+existingPmmlObj.DeepNetwork[0].NetworkLayer[indexInPmml:]
		

# 		newPmmlObj.DeepNetwork[0].NetworkLayer = existingPmmlObj.DeepNetwork[0].NetworkLayer
# 		newPmmlObj.DeepNetwork[0].numberOfLayers = len(newPmmlObj.DeepNetwork[0].NetworkLayer)
# 		if newPmmlObj.Header.Extension:
# 			newPmmlObj.Header.Extension[0].anytypeobjs_ = ['']
# 		for lay in newPmmlObj.DeepNetwork[0].NetworkLayer:
# 			if lay.Extension:
# 				lay.Extension[0].anytypeobjs_ = ['']
# 		try:
# 			lockForPMML.acquire()
# 			newPmmlObj.export(open(filetoSave,'w'),0)
# 		finally:
# 			lockForPMML.release()

# 		# train_prc = Process(target=nyokaPMMLUtilities.writePMML,args=(existingArch,filetoSave))
# 		# train_prc.start()

# 		# # print (MEMORY_DICT_ARCHITECTURE)
# 		if nyokaUtilities.checkAboutLayer(processTheInput) == 'TEMPLATE':
# 			returntoClient={'projectID':userInput['projectID'],'architecture':tempGlobal['architecture']}
# 		else:
# 			returntoClient={'projectID':userInput['projectID'],'layerUpdated':processTheInput}
# 		print('response sent')
# 		return JsonResponse(returntoClient)


# 	def writePmml(self,pmmlObj, filepath, lockForPMML):
# 		try:
# 			lockForPMML.acquire()
# 			pmmlObj.export(open(filepath,'w'),0)
# 			print('>>>>>>>>>>>, PMML written')
# 		except Exception as e:
# 			print('>>>>>>>>>>>> ',str(e))
# 		finally:
# 			lockForPMML.release()


# 	@csrf_exempt
# 	@api_view(['POST'])
# 	@schema(deleteLayerSwagger)
# 	def deletelayer(requests):
# 		userInput=requests.body
# 		userInput=json.loads(userInput)
# 		global MEMORY_DICT_ARCHITECTURE
# 		global lockForPMML
# 		print ('>>>>>',userInput)
# 		existingArch=MEMORY_DICT_ARCHITECTURE[userInput['projectID']]['architecture']
		
# 		# $update$
# 		filetoSave=MEMORY_DICT_ARCHITECTURE[userInput['projectID']]['filePath']
# 		try:
# 			lockForPMML.acquire()
# 			existingPmmlObj=pml.parse(filetoSave,silence=True)
# 		except Exception as e:
# 			print('>>>>>>>>>>>>>>>>> ', str(e))
# 			existingPmmlObj=None
# 		finally:
# 			lockForPMML.release()

# 		existingPmmlObj=pml.parse(filetoSave, silence=True)

# 		layerIdToDelete=userInput['layerDelete']['layerId']

# 		processTheInput=userInput['layerDelete']
# 		try:
# 		    deleteFromSection=processTheInput['sectionId']
# 		    if processTheInput['itemType']!='FOLDING':
# 		        idToDelete=processTheInput['id']
# 		        positionOfSection=existingArch.index([j for j in existingArch if j['itemType']=='FOLDING' if j['sectionId']==deleteFromSection][0])
# 		        positionInChildren=[j['id'] for j in existingArch[positionOfSection]['children']].index(idToDelete)
# 		        del existingArch[positionOfSection]['children'][positionInChildren]
# 		    else:
# 		        positionOfSection=existingArch.index([j for j in existingArch if j['itemType']=='FOLDING' if j['sectionId']==deleteFromSection][0])
# 		        del existingArch[positionOfSection]
# 		except:
# 		    idToDelete=processTheInput['id']
# 		    positionInArch=[j['id'] for j in existingArch].index(idToDelete)
# 		    del existingArch[positionInArch]
		    
		    
# 		for num,lay in enumerate(existingArch):
# 		    if lay['itemType']=='FOLDING':
# 		        for num2,levLay in enumerate(lay['children']):
# 		            levLay['layerIndex']=num2
# 		    else:
# 		        lay['layerIndex']=num
		
# 		# $update$
# 		indexToDelete = -1
# 		for index, layer in enumerate(existingPmmlObj.DeepNetwork[0].NetworkLayer):
# 			print("**********************************",layer.layerId)
# 			if layer.layerId == layerIdToDelete:
# 				indexToDelete = index
# 				break
# 		if indexToDelete != -1:
# 			del existingPmmlObj.DeepNetwork[0].NetworkLayer[indexToDelete]
# 		existingPmmlObj.Header.Extension[0].anytypeobjs_ = ['']
# 		for lay in existingPmmlObj.DeepNetwork[0].NetworkLayer:
# 			if lay.Extension:
# 				lay.Extension[0].anytypeobjs_ = ['']
# 		existingPmmlObj.DeepNetwork[0].numberOfLayers = len(existingPmmlObj.DeepNetwork[0].NetworkLayer)

# 		try:
# 			lockForPMML.acquire()
# 			existingPmmlObj.export(open(filetoSave,'w'),0)
# 		except Exception as e:
# 			print('>>>>>>>>>> ', str(e))
# 		finally:
# 			lockForPMML.release()

		
# 		MEMORY_DICT_ARCHITECTURE[userInput['projectID']]['architecture']=existingArch
# 		message={'message':'Success'}

# 		return JsonResponse(message)


# 	@csrf_exempt
# 	@api_view(['POST'])
# 	def getGlobalObject(requests):
# 		global MEMORY_DICT_ARCHITECTURE
# 		return JsonResponse(MEMORY_DICT_ARCHITECTURE)



# 	@csrf_exempt
# 	@api_view(['POST'])
# 	@schema(getDetailsOfPMMLswagger)
# 	def getDetailsOfPMML(requests):
# 		# print('#######',requests.body)
# 		userInput=requests.body
# 		userInput=json.loads(userInput)
# 		filepath=userInput['filePath']
# 		# print('$$$$$$$$$$',filepath)
# 		# print('filepath',filepath)
# 		pmmlObj=pml.parse(filepath,silence=True)
# 		tempObj=pmmlObj.__dict__
		


# 		listOfObjectstogetData=[]
# 		for j in tempObj.keys():
# 		    if (tempObj[j] is None) :
# 		        pass
# 		    elif (isinstance(tempObj[j], typing.List)):
# 		        if (len(tempObj[j])==0):
# 		            pass
# 		        else:
# 		            listOfObjectstogetData.append(j)
# 		    else:
# 		        listOfObjectstogetData.append(j)


# 		allInfo={}
# 		for towork in listOfObjectstogetData:
# 		    if towork=='version':
# 		        allInfo['Version']=tempObj['version']
# 		    elif towork=='Header':
# 		        allInfo.update(nyokaUtilities.getHeaderInfo(tempObj))
# 		    elif towork=='DataDictionary':
# 		        allInfo.update(nyokaUtilities.getDataFields(tempObj))
# 		    elif towork=='NearestNeighborModel':
# 		        allInfo.update(nyokaUtilities.getInfoNearestNeighborModel(tempObj))
# 		    elif towork=='DeepNetwork':
# 		        allInfo.update(nyokaUtilities.getInfoOfDeepNetwork(tempObj))
# 		    elif towork=='MiningModel':
# 		        allInfo.update(nyokaUtilities.getInfoMiningModel(tempObj))
# 		    elif towork=='SupportVectorMachineModel':
# 		        allInfo.update(nyokaUtilities.getInfoSupportVectorMachineModel(tempObj))
# 		    elif towork=='TreeModel':
# 		    	allInfo.update(nyokaUtilities.getInfoTreeModel(tempObj))
# 		allInfo=nyokaUtilities.changeStructure(allInfo)
# 		print('response sent')
# 		return JsonResponse(allInfo)


