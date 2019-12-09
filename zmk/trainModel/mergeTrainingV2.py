import pandas  as pd
from django.http import JsonResponse
import numpy as np
from sklearn import model_selection,preprocessing
from keras.preprocessing.image import ImageDataGenerator
from datetime import datetime
import matplotlib.pyplot as plt
from datetime import datetime
from keras import optimizers
import sys, os,ast,json,copy,traceback,pathlib
from keras import backend as K
import keras
from multiprocessing import Process
from trainModel import kerasUtilities
kerasUtilities = kerasUtilities.KerasUtilities()
from multiprocessing import Lock, Process
from nyokaBase import PMML43Ext as ny
from tensorflow import Graph, Session
import tensorflow as tf

global PMMLMODELSTORAGE

PMMLMODELSTORAGE={}


modelObjectToCheck=['AssociationModel', 'AnomalyDetectionModel', 'BayesianNetworkModel',
                    'BaselineModel', 'ClusteringModel', 'DeepNetwork', 'GaussianProcessModel',
                    'GeneralRegressionModel', 'MiningModel', 'NaiveBayesModel', 'NearestNeighborModel', 
                    'NeuralNetwork', 'RegressionModel', 'RuleSetModel', 'SequenceModel', 'Scorecard', 
                    'SupportVectorMachineModel', 'TextModel', 'TimeSeriesModel', 'TreeModel']

selDev="/device:CPU:0"
def gpuCPUSelect(selDev):
	return selDev

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
        if modObjToDetect.__dict__['original_tagname_'] in ['MiningModel','DeepNetwork','RegressionModel','AnomalyDetectionModel']:
            try:
                for minF in modObjToDetect.get_MiningSchema().__dict__['MiningField']:
                    if minF.__dict__['usageType'] == 'target':
                        targetCol=minF.__dict__['name']
                    else:
                        listOFColumns.append(minF.__dict__['name'])
            except:
                pass
            try:
                modelPath=modObjToDetect.get_filePath()
            except:
                modelPath=None
        else:
            print ('>>>>>>>>>>>>>>>>>>>>>>>>','Add support')
            targetCol=None
            listOFColumns=[]
        return listOFColumns,targetCol,modelPath

    def nyObjOfModel(self,pmmlObj,singMod):
        import nyokaBase.PMML43Ext as ny
        if singMod['pmmlModelObject'].__dict__['original_tagname_']=='MiningModel':
            nyokaObj=ny.PMML(MiningBuildTask=pmmlObj.MiningBuildTask,DataDictionary=pmmlObj.DataDictionary,MiningModel=[singMod['pmmlModelObject']])
        elif singMod['pmmlModelObject'].__dict__['original_tagname_']=='DeepNetwork':
            nyokaObj=ny.PMML(DataDictionary=pmmlObj.DataDictionary,DeepNetwork=[singMod['pmmlModelObject']])
        elif singMod['pmmlModelObject'].__dict__['original_tagname_']=='RegressionModel':
            nyokaObj=ny.PMML(MiningBuildTask=pmmlObj.MiningBuildTask,DataDictionary=pmmlObj.DataDictionary,RegressionModel=[singMod['pmmlModelObject']])
        elif singMod['pmmlModelObject'].__dict__['original_tagname_']=='AnomalyDetectionModel':
            nyokaObj=ny.PMML(MiningBuildTask=pmmlObj.MiningBuildTask,DataDictionary=pmmlObj.DataDictionary,AnomalyDetectionModel=[singMod['pmmlModelObject']])
        elif singMod['pmmlModelObject'].__dict__['original_tagname_']=='NeuralNetwork':
            nyokaObj=ny.PMML(MiningBuildTask=pmmlObj.MiningBuildTask,DataDictionary=pmmlObj.DataDictionary,NeuralNetwork=[singMod['pmmlModelObject']])
        elif singMod['pmmlModelObject'].__dict__['original_tagname_']=='SupportVectorMachineModel':
            nyokaObj=ny.PMML(MiningBuildTask=pmmlObj.MiningBuildTask,DataDictionary=pmmlObj.DataDictionary,SupportVectorMachineModel=[singMod['pmmlModelObject']])
        elif singMod['pmmlModelObject'].__dict__['original_tagname_']=='SupportVectorMachineModel':
            nyokaObj=ny.PMML(MiningBuildTask=pmmlObj.MiningBuildTask,DataDictionary=pmmlObj.DataDictionary,ClusteringModel=[singMod['pmmlModelObject']])
        elif singMod['pmmlModelObject'].__dict__['original_tagname_']=='ClusteringModel':
            nyokaObj=ny.PMML(MiningBuildTask=pmmlObj.MiningBuildTask,DataDictionary=pmmlObj.DataDictionary,AnomalyDetectionModel=[singMod['pmmlModelObject']])
        elif singMod['pmmlModelObject'].__dict__['original_tagname_']=='NearestNeighborModel':
            nyokaObj=ny.PMML(MiningBuildTask=pmmlObj.MiningBuildTask,DataDictionary=pmmlObj.DataDictionary,NearestNeighborModel=[singMod['pmmlModelObject']])
        elif singMod['pmmlModelObject'].__dict__['original_tagname_']=='NaiveBayesModel':
            nyokaObj=ny.PMML(MiningBuildTask=pmmlObj.MiningBuildTask,DataDictionary=pmmlObj.DataDictionary,NaiveBayesModel=[singMod['pmmlModelObject']])
        else:
            nyokaObj=None
        return nyokaObj

    def getPredictionClassName(self,pmmlObj):
        try:
            predClasses=[]
            for j in pmmlObj.__dict__['DataDictionary'].__dict__['DataField']:
                if j.get_name()=='predictions':
                    print (j)
                    for k in j.get_Value():
                        predClasses.append(k.__dict__['value'])
                    return predClasses
        except:
            return None

    def loadExecutionModel(self,pmmlFile):
        # print ('loadmodel started')
        # print (pmmlFile)
        global PMMLMODELSTORAGE
        pmmlFileObj=pathlib.Path(pmmlFile)
        pmmlFileForKey=pmmlFileObj.name.replace(pmmlFileObj.suffix,'')
        from nyokaBase import PMML43Ext as ny
        pmmlObj=ny.parse(pmmlFile,silence=True)
        # print (pmmlObj)
        print ('load model step 1.0')
        modelObj=[]
        for inMod in modelObjectToCheck:
            if len(pmmlObj.__dict__[inMod]) >0:
                modPMMLObj=pmmlObj.__dict__[inMod]
                if inMod == 'DeepNetwork':
                    print ('load model step 1.0.0')
                    for ininMod in modPMMLObj:
                        colInfo=self.getTargetAndColumnsName(ininMod)
                        modelObj.append({'modelArchType':'NNModel','pmmlModelObject':ininMod,'recoModelObj':None,'listOFColumns':None,'targetCol':colInfo[1],'modelPath':colInfo[2]})
                else:
                    for ininMod in modPMMLObj:
                        colInfo=self.getTargetAndColumnsName(ininMod)
        #                 recoModelObj=generateModelfromPMML(ininMod)
                        modelObj.append({'modelArchType':'SKLModel','pmmlModelObject':ininMod,'recoModelObj':None,'listOFColumns':colInfo[0],'targetCol':colInfo[1],'modelPath':colInfo[2]})
        
        print ('load model step 1.1')
        tempDict={}
        tempDict['train']={}

        tempDict['score']={}
        print ('print  step LM 1')
        for singMod in modelObj:
            if singMod['pmmlModelObject'].taskType=='trainAndscore':
                tempDict['train'][singMod['pmmlModelObject'].modelName]={}
                tempDict['train'][singMod['pmmlModelObject'].modelName]['modelObj']=singMod
                tempDict['train'][singMod['pmmlModelObject'].modelName]['modelObj']['pmmlDdicObj']=pmmlObj.DataDictionary
                tempDict['train'][singMod['pmmlModelObject'].modelName]['modelObj']['pmmlNyokaObj']=self.nyObjOfModel(pmmlObj,singMod)
                tempDict['train'][singMod['pmmlModelObject'].modelName]['modelObj']['predictedClasses']=self.getPredictionClassName(pmmlObj)
                tempDict['score'][singMod['pmmlModelObject'].modelName]={}
                tempDict['score'][singMod['pmmlModelObject'].modelName]['modelObj']=singMod
                tempDict['score'][singMod['pmmlModelObject'].modelName]['modelObj']['pmmlDdicObj']=pmmlObj.DataDictionary
                tempDict['score'][singMod['pmmlModelObject'].modelName]['modelObj']['pmmlNyokaObj']=self.nyObjOfModel(pmmlObj,singMod)
                tempDict['score'][singMod['pmmlModelObject'].modelName]['modelObj']['predictedClasses']=self.getPredictionClassName(pmmlObj)
            else:
                tempDict[singMod['pmmlModelObject'].taskType][singMod['pmmlModelObject'].modelName]={}
                tempDict[singMod['pmmlModelObject'].taskType][singMod['pmmlModelObject'].modelName]['modelObj']=singMod
                tempDict[singMod['pmmlModelObject'].taskType][singMod['pmmlModelObject'].modelName]['modelObj']['pmmlDdicObj']=pmmlObj.DataDictionary
                tempDict[singMod['pmmlModelObject'].taskType][singMod['pmmlModelObject'].modelName]['modelObj']['pmmlNyokaObj']=self.nyObjOfModel(pmmlObj,singMod)
                tempDict[singMod['pmmlModelObject'].taskType][singMod['pmmlModelObject'].modelName]['modelObj']['predictedClasses']=self.getPredictionClassName(pmmlObj)
        print ('print  step LM 2')
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

        print ('print  step LM 3')

        tempDict=tempDict2.copy()

        # print (tempDict)

        for sc1 in pmmlObj.script:
            if sc1.scriptPurpose=='trainAndscore':
                tempDict['train'][sc1.for_][sc1.class_]={}
                tempDict['train'][sc1.for_][sc1.class_]['codeCont']=self.getCode(sc1.valueOf_)
                tempDict['train'][sc1.for_][sc1.class_]['codeObj']=self.getCodeObjectToProcess(self.getCode(sc1.valueOf_))
                tempDict['train'][sc1.for_][sc1.class_]['scriptOutput']=sc1.scriptOutput
                tempDict['train'][sc1.for_][sc1.class_]['scriptPath']=sc1.filePath
                # tempDict['train'][sc1.for_][sc1.class_]['scriptPurpose']=sc1.filePath
                tempDict['score'][sc1.for_][sc1.class_]={}
                tempDict['score'][sc1.for_][sc1.class_]['codeCont']=self.getCode(sc1.valueOf_)
                tempDict['score'][sc1.for_][sc1.class_]['codeObj']=self.getCodeObjectToProcess(self.getCode(sc1.valueOf_))
                tempDict['score'][sc1.for_][sc1.class_]['scriptOutput']=sc1.scriptOutput
                tempDict['score'][sc1.for_][sc1.class_]['scriptPath']=sc1.filePath
                # tempDict['train'][sc1.for_][sc1.class_]['scriptPurpose']=sc1.filePath
            else:
                tempDict[sc1.scriptPurpose][sc1.for_][sc1.class_]={}
                tempDict[sc1.scriptPurpose][sc1.for_][sc1.class_]['codeCont']=self.getCode(sc1.valueOf_)
                tempDict[sc1.scriptPurpose][sc1.for_][sc1.class_]['codeObj']=self.getCodeObjectToProcess(self.getCode(sc1.valueOf_))
                tempDict[sc1.scriptPurpose][sc1.for_][sc1.class_]['scriptOutput']=sc1.scriptOutput
                tempDict[sc1.scriptPurpose][sc1.for_][sc1.class_]['scriptPath']=sc1.filePath

        # print (tempDict)
        print ('print  step LM 4')

        taskTypesName=list(tempDict.keys())
        listOfModelNames=set([k for j in tempDict for k in tempDict[j]])

        
        try:
            hyperParDict={}
            for extObj in pmmlObj.MiningBuildTask.Extension:
                if extObj.name=='hyperparameters':
                    hyperParDict[extObj.for_]=ast.literal_eval(extObj.value)
        except:
            hyperParDict=None

        try:
            miningBuildTaskList=pmmlObj.MiningBuildTask.__dict__['Extension']
            for bTask in miningBuildTaskList:
                if bTask.__dict__['for_'] in listOfModelNames:
                    for tT in taskTypesName:
                        for modInd in listOfModelNames:
                            tempDict[tT][modInd]['modelObj']['miningExtension']=bTask
        except:
            pass

        print ('print  step LM 5')
        for dO in pmmlObj.Data:
            for tT in taskTypesName:
                for modInd in listOfModelNames:
                    print (tT,modInd)
                    if dO.for_ == modInd:
                        try:
                            tempDict[tT][modInd]['Data']=dO.filePath
                        except:
                            pass

        modelLoadStatus=[]

        # print ('tempDict  >>>>>>>>>>> ',tempDict)

        for taskT in tempDict:
            # print (taskT)
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
                    # print ('>>>>>>>>>>>>>>>>>>>>>>>',modelProp)
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

        
        
        PMMLMODELSTORAGE[pmmlFileForKey]=tempDict

        # print('*'*100)

        # print(PMMLMODELSTORAGE)
        # print('*'*100)
        if 0 in modelLoadStatus:
            messageToWorld= "Model load failed, please connect with admin"
        else:
            messageToWorld= "Model Loaded Successfully"

        resultResp={'message':messageToWorld,'keytoModel':pmmlFileForKey}
        print (resultResp)
        return JsonResponse(resultResp,status=200)


class NewTrainingView:

    global PMMLMODELSTORAGE

    def upDateStatus(self,statusFile):
        self.lockForStatus.acquire()
        sFile=open(statusFile,'r')
        sFileText=sFile.read()
        # print (sFileText)
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
        self.logFolder = 'logs/'
        self.lockForStatus = Lock()

    def upDateStatus(self):
        self.lockForStatus.acquire()
        sFile=open(self.statusFile,'r')
        sFileText=sFile.read()
        data_details=json.loads(sFileText)
        sFile.close()
        self.lockForStatus.release()
        return data_details

    def setOptimizer(self, optimizerName, learningRate):

        if optimizerName == 'Adadelta':
            opti=optimizers.Adadelta(lr=learningRate, rho=0.95, epsilon=None, decay=0.0)
        elif optimizerName == 'Adagrad':
            opti=optimizers.Adagrad(lr=learningRate, epsilon=None, decay=0.0)
        elif optimizerName == 'Adam':
            opti=optimizers.Adam(lr=learningRate, beta_1=0.9, beta_2=0.999, epsilon=None, decay=1e-6, amsgrad=False)
        elif optimizerName == 'Adamax':
            opti=optimizers.Adamax(lr=learningRate, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0)
        elif optimizerName == 'Nadam':
            opti=optimizers.Nadam(lr=learningRate, beta_1=0.9, beta_2=0.999, epsilon=None, schedule_decay=0.004)
        elif optimizerName == 'Rmsprop':
            opti=optimizers.RMSprop(lr=learningRate, rho=0.9, epsilon=None, decay=0.0)
        elif optimizerName == 'Sgd':
            opti=optimizers.SGD(lr=learningRate, momentum=0.0, decay=0.0, nesterov=False)
        else:
            opti=optimizers.Adam(lr=learningRate, beta_1=0.9, beta_2=0.999, epsilon=None, decay=1e-6, amsgrad=False)
        return opti

    def updateStatusWithError(self,data_details,statusOFExe,errorMessage,errorTraceback,statusFile):
        data_details=self.upDateStatus()
        data_details['status']=statusOFExe
        data_details['errorMessage']=errorMessage
        data_details['errorTraceback']=errorTraceback
        with open(statusFile,'w') as filetosave:
            json.dump(data_details, filetosave)
        return ('done')

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

    def f1(self,y_true, y_pred):
        def recall(y_true, y_pred):
            true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
            possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
            recall = true_positives / (possible_positives + K.epsilon())
            return recall

        def precision(y_true, y_pred):
            true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
            predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
            precision = true_positives / (predicted_positives + K.epsilon())
            return precision
        precision = precision(y_true, y_pred)
        recall = recall(y_true, y_pred)
        return 2*((precision*recall)/(precision+recall+K.epsilon()))


    def generateAndCompileModel(self,modelObjZG, lossType, optimizerName, learningRate, listOfMetrics, compileTestOnly=False):

       
        try:
            optiMi=self.setOptimizer(optimizerName,learningRate)
        except Exception as e:
            if not compileTestOnly:
                data_details=self.upDateStatus()
                self.updateStatusWithError(data_details,'Training Failed','Unable to get the optimizer '+optimizerName+' >> '+ str(e),traceback.format_exc(),self.statusFile)
            else:
                data_details = {}
                self.updateStatusWithError(data_details,'Model Compilation Failed','Error while compiling the Model >> '+ str(e),traceback.format_exc(),self.statusFile)
            return data_details

        try:
            model_graph = modelObjZG['modelObj']['model_graph']
            tf_session = modelObjZG['modelObj']['tf_session']
            # print ('model_graph,tf_session',model_graph,tf_session)
            with model_graph.as_default():
                with tf_session.as_default():
                    model=modelObjZG['modelObj']['recoModelObj'].model
                    if 'f1' in listOfMetrics:
                        listOfMetrics.remove('f1')
                        model.compile(optimizer=optiMi, loss=lossType, metrics=listOfMetrics+[self.f1])
                    else:
                        model.compile(optimizer=optiMi, loss=lossType, metrics=listOfMetrics)
        except Exception as e:
            if not compileTestOnly:
                data_details=self.upDateStatus()
                self.updateStatusWithError(data_details,'Training Failed','Error while compiling Model >> '+ str(e),traceback.format_exc(),self.statusFile)
            else:
                data_details = {}
                self.updateStatusWithError(data_details,'Model Compilation Failed','Error while compiling Model >> '+ str(e),traceback.format_exc(),self.statusFile)
            return data_details
        if not compileTestOnly:
            kerasUtilities.updateStatusOfTraining(self.statusFile,'Model Successfully compiled')
        return model,model_graph,tf_session

    def startTensorBoard(self, tensorboardLogFolder):
        # print ('tensorboardLogFolder >>>>>>',tensorboardLogFolder)
        tensor_board=keras.callbacks.TensorBoard(log_dir=tensorboardLogFolder, histogram_freq=0,write_graph=True, write_images=False)
        return tensor_board
    def kerasDataPrep(self,dataFolder,batch_size,img_height, img_width):
        train_data_dir=dataFolder+'/'+'train/'
        val_data_dir=dataFolder+'/'+'validation/'

        train_datagen = ImageDataGenerator(rescale=1. / 255,shear_range=0.2,zoom_range=0.2,horizontal_flip=True)
        test_datagen = ImageDataGenerator(rescale=1. / 255)

        train_generator = train_datagen.flow_from_directory(train_data_dir,target_size=(img_height, img_width),
        batch_size=batch_size,class_mode='categorical')
        if os.path.exists(val_data_dir)==True:
            validation_generator = test_datagen.flow_from_directory(val_data_dir,target_size=(img_height, img_width),
            batch_size=batch_size,class_mode='categorical')
            return train_generator,validation_generator,len(train_generator.class_indices)
        else:
            return train_generator,None,len(train_generator.class_indices)

    def verifyHyperparameters(self,datHyperPara):
        try:
            lossType=datHyperPara['loss']
        except Exception as e:
            self.pathOfData=None
            data_details=self.upDateStatus()
            self.updateStatusWithError(data_details,'Training Failed',"Couldn't find hyperparameters lossType >> "+ str(e),traceback.format_exc(),self.statusFile)
            return -1
        try:
            listOfMetrics=datHyperPara['metrics']
        except Exception as e:
            self.pathOfData=None
            data_details=self.upDateStatus()
            self.updateStatusWithError(data_details,'Training Failed',"Couldn't find hyperparameters listOfMetrics >> "+ str(e),traceback.format_exc(),self.statusFile)
            return -1

        try:
            batchSize=datHyperPara['batchSize']
        except Exception as e:
            self.pathOfData=None
            data_details=self.upDateStatus()
            self.updateStatusWithError(data_details,'Training Failed',"Couldn't find hyperparameters batchSize >> "+ str(e),traceback.format_exc(),self.statusFile)
            return -1

        try:
            epoch=datHyperPara['epoch']
        except Exception as e:
            self.pathOfData=None
            data_details=self.upDateStatus()
            self.updateStatusWithError(data_details,'Training Failed',"Couldn't find hyperparameters epoch >> "+ str(e),traceback.format_exc(),self.statusFile)
            return -1

        try:
            problemType=datHyperPara['problemType']
        except Exception as e:
            self.pathOfData=None
            data_details=self.upDateStatus()
            self.updateStatusWithError(data_details,'Training Failed',"Couldn't find hyperparameters problemType >> "+ str(e),traceback.format_exc(),self.statusFile)
            return -1

        try:
            optimizerName=datHyperPara['optimizer']
        except Exception as e:
            self.pathOfData=None
            data_details=self.upDateStatus()
            self.updateStatusWithError(data_details,'Training Failed',"Couldn't find hyperparameters optimizerName >> "+ str(e),traceback.format_exc(),self.statusFile)
            return -1

        try:
            learningRate=datHyperPara['learningRate']
        except Exception as e:
            self.pathOfData=None
            data_details=self.upDateStatus()
            self.updateStatusWithError(data_details,'Training Failed',"Couldn't find hyperparameters learningRate >> "+ str(e),traceback.format_exc(),self.statusFile)
            return -1

        try:
            testSize=datHyperPara['testSize']
        except Exception as e:
            testSize=None
        return 'done'
    def trainModelObjectDict(self,modelObj,idforData,tensorboardLogFolder):
        print ('modelObj???????????????????',modelObj)
        try:
            dataObj=modelObj['Data']
            print ('dataObj',dataObj)
        except:
            dataObj=None
        modelArch=modelObj['modelObj']['modelArchType']
        try:
            scriptOutputPrepro=modelObj['preprocessing']['scriptOutput']
        except:
            scriptOutputPrepro=None
        
        print ('scriptOutputPrepro',scriptOutputPrepro,dataObj,modelArch)
        datHyperPara=modelObj['modelObj']['hyperparameters']
        
        if modelArch == 'NNModel':
            print ('came to final model training')
            checkVal=self.verifyHyperparameters(datHyperPara)
            if checkVal == 'done':
                pass
            else:
                data_details=self.upDateStatus()
                self.updateStatusWithError(data_details,'Training Failed',"Some issue with hyperparameters >> ",'No info',self.statusFile)
                return -1

        try:
            if (dataObj == None) & (scriptOutputPrepro != None):
                print ('To complicated 1')
                modelObjTrained=self.trainComplicatedDNNObj(modelObj,tensorboardLogFolder,scriptOutputPrepro)
            elif (os.path.isdir(dataObj)) & (scriptOutputPrepro==None):
                print ('Came to Image classifier')
                modelObjTrained=self.trainImageClassifierNN(modelObj,tensorboardLogFolder)
            elif (pathlib.Path(dataObj).suffix == '.csv') & (scriptOutputPrepro==None) :
                print('Simple DNN')
                dataObjPd=pd.read_csv(modelObj['Data'])
                print (dataObjPd.shape)
                modelObjTrained=self.trainSimpleDNNObj(modelObj,tensorboardLogFolder,dataObjPd)
            elif (pathlib.Path(dataObj).suffix == '.csv') & (scriptOutputPrepro!=None) :
                dataObjPd=pd.read_csv(modelObj['Data'])
                print (dataObjPd.shape)
                print('Simple DNN with preprocessing',modelObj,tensorboardLogFolder)
                modelObjTrained=self.trainSimpleDNNObjWithPrepro(modelObj,tensorboardLogFolder,dataObjPd)
                
            else:
                data_details=self.upDateStatus()
                self.updateStatusWithError(data_details,'Training Failed',"Not supported >> ",'No traceback',self.statusFile)
                return -1
        except:
            data_details=self.upDateStatus()
            self.updateStatusWithError(data_details,'Training Failed',"Not supported >> ",'No traceback',self.statusFile)
            return -1
        return modelObjTrained


    def trainSimpleDNNObj(self,modelObj,tensorboardLogFolder,dataObj):
        dataFolder=modelObj['Data']
        # modelToCompile=modelObj['modelObj']['recoModelObj']
        datHyperPara=modelObj['modelObj']['hyperparameters']
        listOfMetrics=datHyperPara['metrics']
        modelV1=modelObj['modelObj']['recoModelObj'].model
        print(">>>>>>>>>>>>>>SimpleDNN")
        print('pathofdata>>>>>',dataFolder)
        predictedClasses=None
        targetColumnName = 'target'
        df = dataObj
        indevar=list(df.columns)
        indevar.remove('target')
        targetCol = df[targetColumnName]
        if datHyperPara['problemType']=='classification':
            lb=preprocessing.LabelBinarizer()
            y=lb.fit_transform(targetCol)
            predictedClass = list(targetCol.unique())
        else:
            y=df[targetColumnName]
            predictedClass=None
        ##### Split data into test and validation set for training#################################
        trainDataX,testDataX,trainDataY,testDataY=model_selection.train_test_split(df[indevar],y,
                                                        test_size=datHyperPara['testSize'])
        stepsPerEpochT=int(len(trainDataX)/datHyperPara['batchSize'])
        stepsPerEpochV=int(len(testDataX)/datHyperPara['batchSize'])
        kerasUtilities.updateStatusOfTraining(self.statusFile,'Data split in Train validation part')

        # modelObj = self.generateAndCompileModel(datHyperPara['lossType'],datHyperPara['optimizerName'],datHyperPara['learningRate'],listOfMetrics)
        # if modelObj.__class__.__name__ == 'dict':
        #     return
        # model = modelObj.model
        tensor_board = self.startTensorBoard(tensorboardLogFolder)
        # try:
            # print ('Came here 1'*5 )
        model_graph = modelObj['modelObj']['model_graph']
        tf_session = modelObj['modelObj']['tf_session']
        with model_graph.as_default():
            with tf_session.as_default():
                
                if 'f1' in listOfMetrics:
                    listOfMetrics.remove('f1')
                    optiMi=self.setOptimizer(datHyperPara['optimizer'],datHyperPara['learningRate'])
                    modelV1.compile(optimizer=optiMi, loss=datHyperPara['loss'],metrics=listOfMetrics+[self.f1])
                    import tensorflow as tf
                    kerasUtilities.updateStatusOfTraining(self.statusFile,'Training Started')
                    with tf.device(gpuCPUSelect(selDev)):
                        modelV1.fit(x=trainDataX, y=trainDataY, epochs=datHyperPara['epoch'], callbacks=[tensor_board],\
                                    validation_data=(testDataX, testDataY), steps_per_epoch=stepsPerEpochT, validation_steps=stepsPerEpochV)
                else:
                    optiMi=self.setOptimizer(datHyperPara['optimizer'],datHyperPara['learningRate'])
                    modelV1.compile(optimizer=optiMi, loss=datHyperPara['loss'], metrics=listOfMetrics)
                    import tensorflow as tf
                    kerasUtilities.updateStatusOfTraining(self.statusFile,'Training Started')
                    with tf.device(gpuCPUSelect(selDev)):
                        modelV1.fit(x=trainDataX, y=trainDataY, epochs=datHyperPara['epoch'], callbacks=[tensor_board],\
                                    validation_data=(testDataX, testDataY), steps_per_epoch=stepsPerEpochT, validation_steps=stepsPerEpochV)

                        print ('9'*500)
        # except Exception as e:
        #     print ('Came here 2'*5 )
        #     data_details=self.upDateStatus()
        #     self.updateStatusWithError(data_details,'Training Failed','Error while fitting data to Keras Model >> '+ str(e),traceback.format_exc(),self.statusFile)

        kerasUtilities.updateStatusOfTraining(self.statusFile,'Training Completed')
        modelObj['modelObj']['recoModelObj'].model=modelV1
        modelObj['modelObj']['predictedClasses']=predictedClass
        return modelObj

    def trainSimpleDNNObjWithPrepro(self,modelObj,tensorboardLogFolder,dataObj):
        dataFolder=modelObj['Data']
        # modelToCompile=modelObj['modelObj']['recoModelObj']
        datHyperPara=modelObj['modelObj']['hyperparameters']
        listOfMetrics=datHyperPara['metrics']
        modelV1=modelObj['modelObj']['recoModelObj'].model
        print(">>>>>>>>>>>>>>SimpleDNN with Prepro")
        print('pathofdata>>>>>',dataFolder)
        predictedClasses=None
        targetColumnName = 'target'
        # df = dataObj
        print (modelObj['preprocessing']['codeObj'])
        print (dataObj.shape)

        scriptCode=modelObj['preprocessing']['codeObj']
        dfX,dfY=scriptCode(dataObj)
        print ('data prepared',dfX.shape)

        indevar=list(dfX.columns)
        # indevar.remove('target')
        targetCol = list(dfY.columns)[0]
        if datHyperPara['problemType']=='classification':
            lb=preprocessing.LabelBinarizer()
            y=lb.fit_transform(targetCol)
            predictedClass = list(targetCol.unique())
        else:
            y=dfY[targetCol]
            predictedClass=None
        ##### Split data into test and validation set for training#################################
        trainDataX,testDataX,trainDataY,testDataY=model_selection.train_test_split(dfX,dfY,
                                                        test_size=datHyperPara['testSize'])
        stepsPerEpochT=int(len(trainDataX)/datHyperPara['batchSize'])
        stepsPerEpochV=int(len(testDataX)/datHyperPara['batchSize'])
        kerasUtilities.updateStatusOfTraining(self.statusFile,'Data split in Train validation part')

        # modelObj = self.generateAndCompileModel(datHyperPara['lossType'],datHyperPara['optimizerName'],datHyperPara['learningRate'],listOfMetrics)
        # if modelObj.__class__.__name__ == 'dict':
        #     return
        # model = modelObj.model
        tensor_board = self.startTensorBoard(tensorboardLogFolder)
        # try:
            # print ('Came here 1'*5 )
        model_graph = modelObj['modelObj']['model_graph']
        tf_session = modelObj['modelObj']['tf_session']
        with model_graph.as_default():
            with tf_session.as_default():
                
                if 'f1' in listOfMetrics:
                    listOfMetrics.remove('f1')
                    optiMi=self.setOptimizer(datHyperPara['optimizer'],datHyperPara['learningRate'])
                    modelV1.compile(optimizer=optiMi, loss=datHyperPara['loss'],metrics=listOfMetrics+[self.f1])
                    import tensorflow as tf
                    kerasUtilities.updateStatusOfTraining(self.statusFile,'Training Started')
                    with tf.device(gpuCPUSelect(selDev)):
                        modelV1.fit(x=trainDataX, y=trainDataY, epochs=datHyperPara['epoch'], callbacks=[tensor_board],\
                                    validation_data=(testDataX, testDataY), steps_per_epoch=stepsPerEpochT, validation_steps=stepsPerEpochV)
                else:
                    optiMi=self.setOptimizer(datHyperPara['optimizer'],datHyperPara['learningRate'])
                    modelV1.compile(optimizer=optiMi, loss=datHyperPara['loss'], metrics=listOfMetrics)
                    import tensorflow as tf
                    kerasUtilities.updateStatusOfTraining(self.statusFile,'Training Started')
                    with tf.device(gpuCPUSelect(selDev)):
                        modelV1.fit(x=trainDataX, y=trainDataY, epochs=datHyperPara['epoch'], callbacks=[tensor_board],\
                                    validation_data=(testDataX, testDataY), steps_per_epoch=stepsPerEpochT, validation_steps=stepsPerEpochV)

                        print ('9'*500)
        # except Exception as e:
        #     print ('Came here 2'*5 )
        #     data_details=self.upDateStatus()
        #     self.updateStatusWithError(data_details,'Training Failed','Error while fitting data to Keras Model >> '+ str(e),traceback.format_exc(),self.statusFile)

        kerasUtilities.updateStatusOfTraining(self.statusFile,'Training Completed')
        modelObj['modelObj']['recoModelObj'].model=modelV1
        modelObj['modelObj']['predictedClasses']=predictedClass
        return modelObj

    def trainImageClassifierNN(self,modelObj,tensorboardLogFolder):
        print ('Enter image classifier')
        dataFolder=modelObj['Data']
        # modelToCompile=modelObj['modelObj']['recoModelObj']
        datHyperPara=modelObj['modelObj']['hyperparameters']
        print ('datHyperPara',datHyperPara)
        listOfMetrics=datHyperPara['metrics']
        modelV1=modelObj['modelObj']['recoModelObj'].model

        print ('Classification data folder at',dataFolder)
        try:
            self.trainFolder=dataFolder+'/'+'train/'
            self.validationFolder=dataFolder+'/'+'validation/'
            kerasUtilities.checkCreatePath(self.trainFolder)
            kerasUtilities.checkCreatePath(self.validationFolder)
        except Exception as e:
            data_details=self.upDateStatus()
            self.updateStatusWithError(data_details,'Training Failed','Unable to find train and validation folder >> '+ str(e),traceback.format_exc(),self.statusFile)
            return -1

        try:
            img_height, img_width=modelV1.input_shape[1:3]
        except Exception as e:
            data_details=self.upDateStatus()
            self.updateStatusWithError(data_details,'Training Failed','Model input_shape is invalid >> '+ str(e),traceback.format_exc(),self.statusFile)
            return -1

        try:
            tGen,vGen,nClass=self.kerasDataPrep(dataFolder,datHyperPara['batchSize'],img_height,img_width)
            stepsPerEpochT=tGen.n/tGen.batch_size
            stepsPerEpochV=vGen.n/vGen.batch_size
        except Exception as e:
            data_details=self.upDateStatus()
            self.updateStatusWithError(data_details,'Training Failed','Error while generating data for Keras >> '+ str(e),traceback.format_exc(),self.statusFile)
            return -1

        tensor_board = self.startTensorBoard(tensorboardLogFolder)

        try:
            print ('Came here 1'*5 )
            model_graph = modelObj['modelObj']['model_graph']
            tf_session = modelObj['modelObj']['tf_session']
            with model_graph.as_default():
                with tf_session.as_default():
                    
                    if 'f1' in listOfMetrics:
                        listOfMetrics.remove('f1')
                        optiMi=self.setOptimizer(datHyperPara['optimizer'],datHyperPara['learningRate'])
                        modelV1.compile(optimizer=optiMi, loss=datHyperPara['loss'], metrics=listOfMetrics+[self.f1])
                        import tensorflow as tf
                        kerasUtilities.updateStatusOfTraining(self.statusFile,'Training Started')
                        with tf.device(gpuCPUSelect(selDev)):
                            modelV1.fit_generator(tGen,steps_per_epoch=stepsPerEpochT,validation_steps=stepsPerEpochV,epochs=datHyperPara['epoch'],validation_data=vGen,callbacks=[tensor_board])
                    else:
                        optiMi=self.setOptimizer(datHyperPara['optimizer'],datHyperPara['learningRate'])
                        modelV1.compile(optimizer=optiMi, loss=datHyperPara['loss'], metrics=listOfMetrics)
                        import tensorflow as tf
                        kerasUtilities.updateStatusOfTraining(self.statusFile,'Training Started')
                        with tf.device(gpuCPUSelect(selDev)):
                            modelV1.fit_generator(tGen,steps_per_epoch=stepsPerEpochT,validation_steps=stepsPerEpochV,epochs=datHyperPara['epoch'],validation_data=vGen,callbacks=[tensor_board])
        except Exception as e:
            print ('Came here 2'*5 )
            data_details=self.upDateStatus()
            self.updateStatusWithError(data_details,'Training Failed','Error while compiling Model >> '+ str(e),traceback.format_exc(),self.statusFile)

        kerasUtilities.updateStatusOfTraining(self.statusFile,'Training Completed')

        predictedClass=list(tGen.class_indices.keys())
        modelObj['modelObj']['recoModelObj'].model=modelV1
        modelObj['modelObj']['predictedClasses']=predictedClass
        print (modelObj)
        return modelObj

    def getSKLMOdelObjtoFit(self,modelV1):
        from sklearn import ensemble,tree,linear_model
        # print (str(modelV1))
        if 'RandomForestRegressor' in str(modelV1):
            return  ensemble.RandomForestRegressor()
        elif 'RandomForestClassifier' in str(modelV1):
            return  ensemble.RandomForestClassifier()
        elif 'GradientBoostingClassifier' in str(modelV1):
            return  ensemble.GradientBoostingClassifier()
        elif 'GradientBoostingRegressor' in str(modelV1):
            return  ensemble.GradientBoostingRegressor()
        elif 'ExtraTreesClassifier' in str(modelV1):
            return  ensemble.ExtraTreesClassifier()
        elif 'ExtraTreesRegressor' in str(modelV1):
            return  ensemble.ExtraTreesRegressor()
        elif 'LinearRegression' in str(modelV1):
            return  linear_model.LinearRegression()
        elif 'LogisticRegression' in str(modelV1):
            return  linear_model.LogisticRegression()
        return modelV1
    def trainComplicatedDNNObj(self,modelObj,tensorboardLogFolder,scriptOutputPrepro):
        # print ('*'*500)
        # print ('Came to complicated part',modelObj)
        # print ('modelObj',modelObj.keys())

        if scriptOutputPrepro=='DATA':
            dataObj,tar=modelObj['preprocessing']()
            # print (dataObj.shape)
        else:
            pass

        predictedClass=None
        df = dataObj
        datHyperPara=modelObj['modelObj']['hyperparameters']
        
        if modelObj['modelObj']['modelArchType']=='SKLModel':
            # print('P'*200)
            modelV1=modelObj['modelObj']['recoModelObj']
            modelV1=self.getSKLMOdelObjtoFit(modelV1)
            modelV1.fit(df,tar)
            modelObj['modelObj']['recoModelObj']=modelV1

        else:
            listOfMetrics=datHyperPara['metrics']
            targetCol = tar
            # print(">>>>>>>>>>>>>>SimpleDNN")
            modelV1=modelObj['modelObj']['recoModelObj'].model
            if datHyperPara['problemType']=='classification':
                lb=preprocessing.LabelBinarizer()
                y=lb.fit_transform(targetCol)
                predictedClass = list(targetCol.unique())
            else:
                y=tar
                predictedClass=None
            # print(df.shape,y.shape,datHyperPara['testSize'])
            trainDataX,testDataX,trainDataY,testDataY=model_selection.train_test_split(df,tar,test_size=datHyperPara['testSize'])
            stepsPerEpochT=int(len(trainDataX)/datHyperPara['batchSize'])
            stepsPerEpochV=int(len(testDataX)/datHyperPara['batchSize'])
            kerasUtilities.updateStatusOfTraining(self.statusFile,'Data split in Train validation part')

            # modelObj = self.generateAndCompileModel(datHyperPara['lossType'],datHyperPara['optimizerName'],datHyperPara['learningRate'],listOfMetrics)
            # if modelObj.__class__.__name__ == 'dict':
            #     return
            # model = modelObj.model
            tensor_board = self.startTensorBoard(tensorboardLogFolder)
            try:
                # print ('Came here 1'*5 )
                model_graph = modelObj['modelObj']['model_graph']
                tf_session = modelObj['modelObj']['tf_session']
                with model_graph.as_default():
                    with tf_session.as_default():
                        
                        if 'f1' in listOfMetrics:
                            listOfMetrics.remove('f1')
                            optiMi=self.setOptimizer(datHyperPara['optimizer'],datHyperPara['learningRate'])
                            modelV1.compile(optimizer=optiMi, loss=datHyperPara['lossType'],metrics=listOfMetrics+[self.f1])
                            import tensorflow as tf
                            kerasUtilities.updateStatusOfTraining(self.statusFile,'Training Started')
                            with tf.device(gpuCPUSelect(selDev)):
                                modelV1.fit(x=trainDataX, y=trainDataY, epochs=datHyperPara['epoch'], callbacks=[tensor_board],\
                                            validation_data=(testDataX, testDataY), steps_per_epoch=stepsPerEpochT, validation_steps=stepsPerEpochV)
                        else:
                            optiMi=self.setOptimizer(datHyperPara['optimizer'],datHyperPara['learningRate'])
                            modelV1.compile(optimizer=optiMi, loss=datHyperPara['lossType'], metrics=listOfMetrics)
                            import tensorflow as tf
                            kerasUtilities.updateStatusOfTraining(self.statusFile,'Training Started')
                            with tf.device(gpuCPUSelect(selDev)):
                                modelV1.fit(x=trainDataX, y=trainDataY, epochs=datHyperPara['epoch'], callbacks=[tensor_board],\
                                                validation_data=(testDataX, testDataY), steps_per_epoch=stepsPerEpochT, validation_steps=stepsPerEpochV)
                            # print ('9'*500)
                            modelObj['modelObj']['recoModelObj'].model=modelV1
            except Exception as e:
                print ('Came here 2'*5 )
                data_details=self.upDateStatus()
                self.updateStatusWithError(data_details,'Training Failed','Error while fitting data to Keras Model >> '+ str(e),traceback.format_exc(),self.statusFile)
        
        kerasUtilities.updateStatusOfTraining(self.statusFile,'Training 1st part completed')
        
        return modelObj

    def restructureModelInforForExportDict(self,tempDict):
        print ('tempDict',tempDict)

        listOfModelNames=set([k for j in tempDict for k in tempDict[j]])
        toExportDict={}
        for objDet in listOfModelNames:
            toExportDict[objDet]={'hyperparameters':None,'data':None,
                                'preProcessingScript':{'scripts':[], 'scriptpurpose':[],'scriptOutput':[],'scriptPath':[]},
                                'modelObj':None,'pipelineObj':None,'featuresUsed':None,'targetName':None,
                                'postProcessingScript':{'scripts':[], 'scriptpurpose':[],'scriptOutput':[],'scriptPath':[]},
                                'taskType': None,'modelPath':None,'predictedClasses':None}
        for modObjeCom in tempDict:
            # print ('>>>>>>>>modObj >>>>>> ',modObjeCom)
            if modObjeCom == 'train':
                for echMod in toExportDict:
                    if echMod in tempDict[modObjeCom]:
                        # print ('>>>>>',echMod)
                        # print ('8'*100)
                        # print ('tempDict.keys()',tempDict.keys())
                        # print (tempDict[modObjeCom][echMod]['scriptPath'])
                        if tempDict[modObjeCom][echMod]['modelObj']['modelArchType']=='NNModel':
                        #                     print (tempDict[modObjeCom][echMod]['modelObj'])
                            toExportDict[echMod]['modelObj']=tempDict[modObjeCom][echMod]['modelObj']['recoModelObj'].model
                            toExportDict[echMod]['model_graph']=tempDict[modObjeCom][echMod]['modelObj']['model_graph']
                            toExportDict[echMod]['tf_session']=tempDict[modObjeCom][echMod]['modelObj']['tf_session']
                        else:
                            toExportDict[echMod]['modelObj']=tempDict[modObjeCom][echMod]['modelObj']['recoModelObj']
                        if 'preprocessing' in tempDict[modObjeCom][echMod]:
                            toExportDict[echMod]['preProcessingScript']['scripts'].append(tempDict[modObjeCom][echMod]['preprocessing']['codeCont'])
                            toExportDict[echMod]['preProcessingScript']['scriptpurpose'].append(modObjeCom)
                            toExportDict[echMod]['preProcessingScript']['scriptOutput'].append(tempDict[modObjeCom][echMod]['preprocessing']['scriptOutput'])
                            toExportDict[echMod]['preProcessingScript']['scriptPath'].append(tempDict[modObjeCom][echMod]['preprocessing']['scriptPath'])
                        if 'postprocessing' in tempDict[modObjeCom][echMod]:
                            toExportDict[echMod]['postProcessingScript']['scripts'].append(tempDict[modObjeCom][echMod]['postprocessing']['codeCont'])
                            toExportDict[echMod]['postProcessingScript']['scriptpurpose'].append(modObjeCom)
                            toExportDict[echMod]['postProcessingScript']['scriptOutput'].append(tempDict[modObjeCom][echMod]['postprocessing']['scriptOutput'])
                            toExportDict[echMod]['postProcessingScript']['scriptPath'].append(tempDict[modObjeCom][echMod]['postprocessing']['scriptPath'])
                        toExportDict[echMod]['taskType']=modObjeCom
                        toExportDict[echMod]['featuresUsed']=tempDict[modObjeCom][echMod]['modelObj']['listOFColumns']
                        toExportDict[echMod]['targetName']=tempDict[modObjeCom][echMod]['modelObj']['targetCol']
                        toExportDict[echMod]['hyperparameters']=tempDict[modObjeCom][echMod]['modelObj']['hyperparameters']
                        toExportDict[echMod]['modelPath']=tempDict[modObjeCom][echMod]['modelObj']['modelPath']
                        toExportDict[echMod]['predictedClasses']=tempDict[modObjeCom][echMod]['modelObj']['predictedClasses']

                        if 'Data' in tempDict[modObjeCom][echMod]:
                            toExportDict[echMod]['data']=tempDict[modObjeCom][echMod]['Data']
            if modObjeCom == 'score':
                for echMod in toExportDict:
                    if echMod in tempDict[modObjeCom]:
                        # print ('>>>>',echMod)
                        if tempDict[modObjeCom][echMod]['modelObj']['modelArchType']=='NNModel':
        #                     print (tempDict[modObjeCom][echMod]['modelObj'])
                            toExportDict[echMod]['modelObj']=tempDict[modObjeCom][echMod]['modelObj']['recoModelObj'].model
                            toExportDict[echMod]['model_graph']=tempDict[modObjeCom][echMod]['modelObj']['model_graph']
                            toExportDict[echMod]['tf_session']=tempDict[modObjeCom][echMod]['modelObj']['tf_session']
                        else:
                            toExportDict[echMod]['modelObj']=tempDict[modObjeCom][echMod]['modelObj']['recoModelObj']

                        if 'preprocessing' in tempDict[modObjeCom][echMod]:
                            toExportDict[echMod]['preProcessingScript']['scripts'].append(tempDict[modObjeCom][echMod]['preprocessing']['codeCont'])
                            toExportDict[echMod]['preProcessingScript']['scriptpurpose'].append(modObjeCom)
                            toExportDict[echMod]['preProcessingScript']['scriptOutput'].append(tempDict[modObjeCom][echMod]['preprocessing']['scriptOutput'])
                            toExportDict[echMod]['preProcessingScript']['scriptPath'].append(tempDict[modObjeCom][echMod]['preprocessing']['scriptPath'])
                        if 'postprocessing' in tempDict[modObjeCom][echMod]:
                            toExportDict[echMod]['postProcessingScript']['scripts'].append(tempDict[modObjeCom][echMod]['postprocessing']['codeCont'])
                            toExportDict[echMod]['postProcessingScript']['scriptpurpose'].append(modObjeCom)
                            toExportDict[echMod]['postProcessingScript']['scriptOutput'].append(tempDict[modObjeCom][echMod]['postprocessing']['scriptOutput'])
                            toExportDict[echMod]['postProcessingScript']['scriptPath'].append(tempDict[modObjeCom][echMod]['postprocessing']['scriptPath'])
                        toExportDict[echMod]['taskType']=modObjeCom
                        toExportDict[echMod]['featuresUsed']=tempDict[modObjeCom][echMod]['modelObj']['listOFColumns']
                        toExportDict[echMod]['targetName']=tempDict[modObjeCom][echMod]['modelObj']['targetCol']
                        toExportDict[echMod]['hyperparameters']=tempDict[modObjeCom][echMod]['modelObj']['hyperparameters']
                        toExportDict[echMod]['modelPath']=tempDict[modObjeCom][echMod]['modelObj']['modelPath']
                        toExportDict[echMod]['predictedClasses']=tempDict[modObjeCom][echMod]['modelObj']['predictedClasses']
                        if 'Data' in tempDict[modObjeCom][echMod]:
                            toExportDict[echMod]['data']=tempDict[modObjeCom][echMod]['Data']
    
        for modNa in listOfModelNames:
            if ('train' in  list(tempDict.keys())) & ('score' in  list(tempDict.keys())):
                if (modNa in tempDict['train']) & (modNa in tempDict['score']):
                    toExportDict[modNa]['taskType']='trainAndscore'
                    # print (tempDict['train'][modNa].keys())
                    # print (tempDict['score'][modNa]['preprocessing_code'][0])
                    # print ("tempDict['train'][modNa]",tempDict['train'][modNa],tempDict['score'][modNa])
                    print ('p'*100)
                    if ('scriptOutput' in tempDict['train'][modNa]) & ('scriptOutput' in tempDict['score'][modNa]):
                        if (tempDict['train'][modNa]['scriptOutput']==tempDict['score'][modNa]['scriptOutput']):
                            print ('Came here >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',toExportDict[modNa])
                            if  toExportDict[modNa]['preProcessingScript']['scripts'] != None:
                                toExportDict[modNa]['preProcessingScript']['scriptOutput']=tempDict['train'][modNa]['scriptOutput']
                                toExportDict[modNa]['preProcessingScript']['scriptpurpose']=['trainAndscore']
                                # print( '>>>>>>>>',tempDict['score'][modNa]['preprocessing_code'])
                                toExportDict[modNa]['preProcessingScript']['scripts']=[tempDict['score'][modNa]['preprocessing']['codeCont']]
                                toExportDict[modNa]['preProcessingScript']['scriptPath']=[tempDict['score'][modNa]['scriptPath']]
                            elif toExportDict[modNa]['postProcessingScript']['scripts'] != None:
                                toExportDict[modNa]['postProcessingScript']['scriptOutput']=tempDict['train'][modNa]['scriptOutput']
                                toExportDict[modNa]['postProcessingScript']['scriptpurpose']=['trainAndscore']
                                # print( '>>>>>>>>',tempDict['score'][modNa]['preprocessing_code'])
                                toExportDict[modNa]['postProcessingScript']['scripts']=[tempDict['score'][modNa]['postprocessing']['codeCont']]
                                toExportDict[modNa]['postProcessingScript']['scriptPath']=[tempDict['score'][modNa]['scriptPath']]

            elif ('train' not in  list(tempDict.keys())) & ('score' in  list(tempDict.keys())):
                print ('no train found')
                if modNa in tempDict['score']:
                    toExportDict[modNa]['taskType']='score'
                    # print (tempDict['train'][modNa].keys())
                    # print (tempDict['score'][modNa]['preprocessing_code'][0])
                    # print ("tempDict['train'][modNa]",tempDict['train'][modNa],tempDict['score'][modNa])
                    print ('p'*100)
                    if 'scriptOutput' in tempDict['score'][modNa]:
                        print ('Came here >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',toExportDict[modNa])
                        if  toExportDict[modNa]['preProcessingScript']['scripts'] != None:
                            toExportDict[modNa]['preProcessingScript']['scriptOutput']=tempDict['score'][modNa]['scriptOutput']
                            toExportDict[modNa]['preProcessingScript']['scriptpurpose']=['score']
                            # print( '>>>>>>>>',tempDict['score'][modNa]['preprocessing_code'])
                            toExportDict[modNa]['preProcessingScript']['scripts']=[tempDict['score'][modNa]['preprocessing']['codeCont']]
                            toExportDict[modNa]['preProcessingScript']['scriptPath']=[tempDict['score'][modNa]['scriptPath']]
                        elif toExportDict[modNa]['postProcessingScript']['scripts'] != None:
                            toExportDict[modNa]['postProcessingScript']['scriptOutput']=tempDict['score'][modNa]['scriptOutput']
                            toExportDict[modNa]['postProcessingScript']['scriptpurpose']=['score']
                            # print( '>>>>>>>>',tempDict['score'][modNa]['preprocessing_code'])
                            toExportDict[modNa]['postProcessingScript']['scripts']=[tempDict['score'][modNa]['postprocessing']['codeCont']]
                            toExportDict[modNa]['postProcessingScript']['scriptPath']=[tempDict['score'][modNa]['scriptPath']]

            elif ('train'  in  list(tempDict.keys())) & ('score' not in  list(tempDict.keys())):
                print ('no score found')
                if modNa in tempDict['train']:
                    toExportDict[modNa]['taskType']='train'
                    # print (tempDict['train'][modNa].keys())
                    # print (tempDict['score'][modNa]['preprocessing_code'][0])
                    # print ("tempDict['train'][modNa]",tempDict['train'][modNa],tempDict['score'][modNa])
                    print ('p'*100)
                    if 'scriptOutput' in tempDict['train'][modNa]:
                        print ('Came here >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',toExportDict[modNa])
                        if  toExportDict[modNa]['preProcessingScript']['scripts'] != None:
                            toExportDict[modNa]['preProcessingScript']['scriptOutput']=tempDict['train'][modNa]['scriptOutput']
                            toExportDict[modNa]['preProcessingScript']['scriptpurpose']=['train']
                            # print( '>>>>>>>>',tempDict['score'][modNa]['preprocessing_code'])
                            toExportDict[modNa]['preProcessingScript']['scripts']=[tempDict['train'][modNa]['preprocessing']['codeCont']]
                            toExportDict[modNa]['preProcessingScript']['scriptPath']=[tempDict['train'][modNa]['scriptPath']]
                        elif toExportDict[modNa]['postProcessingScript']['scripts'] != None:
                            toExportDict[modNa]['postProcessingScript']['scriptOutput']=tempDict['train'][modNa]['scriptOutput']
                            toExportDict[modNa]['postProcessingScript']['scriptpurpose']=['train']
                            # print( '>>>>>>>>',tempDict['score'][modNa]['preprocessing_code'])
                            toExportDict[modNa]['postProcessingScript']['scripts']=[tempDict['train'][modNa]['postprocessing']['codeCont']]
                            toExportDict[modNa]['postProcessingScript']['scriptPath']=[tempDict['train'][modNa]['scriptPath']]
                    # elif  (tempDict['train'][modNa]['scriptOutput']=='NONE') & (tempDict['score'][modNa]['scriptOutput'] == 'NONE'):
                    #     print ('Came here >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',toExportDict[modNa])
                    #     if  toExportDict[modNa]['preProcessingScript']['scripts'] != None:
                    #         toExportDict[modNa]['preProcessingScript']['scriptOutput']=['NONE']
                    #         toExportDict[modNa]['preProcessingScript']['scriptpurpose']=['trainAndscore']
                    #         # print( '>>>>>>>>',tempDict['score'][modNa]['preprocessing_code'])
                    #         toExportDict[modNa]['preProcessingScript']['scripts']=[tempDict['score'][modNa]['preprocessing']['codeCont']]
                    #         toExportDict[modNa]['preProcessingScript']['scriptPath']=[tempDict['score'][modNa]['scriptPath']]
                    #     elif toExportDict[modNa]['postProcessingScript']['scripts'] != None:
                    #         toExportDict[modNa]['postProcessingScript']['scriptOutput']=['NONE']
                    #         toExportDict[modNa]['postProcessingScript']['scriptpurpose']=['trainAndscore']
                    #         # print( '>>>>>>>>',tempDict['score'][modNa]['preprocessing_code'])
                    #         toExportDict[modNa]['postProcessingScript']['scripts']=[tempDict['score'][modNa]['postprocessing']['codeCont']]
                    #         toExportDict[modNa]['postProcessingScript']['scriptPath']=[tempDict['score'][modNa]['scriptPath']]
            # print ("toExportDict[modNa]['preProcessingScript']['script']",toExportDict[modNa]['preProcessingScript']['script'])
            if ('train' in  list(tempDict.keys())) & ('score' in  list(tempDict.keys())):
                if ((modNa in tempDict['train'] )== False) & (modNa in tempDict['score']):
                    toExportDict[modNa]['taskType']=['score']

        toExportDict2=toExportDict.copy()
        if ('train' in  list(tempDict.keys())) & ('score' in  list(tempDict.keys())):
            for modT in toExportDict:
                print (modT, '>>>>>>>>>>>>>>>>>>>>>>>>>.')
                if 'preProcessingScript' in toExportDict2[modT]:
                    if len(set(toExportDict2[modT]['preProcessingScript']['scriptPath']))==1:
                        print ('came here agaa')
                        toExportDict2[modT]['preProcessingScript']['scriptpurpose']=['trainAndscore']
                        toExportDict2[modT]['preProcessingScript']['scriptPath']=[toExportDict[modT]['preProcessingScript']['scriptPath'][0]]
                        toExportDict2[modT]['preProcessingScript']['scripts']=[toExportDict[modT]['preProcessingScript']['scripts'][0]]
                        toExportDict2[modT]['preProcessingScript']['scriptOutput']=[toExportDict[modT]['preProcessingScript']['scriptOutput'][0]]
                if 'postProcessingScript' in toExportDict2[modT]:
                    if len(set(toExportDict2[modT]['postProcessingScript']['scriptPath']))==1:
                        toExportDict2[modT]['postProcessingScript']['scriptpurpose']=['trainAndscore']
                        toExportDict2[modT]['postProcessingScript']['scriptPath']=[toExportDict[modT]['postProcessingScript']['scriptPath'][0]]
                        toExportDict2[modT]['postProcessingScript']['scripts']=[toExportDict[modT]['postProcessingScript']['scripts'][0]]
                        toExportDict2[modT]['postProcessingScript']['scriptOutput']=[toExportDict[modT]['postProcessingScript']['scriptOutput'][0]]

        print ('compleged to exportdict2  ',toExportDict2)
        tempTa2=list(toExportDict2.keys())
        tempTa2.sort()
        toExportReOrdered={}
        for taTTemp2 in tempTa2:
            toExportReOrdered[taTTemp2]=toExportDict2[taTTemp2]

        toExportDict2=toExportReOrdered.copy()

        return toExportDict2
    
    def trainModel(self,idforData,pmmlFile,tensorboardLogFolder,hyperParaUser,newNameFile):
        global PMMLMODELSTORAGE
        pmmlFileObj=pathlib.Path(pmmlFile)
        pmmlFileForKey=pmmlFileObj.name.replace(pmmlFileObj.suffix,'')
        saveStatus=self.logFolder+idforData+'/'
        self.statusFile=saveStatus+'status.txt'
        global PMMLMODELSTORAGE

        try:
            NewModelOperations().loadExecutionModel(pmmlFile)
        except Exception as e:
            print ('Came here got stuck')
            data_details=self.upDateStatus()
            self.updateStatusWithError(data_details,'Training Failed',"Couldn't load the PMML >> "+ str(e),traceback.format_exc(),self.statusFile)
            return -1
        # self.statusFile=statusFile
        modelInformation =PMMLMODELSTORAGE[pmmlFileForKey]
        
        modelObjsTrain=list(modelInformation['train'].keys())
        print('model object loaded')
        # tempDict[taskT][mO]['modelObj']['hyperparameters']

        if len(modelObjsTrain)==0:
            data_details=self.upDateStatus()
            self.updateStatusWithError(data_details,'Training Failed',"Error while selecting model to Train >> "+ str(e),traceback.format_exc(),self.statusFile)
            return -1
        elif len(modelObjsTrain) ==2:
            data_details=self.upDateStatus()
            self.updateStatusWithError(data_details,'Training Failed',"Add support for training multiple model >> "+ str(e),traceback.format_exc(),self.statusFile)
            return -1
        elif len(modelObjsTrain) ==1:
            # print ('>>>>>>>>>>>>>>>                 ',self.statusFile)
            print('Came in model 1')
            modeScope=modelInformation['train'][modelObjsTrain[0]]
            if hyperParaUser['epoch'] != None:
                # print ('Print to update hyperparp',hyperParaUser['epoch'])
                modeScope['modelObj']['hyperparameters']=hyperParaUser
            # print ('modeScope>>>>>>>>>>> ',modeScope)
            kerasUtilities.updateStatusofProcess(self.statusFile,'Training Model Loaded')

            modeScope=self.trainModelObjectDict(modeScope,idforData,tensorboardLogFolder)
            modelInformation['train'][modelObjsTrain[0]]=modeScope

        if modeScope == -1:
            return -1

        # print ('trainModelObjectDict modeScope  >>>>>>>>> ',modeScope)
        
        tempDict=modelInformation

        

        # print ('8'*100)
        # print (toExportDict['model1'].keys(),listOfModelNames)
        # print ('8'*100)

        # print('*'*100)

        # print (toExportDict)
        # print('*'*100)
        toExportDict=self.restructureModelInforForExportDict(tempDict)
        fN=pathlib.Path(pmmlFile).name
        orgfName='../ZMOD/Models/'+fN#+'.pmml'
        fN=fN.replace('.pmml','')
        if newNameFile==None:
            copyOrgFName='../ZMOD/Models/'+self.increName(fN)+'.pmml'
            kerasUtilities.updateStatusOfTraining(self.statusFile,'Model Saved in different Version')
        else:
            copyOrgFName=newNameFile
            kerasUtilities.updateStatusOfTraining(self.statusFile,'Model Saved')
        import shutil
        from nyokaBase.skl.skl_to_pmml import model_to_pmml
        try:
            shutil.copy2(orgfName,copyOrgFName)
        except:
            pass
        model_to_pmml(toExportDict, PMMLFileName=copyOrgFName)
        NewModelOperations().loadExecutionModel(orgfName)
        # data_details['status']='Model Saved in different Version'
        
        data_details=self.upDateStatus()

        return JsonResponse(data_details)