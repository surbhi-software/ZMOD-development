from nyokaserver import nyokaUtilities,nyokaPMMLUtilities
# from nyokaBase import PMML43Ext as pml
from scoring.scoringClass import Scoring
# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
# from rest_framework.decorators import api_view,renderer_classes,
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from rest_framework.decorators import api_view,schema


from trainModel import kerasUtilities
from trainModel.kerasUtilities import PMMLMODELSTORAGE
kerasUtilities = kerasUtilities.KerasUtilities()

from nyokaBase.keras.pmml_to_keras_model import GenerateKerasModel 
from nyokaBase import PMML43Ext as ny
from keras.preprocessing.image import ImageDataGenerator

from keras.preprocessing import image
import ast,requests,json, os,subprocess,pathlib,traceback
from random import choice
from string import ascii_uppercase

from tensorflow import Graph, Session
import tensorflow as tf
from string import ascii_uppercase
from utility.utilityClass import RUNNING_TASK_MEMORY
import datetime,shutil
import skimage,pathlib
import pandas as pd
from nyokaBase.reconstruct.pmml_to_pipeline_model import generate_skl_model
from nyokaBase.skl.skl_to_pmml import model_to_pmml
from multiprocessing import Lock, Process
from threading import Thread

from trainModel import kerasUtilities
kerasUtilities = kerasUtilities.KerasUtilities()

logFolder='./logs/'
statusfileLocation = ''

modelObjectToCheck=['AssociationModel', 'AnomalyDetectionModel', 'BayesianNetworkModel',
                    'BaselineModel', 'ClusteringModel', 'DeepNetwork', 'GaussianProcessModel',
                    'GeneralRegressionModel', 'MiningModel', 'NaiveBayesModel', 'NearestNeighborModel', 
                    'NeuralNetwork', 'RegressionModel', 'RuleSetModel', 'SequenceModel', 'Scorecard', 
                    'SupportVectorMachineModel', 'TextModel', 'TimeSeriesModel', 'TreeModel']

global PMMLMODELSTORAGE

global SCRIPTSTORAGE

global RUNNING_TASK_MEMORY

SCRIPTSTORAGE={}

class NewModelOperations:

    def getCode(self,strngVal):
        lines = []
        code = strngVal.lstrip('\n')
        leading_spaces = len(code) - len(code.lstrip(' '))
        for line in code.split('\n'):
            lines.append(line[leading_spaces:])
        code = '\n'.join(lines)
        return code

    def getCodeObjectToProcess(self,codeVal):
        d = {}
        exec(codeVal, None,d)
        objeCode=d[list(d.keys())[0]]
        return objeCode

    def getTargetAndColumnsName(self,modObjToDetect):
        targetCol=None
        listOFColumns=[]
        if modObjToDetect.__dict__['original_tagname_'] in ['MiningModel','DeepNetwork']:
            for minF in modObjToDetect.get_MiningSchema().__dict__['MiningField']:
                if minF.__dict__['usageType'] == 'target':
                    targetCol=minF.__dict__['name']
                else:
                    listOFColumns.append(minF.__dict__['name'])
        else:
            print ('>>>>>>>>>>>>>>>>>>>>>>>>','Add support')
            targetCol=None
            listOFColumns=[]
        return listOFColumns,targetCol

    def nyObjOfModel(self,pmmlObj,singMod):
        import nyokaBase.PMML43Ext as ny
        if singMod['pmmlModelObject'].__dict__['original_tagname_']=='MiningModel':
            nyokaObj=ny.PMML(MiningBuildTask=pmmlObj.MiningBuildTask,DataDictionary=pmmlObj.DataDictionary,MiningModel=[singMod['pmmlModelObject']])
        elif singMod['pmmlModelObject'].__dict__['original_tagname_']=='DeepNetwork':
            nyokaObj=ny.PMML(DataDictionary=pmmlObj.DataDictionary,DeepNetwork=[singMod['pmmlModelObject']])
        else:
            nyokaObj=None
        return nyokaObj

    def loadExecutionModel(self,pmmlFile):
        pmmlFileObj=pathlib.Path(pmmlFile)
        pmmlFileForKey=pmmlFileObj.name.replace(pmmlFileObj.suffix,'')
        from nyokaBase import PMML43Ext as ny
        pmmlObj=ny.parse(pmmlFile,silence=True)

        modelObj=[]
        for inMod in modelObjectToCheck:
            if len(pmmlObj.__dict__[inMod]) >0:
                modPMMLObj=pmmlObj.__dict__[inMod]
                if inMod == 'DeepNetwork':
                    for ininMod in modPMMLObj:
                        colInfo=self.getTargetAndColumnsName(ininMod)
                        modelObj.append({'modelArchType':'NNModel','pmmlModelObject':ininMod,'recoModelObj':None,'listOFColumns':None,'targetCol':colInfo[1]})
                else:
                    for ininMod in modPMMLObj:
                        colInfo=self.getTargetAndColumnsName(ininMod)
        #                 recoModelObj=generateModelfromPMML(ininMod)
                        modelObj.append({'modelArchType':'SKLModel','pmmlModelObject':ininMod,'recoModelObj':None,'listOFColumns':colInfo[0],'targetCol':colInfo[1]})
        
        
        tempDict={}
        tempDict['train']={}

        tempDict['score']={}

        for singMod in modelObj:
            if singMod['pmmlModelObject'].taskType=='trainAndscore':
                tempDict['train'][singMod['pmmlModelObject'].modelName]={}
                tempDict['train'][singMod['pmmlModelObject'].modelName]['modelObj']=singMod
                tempDict['train'][singMod['pmmlModelObject'].modelName]['modelObj']['pmmlDdicObj']=pmmlObj.DataDictionary
                tempDict['train'][singMod['pmmlModelObject'].modelName]['modelObj']['pmmlNyokaObj']=self.nyObjOfModel(pmmlObj,singMod)
                tempDict['score'][singMod['pmmlModelObject'].modelName]={}
                tempDict['score'][singMod['pmmlModelObject'].modelName]['modelObj']=singMod
                tempDict['score'][singMod['pmmlModelObject'].modelName]['modelObj']['pmmlDdicObj']=pmmlObj.DataDictionary
                tempDict['train'][singMod['pmmlModelObject'].modelName]['modelObj']['pmmlNyokaObj']=self.nyObjOfModel(pmmlObj,singMod)
            else:
                tempDict[singMod['pmmlModelObject'].taskType][singMod['pmmlModelObject'].modelName]={}
                tempDict[singMod['pmmlModelObject'].taskType][singMod['pmmlModelObject'].modelName]['modelObj']=singMod
                tempDict[singMod['pmmlModelObject'].taskType][singMod['pmmlModelObject'].modelName]['modelObj']['pmmlDdicObj']=pmmlObj.DataDictionary
                tempDict[singMod['pmmlModelObject'].taskType][singMod['pmmlModelObject'].modelName]['modelObj']['pmmlNyokaObj']=self.nyObjOfModel(pmmlObj,singMod)
        
        tempDict2={}
        for taType in tempDict:
            tempTa=list(tempDict[taType].keys())
            tempTa.sort()
 
            for taTTemp in tempTa:
                if taType in tempDict2:
                    pass
                else:
                    tempDict2[taType]={}
                tempDict2[taType][taTTemp]=tempDict[taType][taTTemp]

        tempDict=tempDict2.copy()

        for sc1 in pmmlObj.script:
            if sc1.scriptPurpose=='trainAndscore':
                tempDict['train'][sc1.for_][sc1.class_]={}
                tempDict['train'][sc1.for_][sc1.class_+'_code']=self.getCode(sc1.valueOf_)
                tempDict['train'][sc1.for_][sc1.class_]=self.getCodeObjectToProcess(self.getCode(sc1.valueOf_))
                tempDict['score'][sc1.for_][sc1.class_]={}
                tempDict['score'][sc1.for_][sc1.class_+'_code']=self.getCode(sc1.valueOf_)
                tempDict['score'][sc1.for_][sc1.class_]=self.getCodeObjectToProcess(self.getCode(sc1.valueOf_))
            else:
                tempDict[sc1.scriptPurpose][sc1.for_][sc1.class_]={}
                tempDict[sc1.scriptPurpose][sc1.for_][sc1.class_+'_code']=self.getCode(sc1.valueOf_)
                tempDict[sc1.scriptPurpose][sc1.for_][sc1.class_]=self.getCodeObjectToProcess(self.getCode(sc1.valueOf_))


        taskTypesName=list(tempDict.keys())
        listOfModelNames=set([k for j in tempDict for k in tempDict[j]])

        hyperParDict={}
        for extObj in pmmlObj.MiningBuildTask.Extension:
            if extObj.name=='hyperparameters':
                hyperParDict[extObj.for_]=ast.literal_eval(extObj.value)

        try:
            miningBuildTaskList=pmmlObj.MiningBuildTask.__dict__['Extension']
            for bTask in miningBuildTaskList:
                if bTask.__dict__['for_'] in listOfModelNames:
                    for tT in taskTypesName:
                        for modInd in listOfModelNames:
                            tempDict[tT][modInd]['modelObj']['miningExtension']=bTask
        except:
            pass

        modelLoadStatus=[]

        for taskT in tempDict:
            print (taskT)
            for mO in tempDict[taskT]:
                if tempDict[taskT][mO]['modelObj']['modelArchType']=="NNModel":
                    modelProp=tempDict[taskT][mO]['modelObj']['pmmlNyokaObj']

                    model_graph = Graph()
                    with model_graph.as_default():
                        tf_session = Session()
                        with tf_session.as_default():
                            print ('step 5')
                            from nyokaBase.reconstruct.pmml_to_pipeline_model import generate_skl_model
                            print ('step 5.1')
                            model_net = generate_skl_model(modelProp)
                            print ('step 5.2')
                            model = model_net.model
                            model_graph = tf.get_default_graph()
                            print ('step 6')
                    inputShapevals=[inpuShape.value for inpuShape in list(model.input.shape)]
                    if str(model_net) != 'None':
                        tempDict[taskT][mO]['modelObj']['recoModelObj']=model_net
                        tempDict[taskT][mO]['modelObj']['model_graph']=model_graph
                        tempDict[taskT][mO]['modelObj']['tf_session']=tf_session
                        tempDict[taskT][mO]['modelObj']['inputShape']=inputShapevals
                        modelLoadStatus.append(1)
                    else:
                        modelLoadStatus.append(0)
                    try:
                        tempDict[taskT][mO]['modelObj']['hyperparameters']=hyperParDict[mO]
                    except:
                        tempDict[taskT][mO]['modelObj']['hyperparameters']=None
                elif tempDict[taskT][mO]['modelObj']['modelArchType']=="SKLModel":
                    modelProp=tempDict[taskT][mO]['modelObj']['pmmlNyokaObj']
                    from nyokaBase.reconstruct.pmml_to_pipeline_model import generate_skl_model
                    recoModelObj=generate_skl_model(modelProp)
                    if recoModelObj != None:
                        tempDict[taskT][mO]['modelObj']['recoModelObj']=recoModelObj
                        modelLoadStatus.append(1)
                    else:
                        modelLoadStatus.append(0)
                    try:
                        tempDict[taskT][mO]['modelObj']['hyperparameters']=hyperParDict[mO]
                    except:
                        tempDict[taskT][mO]['modelObj']['hyperparameters']=None

        # print('*'*100)

        # print(tempDict['score']['model2'])
        # print('*'*100)
        
        PMMLMODELSTORAGE[pmmlFileForKey]=tempDict
        if 0 in modelLoadStatus:
            messageToWorld= "Model load failed, please connect with admin"
        else:
            messageToWorld= "Model Loaded Successfully"

        resultResp={'message':messageToWorld,'keytoModel':pmmlFileForKey}
        return JsonResponse(resultResp,status=200)


class NewScoringDataView:

    global PMMLMODELSTORAGE

    def scoreJsonRecordsLongProcess(self,modelName,jsonData):
        scoreModelObj=NewScoringView()
        train_prc = Thread(target=scoreModelObj.wrapperForNewLogic,args=(modelName,jsonData,))
        train_prc.start()
        resa={'message':'Scoring Started'}
        return JsonResponse(resa)

class NewScoringView:

    def wrapperForNewLogic(self,modelName,jsonData):
        global PMMLMODELSTORAGE
        if modelName in PMMLMODELSTORAGE:
            scoredOutput=self.scoreJsonData(modelName,jsonData)
        else:
            pmmlFile='../ZMOD/Models/'+modelName+'.pmml'
            NewModelOperations().loadExecutionModel(pmmlFile)
            scoredOutput=self.scoreJsonData(modelName,jsonData)
        return scoredOutput

    def scoreJsonData(self,modelName,jsonData):
        global PMMLMODELSTORAGE
        # print('*'*100)
        # print(jsonData)
        # print('*'*100)

        modelInformation =PMMLMODELSTORAGE[modelName]
        modelObjs=list(modelInformation['score'].keys())
        if len(modelObjs)==0:
            resultResp={'result':'Model not for scoring'}
        elif len(modelObjs) ==1:
            modeScope=modelInformation['score'][modelObjs[0]]
            if 'preprocessing' in modeScope:
                # print (modeScope['preprocessing'])
                testData=modeScope['preprocessing'](jsonData)
                XVarForModel=modeScope['modelObj']['listOFColumns']
                testData=testData[XVarForModel]
            else:
                testData=pd.DataFrame([jsonData])

            print('>>>>>>>>>>>>>    modelObjs       ',type(testData),testData)
            if modeScope['modelObj']['modelArchType']=='NNModel':
                rowsIn=testData.shape[0]
                colsIn=testData.shape[1]
                testData=testData.values.reshape(rowsIn,1,colsIn)
                model_graph = modeScope['modelObj']['model_graph']
                tf_session = modeScope['modelObj']['tf_session']
                with model_graph.as_default():
                    with tf_session.as_default():
                        modelToUse=modeScope['modelObj']['recoModelObj'].model
                        resultData=modelToUse.predict(testData)
            else:
                resultData=modeScope['modelObj']['recoModelObj'].predict(testData)
            resultData=resultData.tolist()
            

            # resultData={'result':'Add support'}
        elif len(modelObjs) ==2:
            modeScope=modelInformation['score'][modelObjs[0]]
            if 'preprocessing' in modeScope:
                # print (modeScope['preprocessing'])
                testData=modeScope['preprocessing'](jsonData)
                XVarForModel=modeScope['modelObj']['listOFColumns']
                testData=testData[XVarForModel]
            else:
                testData=pd.DataFrame([jsonData])
            if modeScope['modelObj']['modelArchType']=='NNModel':
                rowsIn=testData.shape[0]
                colsIn=testData.shape[1]
                testData=testData.values.reshape(rowsIn,1,colsIn)
                model_graph = modeScope['modelObj']['model_graph']
                tf_session = modeScope['modelObj']['tf_session']
                with model_graph.as_default():
                    with tf_session.as_default():
                        modelToUse=modeScope['modelObj']['recoModelObj'].model
                        resultData=modelToUse.predict(testData)
            else:
                resultData=modeScope['modelObj']['recoModelObj'].predict(testData)
            #resultData=modeScope['modelObj']['recoModelObj'].predict(testData)

            modeScope2=modelInformation['score'][modelObjs[1]]
            # print ('modeScope2  >>>>>>>>>   ',modeScope2)
            if 'preprocessing' in modeScope2:
                testData=modeScope2['preprocessing'](testData,resultData)
            
            # print('*'*100)
            # print('testData shape',testData.shape)

            if modeScope2['modelObj']['modelArchType']=='NNModel':
                rowsIn=testData.shape[0]
                colsIn=testData.shape[1]
                testData=testData.values.reshape(rowsIn,1,colsIn)
                model_graph = modeScope2['modelObj']['model_graph']
                tf_session = modeScope2['modelObj']['tf_session']
                with model_graph.as_default():
                    with tf_session.as_default():
                        modelToUse=modeScope2['modelObj']['recoModelObj'].model
                        resultData=modelToUse.predict(testData)
            else:
                resultData=modeScope2['modelObj']['recoModelObj'].predict(testData)
            if 'postprocessing' in modeScope2:
                modeScope2['postprocessing'](testData,resultData)

            resultData=resultData.tolist()

        resultResp={'result':resultData}
        return JsonResponse(resultResp,status=200)

class NewTrainingView:

    global PMMLMODELSTORAGE

    def upDateStatus(self,statusFile):
        self.lockForStatus.acquire()
        sFile=open(statusFile,'r')
        sFileText=sFile.read()
        print (sFileText)
        data_details=json.loads(sFileText)
        sFile.close()
        self.lockForStatus.release()
        return data_details

    def trainAllModel(self,modelName):

        idforData=''.join(choice(ascii_uppercase) for i in range(12))
        saveStatus=logFolder+idforData+'/'
        kerasUtilities.checkCreatePath(saveStatus)
        statusfileLocation=saveStatus+'status.txt'

        pID=0

        tempRunMemory={'idforData': idforData,
			'status': 'Execution Failed' if pID==-1 else 'In Progress',
			'createdOn': str(datetime.datetime.now()),
			'type': 'NNModel',
			'pid':pID
            }
        tempRunMemory['taskName']=modelName
        RUNNING_TASK_MEMORY.append(tempRunMemory)
        with open(statusfileLocation,'w') as filetosave:
            json.dump(tempRunMemory, filetosave)
        import time
        time.sleep(5)
        
        trainVieClassObj=TrainingViewModels()
        train_prc = Thread(target=trainVieClassObj.trainModel,args=(modelName,statusfileLocation,))
        train_prc.start()
        pID = train_prc.ident
        tempRunMemory={'idforData': idforData,
			'status': 'Execution Failed' if pID==-1 else 'In Progress',
			'createdOn': str(datetime.datetime.now()),
			'type': 'NNModel',
			'pid':pID
            }
        tempRunMemory['taskName']=modelName
        RUNNING_TASK_MEMORY.append(tempRunMemory)
        with open(statusfileLocation,'w') as filetosave:
            json.dump(tempRunMemory, filetosave)

        
        return JsonResponse(tempRunMemory)



class TrainingViewModels:

    def __init__(self):
        self.statusFile = None
        self.lockForStatus = Lock()

    def upDateStatus(self,statusFile):
        print('Entered update code')
        self.lockForStatus.acquire()
        sFile=open(statusFile,'r')
        sFileText=sFile.read()
        print ('>>>>>>   ',sFileText)
        data_details=json.loads(sFileText)
        sFile.close()
        self.lockForStatus.release()
        return data_details

    def increName(self,nameList):
        import os
        nameList=nameList.split('_')
        if 'V' in nameList[-1]:
            nameExist=True
            while nameExist:
                toInc=int(nameList[-1][1:])+1
                nameList[-1]='V'+str(toInc)
                fName='_'.join(nameList)
                if os.path.exists('../ZMOD/Models/'+fName+'.pmml'):
                    nameExist=True
        else:
            fName='_'.join(nameList)+'_V'+str(1)
            nameList=fName.split('_')
            print ('Step 1 >>>>',fName,nameList)
            nameExist=os.path.exists('../ZMOD/Models/'+fName+'.pmml')
            while nameExist:
                toInc=int(nameList[-1][1:])+1
                nameList[-1]='V'+str(toInc)
                fName='_'.join(nameList)
                if os.path.exists('../ZMOD/Models/'+fName+'.pmml'):
                    nameExist=True
                else:
                    nameExist=False
        return fName

    def trainModel(self,modelName,statusFile):
        global PMMLMODELSTORAGE
        # self.statusFile=statusFile
        modelInformation =PMMLMODELSTORAGE[modelName]
        
        modelObjsTrain=list(modelInformation['train'].keys())
        print('model object loaded')

        if len(modelObjsTrain)==0:
            data_details=self.upDateStatus(statusFile)
            data_details['status']='Training Failed'
            data_details['errorMessage']='Error while selecting model to Train >> '+str(e)
            data_details['errorTraceback']=traceback.format_exc()
            with open(statusFile,'w') as filetosave:
                json.dump(data_details, filetosave)
        elif len(modelObjsTrain) ==2:
            data_details=self.upDateStatus(statusFile)
            data_details['status']='Training Failed'
            data_details['errorMessage']='Add support for training multiple model '+str(e)
            data_details['errorTraceback']=traceback.format_exc()
            with open(statusFile,'w') as filetosave:
                json.dump(data_details, filetosave)
        elif len(modelObjsTrain) ==1:
            print ('>>>>>>>>>>>>>>>                 ',statusFile)
            print('Came in model 1')
            modeScope=modelInformation['train'][modelObjsTrain[0]]
            data_details=self.upDateStatus(statusFile)
            data_details['status']='Training Model Loaded'
            print ('>>>>>>>>>>>>>>>                 ',statusFile)
            with open(statusFile,'w') as filetosave:
                json.dump(data_details, filetosave)
            if 'preprocessing' in modeScope:
                trainData=modeScope['preprocessing']()
                print (trainData.shape)
                print('Preprocess step completed')
                data_details=self.upDateStatus(statusFile)
                data_details['status']='Preprocessing for Model 1 Completed'
                with open(statusFile,'w') as filetosave:
                    json.dump(data_details, filetosave)
            else:
                data_details=self.upDateStatus(statusFile)
                data_details['status']='Training Failed'
                data_details['errorMessage']='Issue on preprocessing script for Model 1 '+str(e)
                data_details['errorTraceback']=traceback.format_exc()
                with open(statusFile,'w') as filetosave:
                    json.dump(data_details, filetosave)

            XVar=modeScope['modelObj']['listOFColumns']
            YVar=modeScope['modelObj']['targetCol']

            modltToTrain=modeScope['modelObj']['recoModelObj']
            print('Training step Started')
            data_details=self.upDateStatus(statusFile)
            data_details['status']='Training in Progress'
            with open(statusFile,'w') as filetosave:
                json.dump(data_details, filetosave)
            if str(type(modltToTrain))=="<class 'lightgbm.basic.Booster'>":
                print('Booster Model started')
                import lightgbm as lgb
                train_data=lgb.Dataset(trainData[XVar],trainData[YVar])
                modelHyParameters=modeScope['modelObj']['hyperparameters']
                newmodel1_ = lgb.train(modelHyParameters, train_data,init_model=modltToTrain)
                data_details=self.upDateStatus(statusFile)
                data_details['status']='Complete'
                with open(statusFile,'w') as filetosave:
                    json.dump(data_details, filetosave)

            elif 'sklearn.ensemble' in str(type(modltToTrain)):
                print('ensemble Model started')
                modelHyParameters=modeScope['modelObj']['hyperparameters']
                if YVar is None:
                    modltToTrain.fit(trainData[XVar])
                else:
                    print('XVar  >>>> ',XVar)
                    modltToTrain.fit(trainData[XVar],trainData[YVar])
                newmodel1_=modltToTrain
                
                data_details=self.upDateStatus(statusFile)
                data_details['status']='Complete'
                with open(statusFile,'w') as filetosave:
                    json.dump(data_details, filetosave)
            else:
                data_details=self.upDateStatus(statusFile)
                data_details['status']='Training Failed'
                data_details['errorMessage']='Add support for other model '+str(e)
                data_details['errorTraceback']=traceback.format_exc()
                with open(statusFile,'w') as filetosave:
                    json.dump(data_details, filetosave)

            modelInformation['score'][modelObjsTrain[0]]['modelObj']['recoModelObj']=modelInformation['train'][modelObjsTrain[0]]['modelObj']['recoModelObj']=newmodel1_
        print ('tempDict is ready to be')
        tempDict=modelInformation
        listOfModelNames=set([k for j in tempDict for k in tempDict[j]])
        listOfModelNames

        toExportDict={}
        for objDet in listOfModelNames:
            toExportDict[objDet]={'hyperparameters':None,
                'preProcessingScript':{'scripts':[], 'scriptpurpose':[]},
                'modelObj':None,
                'pipelineObj':None,
                'featuresUsed':None,
                'targetName':None,
                'postProcessingScript':{'scripts':[], 'scriptpurpose':[]},
                'taskType': None}

        for modObjeCom in tempDict:
            if modObjeCom == 'train':
                for echMod in toExportDict:
                    if echMod in tempDict[modObjeCom]:
                        print ('>>>>>',echMod)
                        if tempDict[modObjeCom][echMod]['modelObj']['modelArchType']=='NNModel':
                            toExportDict[echMod]['modelObj']=tempDict[modObjeCom][echMod]['modelObj']['recoModelObj']
                            toExportDict[echMod]['modelObj']['model_graph']=tempDict[modObjeCom][echMod]['modelObj']['model_graph']
                            toExportDict[echMod]['modelObj']['tf_session']=tempDict[modObjeCom][echMod]['modelObj']['tf_session']
                        else:
                            toExportDict[echMod]['modelObj']=tempDict[modObjeCom][echMod]['modelObj']['recoModelObj']
                        if 'preprocessing_code' in tempDict[modObjeCom][echMod]:
                            toExportDict[echMod]['preProcessingScript']['scripts'].append(tempDict[modObjeCom][echMod]['preprocessing_code'])
                            toExportDict[echMod]['preProcessingScript']['scriptpurpose'].append(modObjeCom)
                        if 'postprocessing_code' in tempDict[modObjeCom][echMod]:
                            toExportDict[echMod]['postProcessingScript']['scripts'].append(tempDict[modObjeCom][echMod]['postprocessing_code'])
                            toExportDict[echMod]['postProcessingScript']['scriptpurpose'].append(modObjeCom)
                        toExportDict[echMod]['taskType']=modObjeCom
                        toExportDict[echMod]['featuresUsed']=tempDict[modObjeCom][echMod]['modelObj']['listOFColumns']
                        toExportDict[echMod]['targetName']=tempDict[modObjeCom][echMod]['modelObj']['targetCol']
                        toExportDict[echMod]['hyperparameters']=tempDict[modObjeCom][echMod]['modelObj']['hyperparameters']
            if modObjeCom == 'score':
                for echMod in toExportDict:
                    if echMod in tempDict[modObjeCom]:
                        print ('>>>>',echMod)
                        if tempDict[modObjeCom][echMod]['modelObj']['modelArchType']=='NNModel':
        #                     print (tempDict[modObjeCom][echMod]['modelObj'])
                            toExportDict[echMod]['modelObj']=tempDict[modObjeCom][echMod]['modelObj']['recoModelObj']
                            toExportDict[echMod]['model_graph']=tempDict[modObjeCom][echMod]['modelObj']['model_graph']
                            toExportDict[echMod]['tf_session']=tempDict[modObjeCom][echMod]['modelObj']['tf_session']
                        else:
                            toExportDict[echMod]['modelObj']=tempDict[modObjeCom][echMod]['modelObj']['recoModelObj']
                        if 'preprocessing_code' in tempDict[modObjeCom][echMod]:
                            toExportDict[echMod]['preProcessingScript']['scripts'].append(tempDict[modObjeCom][echMod]['preprocessing_code'])
                            toExportDict[echMod]['preProcessingScript']['scriptpurpose'].append(modObjeCom)
                        if 'postprocessing_code' in tempDict[modObjeCom][echMod]:
                            toExportDict[echMod]['postProcessingScript']['scripts'].append(tempDict[modObjeCom][echMod]['postprocessing_code'])
                            toExportDict[echMod]['postProcessingScript']['scriptpurpose'].append(modObjeCom)
                        toExportDict[echMod]['taskType']=modObjeCom
                        toExportDict[echMod]['featuresUsed']=tempDict[modObjeCom][echMod]['modelObj']['listOFColumns']
                        toExportDict[echMod]['targetName']=tempDict[modObjeCom][echMod]['modelObj']['targetCol']
                        toExportDict[echMod]['hyperparameters']=tempDict[modObjeCom][echMod]['modelObj']['hyperparameters']
                        
        for modNa in listOfModelNames:
            if (modNa in tempDict['train']) & (modNa in tempDict['score']):
                toExportDict[modNa]['taskType']='trainAndscore'
            if ((modNa in tempDict['train'] )== False) & (modNa in tempDict['score']):
                toExportDict[modNa]['taskType']='score'

        tempTa2=list(toExportDict.keys())
        tempTa2.sort()
        toExportReOrdered={}
        for taTTemp2 in tempTa2:
            toExportReOrdered[taTTemp2]=toExportDict[taTTemp2]

        toExportDict=toExportReOrdered.copy()

        # print ('8'*100)
        # print (modelInformation['score']['model2'])
        # print ('8'*100)

        print('*'*100)

        print (toExportDict)
        print('*'*100)
        orgfName='../ZMOD/Models/'+modelName+'.pmml'
        copyOrgFName='../ZMOD/Models/'+self.increName(modelName)+'.pmml'

        shutil.copy2(orgfName,copyOrgFName)
        model_to_pmml(toExportDict, pmml_f_name=copyOrgFName)
        NewModelOperations().loadExecutionModel(orgfName)
        data_details=self.upDateStatus(statusFile)
        data_details['status']='Model Saved in different Version'
        # data_details['errorMessage']='Add support for other model '+str(e)
        # data_details['errorTraceback']=traceback.format_exc()
        with open(statusFile,'w') as filetosave:
            json.dump(data_details, filetosave)

        return JsonResponse(data_details)


class CodeExecutionFeatureCalc:

    global SCRIPTSTORAGE

    def getCodeObjectToProcess(self,codeVal):
        d = {}
        exec(codeVal, None,d)
        objeCode=d[list(d.keys())[0]]
        return objeCode

    def loadCodeForExec(self,filePath):

        try:
            pathObj=pathlib.Path(filePath)
            codeKey=pathObj.name.replace(pathObj.suffix,'')

            filVal=open(filePath,'r').read()
            codeObj=self.getCodeObjectToProcess(filVal)
            SCRIPTSTORAGE[codeKey]=codeObj
            return JsonResponse({'result':'Code Load Success','codeKey':codeKey},status=200)
        except:
            return JsonResponse({'result':'Some error occured'},status=500)


    def executeFeatureScript(self,scriptName,jsonData):
        global SCRIPTSTORAGE

        # try:
        if scriptName in SCRIPTSTORAGE:
            scriptFunction =SCRIPTSTORAGE[scriptName]
            calcFeatureval=scriptFunction(jsonData)
            resultResp={'result':calcFeatureval}
            return JsonResponse(resultResp,status=200)
        else:
            fPath='../ZMOD/Code/'+scriptName+'.py'
            self.loadCodeForExec(fPath)
            if scriptName in SCRIPTSTORAGE:
                scriptFunction =SCRIPTSTORAGE[scriptName]
                calcFeatureval=scriptFunction(jsonData)
                resultResp={'result':calcFeatureval}
                return JsonResponse(resultResp,status=200)
        # except:
        #     resultResp={'result':'Sccript Exec Faield'}
        #     return JsonResponse(resultResp,status=500)