from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
import requests, json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view,schema
from nyokaserver import nyokaUtilities,nyokaPMMLUtilities
from nyokaBase import PMML43Ext as pml
import typing
from datetime import datetime
import json,sys,subprocess
# from SwaggerSchema.schemas import (
# 	addArchitectureSwagger,
# 	updateLayerSwagger,
# 	deleteLayerSwagger,
# 	getDetailsOfPMMLswagger)


from multiprocessing import Lock, Process
nyokaUtilities = nyokaUtilities.NyokaUtilities()
nyokaPMMLUtilities = nyokaPMMLUtilities.NyokaPMMLUtilities()
global lockForPMML

lockForPMML = None


def create_lock():
    global lockForPMML
    lockForPMML = Lock()

settingFilePath='./settingFiles/'
savedModels='./SavedModels/'



global MEMORY_DICT_ARCHITECTURE,MEMORY_OF_LAYERS

MEMORY_DICT_ARCHITECTURE={}
MEMORY_OF_LAYERS={}

layerDetail=open(settingFilePath+'listOflayers.json','r')
MEMORY_OF_LAYERS=json.loads(layerDetail.read())


def removeExtraNewLinesFromWeights(pmmlObj):
	for lay in pmmlObj.DeepNetwork[0].NetworkLayer:
		try:
			lay.LayerWeights.valueOf_=lay.LayerWeights.valueOf_.replace('\n','')
			lay.LayerWeights.content_[0].value=lay.LayerWeights.content_[0].value.replace('\n','')
		except:
			pass
		try:
			lay.LayerBias.valueOf_=lay.LayerBias.valueOf_.replace('\n','')
			lay.LayerBias.content_[0].value=lay.LayerBias.content_[0].value.replace('\n','')
		except:
			pass
	return pmmlObj


def writePmml(pmmlObj, filepath, lockForPMML):
	_deepNetworkObj=pmmlObj.DeepNetwork[0]
	_deepNetworkObj.modelName ='model1'
	_deepNetworkObj.taskType="trainAndscore"

	pmmlObj.DeepNetwork[0]=_deepNetworkObj

	# print ('came to write')
	try:
		lockForPMML.acquire()
		pmmlObj=removeExtraNewLinesFromWeights(pmmlObj)
		scrptVal2=[]
		scrptVal=pmmlObj.script
		if len(scrptVal) > 0:
			for num,sc in enumerate(scrptVal):
				scriptPurpose=sc.scriptPurpose
				modelVal=sc.for_
				classVal=sc.class_
				filePathUrl=sc.filePath
				scriptOutput=sc.scriptOutput

				code=None
				scripCode=sc.get_valueOf_()
				code = scripCode.lstrip('\n')
				lines = []
				code = scripCode.lstrip('\n')
				leading_spaces = len(code) - len(code.lstrip(' '))
				for line in code.split('\n'):
					lines.append(line[leading_spaces:])
				code = '\n'.join(lines)
				scriptCode=code.replace('<','&lt;')
				# scrp=pml.script(content=scriptCode,for_=modelVal,class_=taskTypeVal,scriptPurpose=scriptPurpose,scriptOutput=scriptOutput,filePath=filePathUrl)
				scrp=pml.script(content=scriptCode,for_=modelVal,class_=classVal,scriptPurpose=scriptPurpose,scriptOutput=scriptOutput,filePath=filePathUrl)
				scrptVal2.append(scrp)
		pmmlObj.script=scrptVal2
		# print ('Code Step 10.1')
		pmmlObj.export(open(filepath,'w'),0)
		# print('>>>>>>>>>>>, PMML written')
	except Exception as e:
		print('>>>>>>>>>>>> ',str(e))
	finally:
		lockForPMML.release()

def resetNetworkLayer(_NetworkLayersObject,indexToStart):
	for num in range(indexToStart,len(_NetworkLayersObject)):
		if _NetworkLayersObject[num].LayerBias:
			_NetworkLayersObject[num].LayerBias.content_ = []
		if _NetworkLayersObject[num].LayerWeights:
			_NetworkLayersObject[num].LayerWeights.content_ = []

	# print ('step 4')
	_idsOfNetworklayer=[i.layerId for i in _NetworkLayersObject]
	# print ('step 5')
	for num,unitNetwork in enumerate(_idsOfNetworklayer):
		if num==0:
			_NetworkLayersObject[num].connectionLayerId='NA'
		else:
			_NetworkLayersObject[num].connectionLayerId=_NetworkLayersObject[num-1].layerId

	return _NetworkLayersObject

class NyokaServer:
	@csrf_exempt
	@api_view(['GET'])
	def listOfLayers(requests):
		global MEMORY_OF_LAYERS
		# print('response sent')
		return JsonResponse(MEMORY_OF_LAYERS)

	# @csrf_exempt
	# @api_view(['POST'])
	# @schema(addArchitectureSwagger)
	def addArchitectureToGlobalMemoryDict(projectID,filePath):
		global MEMORY_DICT_ARCHITECTURE
		try:
			MEMORY_DICT_ARCHITECTURE[projectID]
			tempMemRe=MEMORY_DICT_ARCHITECTURE[projectID]
			# print (tempMemRe)
			if tempMemRe['architecture']==[]:
				archFromPMML=nyokaUtilities.pmmlToJson(filePath)
				# print ('pass',archFromPMML)
				MEMORY_DICT_ARCHITECTURE[projectID]['architecture']=archFromPMML
				tempMemRe=MEMORY_DICT_ARCHITECTURE[projectID]
			tempMemRe={'architecture':tempMemRe['architecture'],'filePath':tempMemRe['filePath'],'projectID':tempMemRe['projectID']}
		except:
			MEMORY_DICT_ARCHITECTURE[projectID]={}
			# archFromPMML=nyokaUtilities.pmmlToJson(filePath)
			# MEMORY_DICT_ARCHITECTURE[projectID]['architecture']=archFromPMML
			try:
				print ('filePath >>>> ',filePath)
				archFromPMML=nyokaUtilities.pmmlToJson(filePath)
				# print ('pass',archFromPMML)
				MEMORY_DICT_ARCHITECTURE[projectID]['architecture']=archFromPMML
			except Exception as e:
				print('<>>>><<>>>>',str(e))
				MEMORY_DICT_ARCHITECTURE[projectID]['architecture']=[]
			#######################################################
			MEMORY_DICT_ARCHITECTURE[projectID]['filePath']=filePath
			MEMORY_DICT_ARCHITECTURE[projectID]['projectID']=projectID
			tempMemRe=MEMORY_DICT_ARCHITECTURE[projectID]
			# print(MEMORY_DICT_ARCHITECTURE)
		# print('response sent')
		return JsonResponse(tempMemRe)

	def updatetoArchitecture(payload, projectID):

		def selectArchitecture(checkTemplateID):
			if checkTemplateID=='mobilenetArch':
				pmmlObj = pml.parse(open(settingFilePath+'MobilenetArch.pmml','r'), silence=True)
				templateArch=nyokaUtilities.pmmlToJson(settingFilePath+'MobilenetArch.pmml')
			elif checkTemplateID=='vgg16Arch':
				pmmlObj = pml.parse(open(settingFilePath+'vGG16Arch.pmml','r'), silence=True)
				templateArch=nyokaUtilities.pmmlToJson(settingFilePath+'vGG16Arch.pmml')
			elif checkTemplateID=='vgg19Arch':
				pmmlObj = pml.parse(open(settingFilePath+'vGG19Arch.pmml','r'), silence=True)
				templateArch=nyokaUtilities.pmmlToJson(settingFilePath+'vGG19Arch.pmml')
			return templateArch,pmmlObj

		def addTemplatetoArchitecture(checkTemplateID,indexInObj,listOFIndices,existingArch):
			if checkTemplateID != None:
				templateArch,templatePmml=selectArchitecture(checkTemplateID)
			if indexInObj not in listOFIndices:
				existingArch=existingArch+templateArch
			else:
				existingArch=existingArch[:indexInObj]+templateArch+existingArch[indexInObj:]
			return existingArch,templatePmml

		def addLayerInArch(indexInObj,existingArch,processTheInput):
			existingArch.insert(indexInObj,processTheInput)
			return existingArch

		def getSectionArchitecture(existingArch,sectionIdOfInput):
			# print ('>>>>>>>>>>>>>>>>>>',type(existingArch))
			tempArchSection=[]
			tempNum=None
			# print (len(existingArch))
			for num,j in enumerate(existingArch):
				# print ('$$$$',j)
				if 'sectionId'in j:
					if j['sectionId']==sectionIdOfInput:
						tempNum,tempArchSection=num,j['children']
				else:
					pass
			return (tempNum,tempArchSection)

		def getSectionArchitecturefromLayerID(existingArch,idInObj):
			# print ('>>>>>>>>>>>>>>>>>>',idInObj)
			tempArchSection=[]
			tempNum=None
			# print ('LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL',len(existingArch))
			for num,j in enumerate(existingArch):
				# print ('$$$$',j)
				if 'sectionId'in j:
					if j['sectionId'] != None:
						# print ('Prntong Section to check on',j)
						if idInObj in [i['id'] for i in j['children'] ]:
							# print ('came here')
							tempNum,tempArchSection=num,j['children']
				else:
					pass
			return (tempNum,tempArchSection)

		def deleteAlayerFromArch(tempArchToDelete,idOfLayer):
			spaceToRem=[j['id'] for j in tempArchToDelete]
			indexToDelete=spaceToRem.index(idOfLayer)
			del tempArchToDelete[indexToDelete]
			return tempArchToDelete

		def reoderArch(tempArchtoReorder):
			for num,j in enumerate(tempArchtoReorder):
				tempArchtoReorder[num]['layerIndex']=num
			return tempArchtoReorder

		def getIndexForNewLayer(existingArch,idInObj,runUpto):
			if runUpto==None:
				listOFIDS=[]
				for j in existingArch:
					if j['itemType']=='FOLDING':
						for k in j['children']:
							listOFIDS.append(k['id'])
					else:
						listOFIDS.append(j['id'])
				return listOFIDS.index(idInObj)
			if runUpto != None:
				listOFIDS=[]
				for j in existingArch[:runUpto]:
					if j['itemType']=='FOLDING':
						for k in j['children']:
							listOFIDS.append(k['id'])
					else:
						listOFIDS.append(j['id'])
				return len(listOFIDS)


		def getIndexForExistingLayer(existingPmmlObj,layerId,runUpto):
			_NetworkLayersObject=existingPmmlObj.DeepNetwork[0].NetworkLayer
			listOFIDS=[i.layerId for i in _NetworkLayersObject]
			if runUpto==None:
				return listOFIDS.index(layerId)
			if runUpto != None:
				return len(listOFIDS)

		def addLayerToPMML(_positionOfLayer,toUpdateLayer,processedOutput,pmmlObject):

			def checkIfFlushRequired(_oldPosition, _newPositon, _pmmlLayer, _networkLayers):
				if _oldPosition==_newPositon:
					if (_pmmlLayer.LayerParameters.inputDimension==_networkLayers[_oldPosition].LayerParameters.inputDimension) & (_pmmlLayer.LayerParameters.outputDimension==_networkLayers[_oldPosition].LayerParameters.outputDimension):
						return False
					else:
						return True
				else:
					return True

			if processedOutput['itemType']=='LAYER':
				_inputForPMML=nyokaPMMLUtilities.convertToStandardJson(processedOutput)
				# print ('',_inputForPMML)
				_pmmlOfLayer=nyokaPMMLUtilities.addLayer(_inputForPMML)
				# print('>>>>>>>',_pmmlOfLayer.__dict__)
				_deepNetworkObj=pmmlObject.DeepNetwork[0]
				# print ('step 1')
				_NetworkLayersObject=_deepNetworkObj.NetworkLayer
				# print ('step 2')
				_idsOfNetworklayer=[i.layerId for i in _NetworkLayersObject]
				flushMemory=False
				if toUpdateLayer==True:
					_oldPositionOFLayer=_idsOfNetworklayer.index(processedOutput['layerId'])
					# print('>>>> layer id is ',processedOutput['layerId'])
					# print('>>>> old position to delete',_oldPositionOFLayer)
					# print('>>>> new position ',_positionOfLayer)
					# print ('_idsOfNetworklayer',_idsOfNetworklayer)
					flushMemory=checkIfFlushRequired(_oldPositionOFLayer,_positionOfLayer,_pmmlOfLayer,_NetworkLayersObject)
					# print('flushmemory is ',flushMemory)
					if flushMemory==False:
						_NetworkLayersObject[_oldPositionOFLayer].Extension=_pmmlOfLayer.Extension
						_pmmlOfLayer=_NetworkLayersObject[_oldPositionOFLayer]
					del _NetworkLayersObject[_oldPositionOFLayer]
				_NetworkLayersObject.insert(_positionOfLayer,_pmmlOfLayer)
				# print ('step 3')
				if flushMemory==True:
					_NetworkLayersObject=resetNetworkLayer(_NetworkLayersObject,_positionOfLayer)
					# print ('step 6')
				_NetworkLayersObject=reorderIdsOfPmml(_NetworkLayersObject)
				_deepNetworkObj.NetworkLayer=_NetworkLayersObject
				_deepNetworkObj.numberOfLayers=len(_NetworkLayersObject)
				_deepNetworkObj.modelName ='model1'
				_deepNetworkObj.taskType="trainAndscore"
				pmmlObject.DeepNetwork[0]=_deepNetworkObj

			
			elif processedOutput['itemType']=='DATA':
				# print ("DATA layer came",processedOutput['filePath'])
				try:
					dataUrl=processedOutput['filePath']
				# if processedOutput['for']:
				# 	dataTagValues=pml.Data(filePath=dataVal,for_=processedOutput['for'])
				# else:
					dataTagValues=pml.Data(filePath=dataUrl,for_='model1')
					pmmlObject.Data=[dataTagValues]
					# print ('Data Step 3')
					# pmmlObject.export(sys.stdout,0)
				except:
					pass

			elif processedOutput['itemType']=='CODE':
				print ("CODE layer came")
				# print ('processedOutput',processedOutput)
				try:
					scrptVal=pmmlObject.script
					urlOfScript=processedOutput['url']
					filePathUrl=processedOutput['filePath']
					scriptFile=open(processedOutput['filePath'],'r')
					scriptCode=scriptFile.read()
					scriptCode=scriptCode.replace('<','&lt;')
					# print (scriptCode)
					modelVal='model1'
					taskTypeVal=processedOutput['taskType']
					scriptPurpose=processedOutput['scriptPurpose']
					scriptOutput=processedOutput['scriptOutput']
					scrp=pml.script(content=scriptCode,for_=modelVal,class_=taskTypeVal,scriptPurpose=scriptPurpose,scriptOutput=scriptOutput,filePath=filePathUrl)
					scrp.export(sys.stdout,0)
					scrptVal.append(scrp)
					pmmlObject.script=scrptVal
					# print ('Code Step 10')
					# pmmlObject.export(sys.stdout,0)
				except:
					pass
			return (pmmlObject)

		def reorderIdsOfPmml(_NetworkLayersObject):
			_idsOfNetworklayer=[i.layerId for i in _NetworkLayersObject]
			# print ('step 5')
			for num,unitNetwork in enumerate(_idsOfNetworklayer):
				if num==0:
					_NetworkLayersObject[num].connectionLayerId='NA'
				else:
					_NetworkLayersObject[num].connectionLayerId=_NetworkLayersObject[num-1].layerId

			return _NetworkLayersObject


		def addTemplateToPMML(_positionOfLayer,existingPmmlObj,templatePmmlObj):
			noOfLayersInTemplate = len(templatePmmlObj.DeepNetwork[0].NetworkLayer)
			
			newNetworkLayers=existingPmmlObj.DeepNetwork[0].NetworkLayer[:_positionOfLayer]+templatePmml.DeepNetwork[0].NetworkLayer\
			+existingPmmlObj.DeepNetwork[0].NetworkLayer[_positionOfLayer:]

			newNetworkLayers=resetNetworkLayer(newNetworkLayers,noOfLayersInTemplate+_positionOfLayer)
			existingPmmlObj.DeepNetwork[0].NetworkLayer = newNetworkLayers
			existingPmmlObj.DeepNetwork[0].numberOfLayers=len(existingPmmlObj.DeepNetwork[0].NetworkLayer)
			return existingPmmlObj



		# print ('#######################################################################')
		global MEMORY_DICT_ARCHITECTURE, lockForPMML
		tempGlobal=MEMORY_DICT_ARCHITECTURE[projectID]
		filetoSave=tempGlobal['filePath']
		existingArch=tempGlobal['architecture']
		oldLenOfArchitecture = len(existingArch)

		if 'sectionCollapse' in payload:
			returntoClient={'projectID':projectID,'sectionCollapse':payload['sectionCollapse']}
			return JsonResponse(returntoClient)

		####################################
		try:
			lockForPMML.acquire()
			existingPmmlObj=pml.parse(filetoSave,silence=True)
		except Exception as e:
			# print('>>>>>>>>>>>>>>>>> ', str(e))
			existingPmmlObj=None
		finally:
			lockForPMML.release()

		isItemType_FOLDING_DATA_CODE_TEMPLATE= payload['itemType'] in ['FOLDING','DATA','CODE','TEMPLATE']
		listOFIDS,listOFIndices,listOfIdOFSections,listOfIdOFLayers=nyokaUtilities.detailsofExistingArch(existingArch)
		indexInObj,idInObj=nyokaUtilities.getIndexOfInput(payload),nyokaUtilities.getIdOfInput(payload)
		lenOfExistingArch=len(existingArch)
		typeOfLayer= nyokaUtilities.getLayerType(payload)
		itemOfLayer= nyokaUtilities.checkItemType(payload)
		sectionIdOfInput=nyokaUtilities.getIdOfSection(payload)
		toUpdateLayer=None
		runUpto=None

		try:
			checkTemplateID=payload['templateId']
		except:
			checkTemplateID=None
		tupleOFindexSect=[(i['layerIndex'],i['sectionId']) for i in existingArch if i['itemType']=='FOLDING']
		hasChildren=nyokaUtilities.checkChildren(payload)
		# print (indexInObj,idInObj,lenOfExistingArch,typeOfLayer,sectionIdOfInput,hasChildren)
		# print (listOFIDS,listOFIndices,listOFIdIndex,listOfSectionID,listOFSectionIdIndex,listOFSectionIdAndId)
		if isItemType_FOLDING_DATA_CODE_TEMPLATE:
			# print ('Pointer 0: GOT FOLDING_DATA_CODE_TEMPLATE')
			processTheInput=payload
		else:
			# print ('Pointer 0: GOT LAYER')
			processTheInput=nyokaUtilities.addLayertoJson(payload)
			# processTheInput=payload
			# print ('##########',processTheInput)

		# print ('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
		# print ('sectionIdOfInput',sectionIdOfInput)
		# print ('itemOfLayer',itemOfLayer)
		# print ('typeOfLayer',typeOfLayer)
		# print ('lenOfExistingArch',lenOfExistingArch)
		# print ('indexInObj',indexInObj)
		# print ('idInObj',idInObj)
		# print ('listOFIndices',listOFIndices)
		# # print ('getSectionArchitecture',getSectionArchitecture(existingArch,sectionIdOfInput))
		# print('listOFIDS',listOFIDS)
		# print ('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

		newPmmlObj,templatePmml=None,None
		newArch=[]
		
		if  lenOfExistingArch == 0:
			if typeOfLayer == 'TEMPLATE':
				runUpto=indexInObj
				# print ('Pointer 1.0: Adding template at 0 position')
				existingArch,templatePmml=addTemplatetoArchitecture(checkTemplateID,indexInObj,listOFIndices,existingArch)
			else:
				# print ('Pointer 2: existingArch is 0')
				newArch.append(processTheInput.copy())
				existingArch=newArch.copy()
				# print (existingArch)

		elif lenOfExistingArch > 0:
			if typeOfLayer == 'TEMPLATE':
				runUpto=indexInObj
				# print ('Pointer 1.1: Adding template at {} position'.format(indexInObj))
				existingArch,templatePmml=addTemplatetoArchitecture(checkTemplateID,indexInObj,listOFIndices,existingArch)
			elif typeOfLayer == 'LAYER':
				# print ('Pointer 2.0: We came in layer operation at {} position'.format(indexInObj))
				# print (listOFIndices,listOFIDS)
				if (indexInObj not in listOFIndices) & (idInObj not in listOFIDS):
					# print ('Pointer 2.1 Got new LAYER object at last index {}'.format(indexInObj) )
					existingArch.append(processTheInput.copy())
				elif (indexInObj in listOFIndices) & (idInObj not in listOFIDS):
					# print ('Pointer 2.2 Got a new LAYER object at existing index {}'.format(indexInObj) )
					newArch=nyokaUtilities.makeModification(existingArch,processTheInput)
					existingArch=newArch.copy()
				elif (indexInObj in listOFIndices) & (idInObj in listOFIDS):
					toUpdateLayer=True
					# print ('Pointer 2.3 Got an old LAYER object at existing index {}'.format(indexInObj) )
					tempExistingArchO=existingArch
					tempExistingArchO=deleteAlayerFromArch(existingArch,idInObj)
					tempExistingArchO=addLayerInArch(indexInObj,tempExistingArchO,processTheInput)
					tempExistingArchO=reoderArch(tempExistingArchO)
					# print ('#########',len(tempExistingArchO))
					# newArch=nyokaUtilities.makeModification(tempExistingArchO,processTheInput)
					newArch=tempExistingArchO
					existingArch=newArch.copy()
				elif (indexInObj not in listOFIndices) & (idInObj in listOFIDS) &  (idInObj in listOfIdOFSections):
					toUpdateLayer=True
					# print ('Pointer 2.4 Got an old LAYER from Section object at new index {}'.format(indexInObj) )
					tempExistingArchO=existingArch
					_positionOfSection,tempExistingArchFromSection=getSectionArchitecturefromLayerID(existingArch,idInObj)
					# print (tempExistingArchFromSection)
					tempExistingArchFromSection=deleteAlayerFromArch(tempExistingArchFromSection,idInObj)
					if len(tempExistingArchFromSection) >0:
						# print ('came here too')
						tempExistingArchO[_positionOfSection]['children']=tempExistingArchFromSection
					else:
						# print ('came here too 3')
						del tempExistingArchO[_positionOfSection]
					tempExistingArchO=addLayerInArch(indexInObj,tempExistingArchO,processTheInput)
					tempExistingArchO=reoderArch(tempExistingArchO)
					# print ('#########',len(tempExistingArchO))
					newArch=tempExistingArchO
					existingArch=newArch.copy()
					# for j in existingArch:
					# 	# print ('>>',j['layerId'],j['layerIndex'])
					# 	try:
					# 		for k in j['children']:
					# 			# print ('>> >>',k['layerId'],k['layerIndex'])
					# 	except:
					# 		pass

			        
			elif typeOfLayer == 'SECTION':
				# print ('Pointer 3.0 Got new LAYER object at index {}'.format(indexInObj))
				# print ('>>>>>>>',sectionIdOfInput)
				_positionOfSection,tempSectionArchInMemory=getSectionArchitecture(existingArch,sectionIdOfInput)
				# print (tempSectionArchInMemory)
				_lenSectionArch = len(tempSectionArchInMemory)
				if _positionOfSection is not None:
					_listOFIDSection,_listOFIndicesSection,_listOFIdIndexSection=nyokaUtilities.detailsofSectionArch(existingArch[_positionOfSection])
					# print ('>>>>',_listOFIDSection)
				if (idInObj not in listOFIDS) & (itemOfLayer == 'FOLDING'):
					_tempArch=addLayerInArch(indexInObj,existingArch,processTheInput)
					newArch=reoderArch(_tempArch)
					# print (newArch)
					existingArch=newArch.copy()
				elif (idInObj not in listOFIDS) & (itemOfLayer == 'LAYER'):
					if _lenSectionArch == 0:
						tempSectionArchInMemory.append(processTheInput)
					else:
						if indexInObj in _listOFIndicesSection:
							# print ('Pointer 3.1 Got new LAYER object at index {}'.format(indexInObj) )
							newArchSec=nyokaUtilities.makeModification(tempSectionArchInMemory,processTheInput)
							tempSectionArchInMemory=newArchSec.copy()
						else:
							# print ('Pointer 3.2 Got new LAYER object at last index {}'.format(indexInObj) )
							tempSectionArchInMemory.append(processTheInput.copy())
						existingArch[_positionOfSection]['children']=tempSectionArchInMemory

				elif (idInObj in listOFIDS) & (itemOfLayer == 'LAYER') & (idInObj in _listOFIDSection):
					toUpdateLayer=True
					# print ('Pointer 3.3 Got existing LAYER with {} object at index {}'.format(idInObj,indexInObj) )
					# print ([(j['layerId'],j['layerIndex']) for j in tempSectionArchInMemory])
					tempSectionArchInMemory=deleteAlayerFromArch(tempSectionArchInMemory,idInObj)
					# print ([(j['layerId'],j['layerIndex']) for j in tempSectionArchInMemory])
					tempSectionArchInMemory=addLayerInArch(indexInObj,tempSectionArchInMemory,processTheInput)
					# print (len(tempSectionArchInMemory))
					# print ([(j['layerId'],j['layerIndex']) for j in tempSectionArchInMemory])
					tempSectionArchInMemory=reoderArch(tempSectionArchInMemory)
					existingArch[_positionOfSection]['children']=tempSectionArchInMemory

				elif (idInObj in listOFIDS) & (itemOfLayer == 'LAYER') & (idInObj not in _listOFIDSection) & (idInObj not in listOfIdOFLayers):
					toUpdateLayer=True
					# print ('Pointer 3.4 Got existing LAYER with diff Section {} object at index {}'.format(idInObj,indexInObj) )
					_fromNum,_fromArchi=getSectionArchitecturefromLayerID(existingArch,idInObj)
					# print ('_fromArchi',_fromArchi)
					_fromArchi=deleteAlayerFromArch(_fromArchi,idInObj)
					_fromArchi=reoderArch(_fromArchi)
					existingArch[_fromNum]['children']=_fromArchi.copy()
					tempSectionArchInMemory=addLayerInArch(indexInObj,tempSectionArchInMemory,processTheInput)
					tempSectionArchInMemory=reoderArch(tempSectionArchInMemory)
					existingArch[_positionOfSection]['children']=tempSectionArchInMemory
				elif (idInObj in listOFIDS) & (itemOfLayer == 'LAYER') & (idInObj not in _listOFIDSection) & (idInObj  in listOfIdOFLayers):
					toUpdateLayer=True
					_positionOfSection,tempSectionArchInMemory=getSectionArchitecture(existingArch,sectionIdOfInput)
					# print ('Pointer 3.5 Got existing LAYER not in Section {} object at index {}'.format(idInObj,indexInObj) )
					_fromNum,_fromArchi=getSectionArchitecturefromLayerID(existingArch,idInObj)
					# print ('_fromArchi',_fromArchi)
					existingArch=deleteAlayerFromArch(existingArch,idInObj)
					existingArch=reoderArch(existingArch)
					tempSectionArchInMemory=addLayerInArch(indexInObj,tempSectionArchInMemory,processTheInput)
					tempSectionArchInMemory=reoderArch(tempSectionArchInMemory)
					_positionOfSection,notToUSe=getSectionArchitecture(existingArch,sectionIdOfInput)
					existingArch[_positionOfSection]['children']=tempSectionArchInMemory

		layerId=payload['layerId']
		existingLayerIds=[lay.layerId for lay in existingPmmlObj.DeepNetwork[0].NetworkLayer]
		if itemOfLayer == 'TEMPLATE':
			_positionOfLayer=getIndexForNewLayer(existingArch,idInObj,runUpto)
			# if layerId not in existingLayerIds:
			# 	_positionOfLayer=getIndexForNewLayer(existingArch,idInObj,runUpto)
			# else:
			# 	_positionOfLayer=getIndexForExistingLayer(existingPmmlObj,layerId,runUpto)
			_updatedPMMLObj=addTemplateToPMML(_positionOfLayer,existingPmmlObj,templatePmml)
			writePmml(_updatedPMMLObj, filetoSave, lockForPMML)
		elif itemOfLayer == 'FOLDING':
			if len(processTheInput['children']) == 0:
				pass
		else:
			_positionOfLayer=getIndexForNewLayer(existingArch,idInObj,runUpto)
			# if layerId not in existingLayerIds:
			# 	_positionOfLayer=getIndexForNewLayer(existingArch,idInObj,runUpto)
			# else:
			# 	_positionOfLayer=getIndexForExistingLayer(existingPmmlObj,layerId,runUpto)
			_updatedPMMLObj=addLayerToPMML(_positionOfLayer,toUpdateLayer,processTheInput,existingPmmlObj)
			writePmml(_updatedPMMLObj, filetoSave, lockForPMML)

		tempGlobal['architecture']=existingArch
		MEMORY_DICT_ARCHITECTURE[projectID]['architecture']=tempGlobal['architecture']
		if typeOfLayer == 'TEMPLATE':
			returntoClient={'projectID':projectID,'architecture':tempGlobal['architecture']}
		else:
			returntoClient={'projectID':projectID,'layerUpdated':processTheInput}
		return JsonResponse(returntoClient)

	def updatetoWorkflow(payload,projectID):

		# print (payload)

		def getCodeObjectToProcess(codeVal):
			d = {}
			exec(codeVal, None,d)
			objeCode=d[list(d.keys())[0]]
			return objeCode

		def getCOlumDet(pmmlObj):
			import typing
			listOfObjectstogetData=[]
			tempObj=pmmlObj.__dict__
			for j in tempObj.keys():
				if (tempObj[j] is None) :
					pass
				elif (isinstance(tempObj[j], typing.List)):
					if (len(tempObj[j])==0):
						pass
					else:
						listOfObjectstogetData.append(j)
				else:
					listOfObjectstogetData.append(j)
			for ob in listOfObjectstogetData:
				if ob == 'TreeModel':
					minigFieldList=tempObj['TreeModel'][0].__dict__['MiningSchema'].__dict__['MiningField']
					break
				elif ob=='RegressionModel':
					minigFieldList=tempObj['RegressionModel'][0].__dict__['MiningSchema'].__dict__['MiningField']
					break
				elif ob=='MiningModel':
					minigFieldList=tempObj['MiningModel'][0].__dict__['MiningSchema'].__dict__['MiningField']
					break
				elif ob=='AnomalyDetectionModel':
					minigFieldList=tempObj['AnomalyDetectionModel'][0].__dict__['MiningSchema'].__dict__['MiningField']
					break
				elif ob=='DeepNetwork':
					minigFieldList=tempObj['DeepNetwork'][0].__dict__['MiningSchema'].__dict__['MiningField']
					break
				else:
					None
			targetCol=None
			colNames=[]
			for indCol in minigFieldList:
				if indCol.__dict__['usageType']=='target':
					targetCol=indCol.__dict__['name']
				else:
					colNames.append(indCol.__dict__['name'])
			return (colNames,targetCol)
			
		from nyokaBase.skl.skl_to_pmml import model_to_pmml
		processTheInput=payload
		global MEMORY_DICT_ARCHITECTURE
		try:
			MEMORY_DICT_ARCHITECTURE[projectID]['toExportDict']
		except:
			MEMORY_DICT_ARCHITECTURE[projectID]['toExportDict']={}
		
		try:
			MEMORY_DICT_ARCHITECTURE[projectID]['tempSecMem']
		except:
			MEMORY_DICT_ARCHITECTURE[projectID]['tempSecMem']={}

		tempMem=MEMORY_DICT_ARCHITECTURE[projectID]['toExportDict']
		tempSecMem=MEMORY_DICT_ARCHITECTURE[projectID]['tempSecMem']
		# print ('processTheInput,',processTheInput)
		
		if processTheInput['itemType']=='FOLDING':
			tempSecMem[processTheInput['sectionId']]=processTheInput['layerId']
			tempMem[tempSecMem[processTheInput['sectionId']]]={'data':None,'hyperparameters':None,'preProcessingScript':None,
                        'pipelineObj':None,'modelObj':None,'featuresUsed':None,'targetName':None,'postProcessingScript':None,
                      'taskType': None,'predictedClasses':None,'dataSet':None}

			
			# print (tempSecMem)
		elif processTheInput['itemType']=='DATA':
			tempMem[tempSecMem[processTheInput['sectionId']]]['data']=processTheInput['filePath']
		elif processTheInput['itemType']=='CODE':
			scriptObj=open(processTheInput['filePath'],'r').read()
			# print('scriptObj',scriptObj)
			if processTheInput['taskType']=='preprocessing':
				tempMem[tempSecMem[processTheInput['sectionId']]]['preProcessingScript']={'scripts':[scriptObj],\
																			  'scriptpurpose':[processTheInput['scriptPurpose']],\
																			  'scriptOutput':[processTheInput['scriptOutput']],\
																			'scriptPath':[processTheInput['filePath']]}
			elif processTheInput['taskType']=='postprocessing':
				tempMem[tempSecMem[processTheInput['sectionId']]]['postProcessingScript']={'scripts':[scriptObj],\
																			  'scriptpurpose':[processTheInput['scriptPurpose']],\
																			  'scriptOutput':[processTheInput['scriptOutput']],\
																			  'scriptPath':[processTheInput['filePath']]}
			
		elif processTheInput['itemType']=='MODEL':
			modelPath=processTheInput['filePath']
			from nyokaBase.reconstruct.pmml_to_pipeline_model import generate_skl_model
			from sklearn.pipeline import Pipeline
			from nyokaBase import PMML43Ext as pmmNY
			pmObj=pmmNY.parse(modelPath,silence=True)
			colInfo=getCOlumDet(pmObj)
			print ('came to reconstruct')
			if len(pmObj.__dict__['DeepNetwork']) >0:
				from tensorflow import Graph, Session
				import tensorflow as tf
				model_graph = Graph()
				with model_graph.as_default():
					tf_session = Session()
					with tf_session.as_default():
						print ('step 5')
						from nyokaBase.reconstruct.pmml_to_pipeline_model import generate_skl_model
						print ('step 5.1')
						modelOb = generate_skl_model(pmObj).model
						model_graph = tf.get_default_graph()
						
			else:
				modelOb=generate_skl_model(pmObj)
				model_graph=None
			# print (modelOb)
			# modelOb=None
			import sklearn
			if type(modelOb)==sklearn.pipeline.Pipeline:
				tempMem[tempSecMem[processTheInput['sectionId']]]['modelObj']=modelOb.steps[-1][1]
				tempMem[tempSecMem[processTheInput['sectionId']]]['pipelineObj']=Pipeline(modelOb.steps[:-1])
				tempMem[tempSecMem[processTheInput['sectionId']]]['featuresUsed']=colInfo[0]
				tempMem[tempSecMem[processTheInput['sectionId']]]['targetName']=colInfo[1]
			else:
				tempMem[tempSecMem[processTheInput['sectionId']]]['modelObj']=modelOb
			if model_graph != None:
				tempMem[tempSecMem[processTheInput['sectionId']]]['model_graph']=model_graph
				tempMem[tempSecMem[processTheInput['sectionId']]]['tf_session']=tf_session
			tempMem[tempSecMem[processTheInput['sectionId']]]['modelPath']=modelPath
			tempMem[tempSecMem[processTheInput['sectionId']]]['taskType']=processTheInput['taskType']
			
		
		MEMORY_DICT_ARCHITECTURE[projectID]['toExportDict']=tempMem.copy()

		# print ('tempMem',tempMem)

		model_to_pmml(MEMORY_DICT_ARCHITECTURE[projectID]['toExportDict'], PMMLFileName=MEMORY_DICT_ARCHITECTURE[projectID]['filePath'],tyP='multi')
		# print ('processTheInput',processTheInput)
		# print ('MEMORY_DICT_ARCHITECTURE[projectID]',MEMORY_DICT_ARCHITECTURE[projectID])

		returntoClient={'projectID':projectID,'layerUpdated':processTheInput}
		return JsonResponse(returntoClient)

	def deleteWorkflowlayer(payload,projectID):
		message={'message':'Success'}
		return JsonResponse(message)


	def deletelayer(payload,projectID):
		global MEMORY_DICT_ARCHITECTURE
		global lockForPMML
		# print ('>>>>>',userInput)

		existingArch=MEMORY_DICT_ARCHITECTURE[projectID]['architecture']
		
		# $update$
		filetoSave=MEMORY_DICT_ARCHITECTURE[projectID]['filePath']
		try:
			lockForPMML.acquire()
			existingPmmlObj=pml.parse(filetoSave,silence=True)
		except Exception as e:
			# print('>>>>>>>>>>>>>>>>> ', str(e))
			existingPmmlObj=None
		finally:
			lockForPMML.release()

		# existingPmmlObj=pml.parse(filetoSave, silence=True)

		processTheInput=payload['layerDelete']
		try:
		    deleteFromSection=processTheInput['sectionId']
		    if processTheInput['itemType']!='FOLDING':
		        idToDelete=processTheInput['id']
		        positionOfSection=existingArch.index([j for j in existingArch if j['itemType']=='FOLDING' if j['sectionId']==deleteFromSection][0])
		        positionInChildren=[j['id'] for j in existingArch[positionOfSection]['children']].index(idToDelete)
		        del existingArch[positionOfSection]['children'][positionInChildren]
		    else:
		        positionOfSection=existingArch.index([j for j in existingArch if j['itemType']=='FOLDING' if j['sectionId']==deleteFromSection][0])
		        del existingArch[positionOfSection]
		except:
		    idToDelete=processTheInput['id']
		    positionInArch=[j['id'] for j in existingArch].index(idToDelete)
		    del existingArch[positionInArch]
		    
		    
		for num,lay in enumerate(existingArch):
		    if lay['itemType']=='FOLDING':
		        for num2,levLay in enumerate(lay['children']):
		            levLay['layerIndex']=num2
		    else:
		        lay['layerIndex']=num

		import ast
		if processTheInput['itemType']=='FOLDING':
			sectionToDelete=processTheInput['sectionId']
			indexToDelete=-1
			existingNetworkLayers=existingPmmlObj.DeepNetwork[0].NetworkLayer
			for index, layer in enumerate(existingNetworkLayers):
				if layer.Extension:
					sectionId=ast.literal_eval(layer.Extension[0].value)['sectionId']
					if sectionId==sectionToDelete:
						indexToDelete=index
						break
			deleteTill=-1
			if indexToDelete!=-1:
				for idx in range(indexToDelete, len(existingNetworkLayers)):
					if not layer.Extension:
						deleteTill=idx-1
						break
					else:
						sectionId=ast.literal_eval(existingNetworkLayers[idx].Extension[0].value)['sectionId']
						if sectionId==sectionToDelete:
							deleteTill=idx
				if deleteTill==-1:
					del existingNetworkLayers[indexToDelete]
				else:
					existingNetworkLayers=existingNetworkLayers[:indexToDelete]+existingNetworkLayers[deleteTill+1:]
				existingNetworkLayers=resetNetworkLayer(existingNetworkLayers,indexToDelete)
				existingPmmlObj.DeepNetwork[0].NetworkLayer=existingNetworkLayers

		elif processTheInput['itemType']=='LAYER':
			layerIdToDelete=processTheInput['layerId']
			indexToDelete = -1
			for index, layer in enumerate(existingPmmlObj.DeepNetwork[0].NetworkLayer):
				if layer.layerId == layerIdToDelete:
					indexToDelete = index
					break
			if indexToDelete != -1:
				del existingPmmlObj.DeepNetwork[0].NetworkLayer[indexToDelete]
				existingNetworkLayers=resetNetworkLayer(existingPmmlObj.DeepNetwork[0].NetworkLayer,indexToDelete)
				existingPmmlObj.DeepNetwork[0].NetworkLayer=existingNetworkLayers
		
		if existingPmmlObj.Header.Extension:
			existingPmmlObj.Header.Extension[0].anytypeobjs_ = ['']
		for lay in existingPmmlObj.DeepNetwork[0].NetworkLayer:
			if lay.Extension:
				lay.Extension[0].anytypeobjs_ = ['']
		existingPmmlObj.DeepNetwork[0].numberOfLayers = len(existingPmmlObj.DeepNetwork[0].NetworkLayer)

		writePmml(existingPmmlObj, filetoSave, lockForPMML)
		
		MEMORY_DICT_ARCHITECTURE[projectID]['architecture']=existingArch
		message={'message':'Success'}

		return JsonResponse(message)

	def getGlobalObject():
		global MEMORY_DICT_ARCHITECTURE
		# print (MEMORY_DICT_ARCHITECTURE)
		return JsonResponse(MEMORY_DICT_ARCHITECTURE)

	def getDetailsOfPMML(filepath):
		# print ('Enter this world')
		pmmlObj=pml.parse(filepath,silence=True)
		tempObj=pmmlObj.__dict__

		if len(tempObj['DeepNetwork']) >0:
			layerList=[]
			for kk in tempObj['DeepNetwork'][0].NetworkLayer:
				layerList.append(kk.get_layerType())

			if (len(tempObj['script']) >=1) or ('LSTM' in layerList) or (tempObj['Header'].__dict__['description'] == 'Work Flow'):
				deployInfo=False
			else:
				deployInfo=True
		else:
			if (len(tempObj['script']) >=1) or (tempObj['Header'].__dict__['description'] == 'Work Flow'):
				deployInfo=False
			else:
				deployInfo=True


		
		listOfObjectstogetData=[]
		for j in tempObj.keys():
		    if (tempObj[j] is None) :
		        pass
		    elif (isinstance(tempObj[j], typing.List)):
		        if (len(tempObj[j])==0):
		            pass
		        else:
		            listOfObjectstogetData.append(j)
		    else:
		        listOfObjectstogetData.append(j)


		allInfo={}
		for towork in listOfObjectstogetData:
			if towork=='type_':
				allInfo['type']=tempObj['type_']
			if towork=='version':
				allInfo['Version']=tempObj['version']
			elif towork=='Header':
				allInfo.update(nyokaUtilities.getHeaderInfo(tempObj))
			elif towork=='DataDictionary':
				allInfo.update(nyokaUtilities.getDataFields(tempObj))
			elif towork=='NearestNeighborModel':
				allInfo.update(nyokaUtilities.getInfoNearestNeighborModel(tempObj))
			elif towork=='DeepNetwork':
				allInfo.update(nyokaUtilities.getInfoOfDeepNetwork(tempObj))
			elif towork=='MiningModel':
				allInfo.update(nyokaUtilities.getInfoMiningModel(tempObj))
			elif towork=='SupportVectorMachineModel':
				allInfo.update(nyokaUtilities.getInfoSupportVectorMachineModel(tempObj))
			elif towork=='TreeModel':
				allInfo.update(nyokaUtilities.getInfoTreeModel(tempObj))
			elif towork=='RegressionModel':
				allInfo.update(nyokaUtilities.getInfoLinearModel(tempObj))
			elif towork=='NaiveBayesModel':
				allInfo.update(nyokaUtilities.getInfoOfNaiveBayesModel(tempObj))
			elif towork=='AnomalyDetectionModel':
				allInfo.update(nyokaUtilities.getInfoOfAnomalyDetectionModel(tempObj))

		allInfo=nyokaUtilities.changeStructure(allInfo)
		allInfo['deployableToZAD']= deployInfo
		
		# print('response sent',allInfo)
		return JsonResponse(allInfo)


	

