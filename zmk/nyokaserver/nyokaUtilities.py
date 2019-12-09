# nyokaUtilities.py
import numpy as np
from random import choice
from string import ascii_uppercase
import copy,json
import ast,pathlib
import traceback
from nyokaBase import PMML43Ext as ny
global MEMORY_DICT_ARCHITECTURE,MEMORY_OF_LAYERS

settingFilePath='./settingFiles/'
savedModels='./SavedModels/'
MEMORY_OF_LAYERS={}
from trainModel.mergeTrainingV2 import PMMLMODELSTORAGE
layerDetail=open(settingFilePath+'listOflayers.json','r')
MEMORY_OF_LAYERS=json.loads(layerDetail.read())
#########################################All functions is to write PMML###############################
class NyokaUtilities:

    def convertToStandardJson(self,pp):
        tempData={}
        tempData['connectionLayerId']=pp['connectionLayerId']
        tempData['itemType']=pp['itemType']
        tempData['layerType']=pp['layerType']
        tempData['connectionLayerId']=pp['connectionLayerId']
        tempData['layerId']=pp['layerId']
        tempData['name']=pp['name']
        tempData['properties']={}
        for j in pp['properties']:
            tempData['properties'][j['id']]=j['value']
        return tempData


    def calculateOutputSize(self,N,S,F,P=None):
        if P==None:
            P=0
        val=((N-F+(2*P))/S)+1
        return int(val)

    def calculatePadding(self,N,O,S,F):
        val=abs((N-(O*S)-F+S)/2)
        return int(val)

    def outputForDepthWiseConv2D(self,tempData):
        try:
            tempData=self.convertToStandardJson(tempData)
            wid,heig,channel=tempData['properties']['inputDimension']
            widFil,heigFil=tempData['properties']['kernel']
            widStri,heigStri=tempData['properties']['stride']
            if tempData['properties']['paddingType']=='valid':
                padding=0
                widthOutput=self.calculateOutputSize(wid,widStri,widFil,padding)
                heightOutput=self.calculateOutputSize(heig,heigStri,heigFil,padding)
            elif tempData['properties']['paddingType']=='same':
                padding=self.calculatePadding(wid,wid,widStri,widFil)
                widthOutput=self.calculateOutputSize(wid,widStri,widFil,padding)
                heightOutput=self.calculateOutputSize(heig,heigStri,heigFil,padding)
            out_filter=channel*tempData['properties']['depthMultiplier']
            return((widthOutput,heightOutput,out_filter),'success','success')
        except Exception as e:
            errorMessage='Error while calculating output >> '+ str(e)
            errorTraceback=str(traceback.format_exc())
            wid,heig,out_filter=(0,0,0)
            return((wid,heig,out_filter),errorMessage,errorTraceback)


    def outputForConv2D(self,tempData2):
        try:
            tempData2=self.convertToStandardJson(tempData2)
            wid,heig,channel=tempData2['properties']['inputDimension']
            widFil,heigFil=tempData2['properties']['kernel']
            widStri,heigStri=tempData2['properties']['stride']
            try:
                featureMaps=tempData2['properties']['featureMaps']
            except:
                featureMaps=None
            if tempData2['properties']['paddingType']=='valid':
                padding=0
                widthOutput=self.calculateOutputSize(wid,widStri,widFil,padding)
                heightOutput=self.calculateOutputSize(heig,heigStri,heigFil,padding)
            elif tempData2['properties']['paddingType']=='same':
                padding=self.calculatePadding(wid,heig,widStri,widFil)
                widthOutput=self.calculateOutputSize(wid,widStri,widFil,padding)
                heightOutput=self.calculateOutputSize(heig,heigStri,heigFil,padding)
            if featureMaps==None:
                return ((widthOutput,heightOutput,channel), 'success','success')
            else:
                return ((widthOutput,heightOutput,featureMaps), 'success','success')
        except Exception as e:
            # print('No input came')
            errorMessage='Error while calculating output >> '+ str(e)
            errorTraceback=str(traceback.format_exc())
            widthOutput,heightOutput,featureMaps=0,0,0
            return ((widthOutput,heightOutput,featureMaps), errorMessage,errorTraceback)


    def outputForMaxPooling1D(self,tempData):
        try:
            tempData=self.convertToStandardJson(tempData)
            N = tempData['properties']['inputDimension'][-2]
            S = tempData['properties']['stride']
            F = tempData['properties']['poolSize']
            return ((self.calculateOutputSize(N, S, F), tempData['properties']['inputDimension'][-1]), 'success','success')
        except Exception as e:
            # print('No input came')
            errorMessage='Error while calculating output >> '+ str(e)
            errorTraceback=str(traceback.format_exc())
            return ((0,0), errorMessage,errorTraceback)


    def outputForMaxPooling2D(self,tempData):
        # print('>>>>>> outputForMaxpooling1D', tempData)
        try:
            tempData=self.convertToStandardJson(tempData)
            N1, N2 = tempData['properties']['inputDimension'][:-1]
            if len(tempData['properties']['stride']) == 1:
                S1 = tempData['properties']['stride'][0]
            else:
                S1, S2 = tempData['properties']['stride']
            if len(tempData['properties']['poolSize']) == 1:
                F1 = tempData['properties']['poolSize'][0]
            else:
                F1, F2 = tempData['properties']['poolSize']
            return ((self.calculateOutputSize(N1, S1, F1), self.calculateOutputSize(N2, S1, F1), \
                tempData['properties']['inputDimension'][-1]), 'success','success')
        except Exception as e:
            # print('No input came')
            errorMessage='Error while calculating output >> '+ str(e)
            errorTraceback=str(traceback.format_exc())
            return ((0,0,0),errorMessage,errorTraceback)


    def outputForInput(self,inputDimension):
        # print ('$$$$$$$$$$$$$outputForInput >>>>>> ',inputDimension)
        inputDimension=self.convertToStandardJson(inputDimension)
        if len(inputDimension['properties']['inputDimension'])==1:
            return ((inputDimension['properties']['inputDimension'][0],1),'success','success')
        else:
            return ((inputDimension['properties']['inputDimension']),'success','success')


    def outputForFlatten(self,tempData4):
        try:
            tempData4=self.convertToStandardJson(tempData4)
            tomul=tempData4['properties']['inputDimension']
            val=int(np.prod(tomul))
            return ((val,1), 'success','success')
        except Exception as e:
            # print('No input came')
            errorMessage='Error while calculating output >> '+ str(e)
            errorTraceback=str(traceback.format_exc())
            return ((0,0), errorMessage,errorTraceback)


    def outputFor1DPadding(self,tempData):
        try:
            tempData=self.convertToStandardJson(tempData)
            width,height=tempData['properties']['inputDimension']
            if len(tempData['properties']['paddingDims']) == 1:
                left_pad = right_pad = tempData['properties']['paddingDims'][0]
            else:
                left_pad, right_pad=tempData['properties']['paddingDims']
            width=width+left_pad+right_pad
            return ((width, height),'success','success')
        except Exception as e:
            # print('No input came')
            errorMessage='Error while calculating output >> '+ str(e)
            errorTraceback=str(traceback.format_exc())
            return ((0,0), errorMessage,errorTraceback)


    def outputFor2DPadding(self,tempData6):
        try:
            tempData6=self.convertToStandardJson(tempData6)
            width,height,channel=tempData6['properties']['inputDimension']
            if len(tempData6['properties']['paddingDims']) == 1:
                top_pad = bottom_pad = left_pad = right_pad = tempData6['properties']['paddingDims'][0]
            elif len(tempData6['properties']['paddingDims']) == 2:
                top_pad, left_pad=tempData6['properties']['paddingDims']
                bottom_pad, right_pad = top_pad, left_pad
            else:
                top_pad, bottom_pad,left_pad, right_pad=tempData6['properties']['paddingDims']
            width=width+left_pad+right_pad
            height=height+top_pad+bottom_pad
            return ((width,height,channel), 'success','success')
        except Exception as e:
            # print('No input came')
            errorMessage='Error while calculating output >> '+ str(e)
            errorTraceback=str(traceback.format_exc())
            return ((0,0,0), errorMessage,errorTraceback)


    def outputForDense(self,tempdata7):
        try:
            tempdata7=self.convertToStandardJson(tempdata7)
            tomul=tempdata7['properties']['units']
            if tomul.__class__.__name__ != 'int':
                raise Exception("Expected integer value for units, got string/empty value",tomul)
            return ((tomul,1),'success','success')
        except Exception as e :
            errorMessage='Error while calculating output >> '+ str(e)
            errorTraceback=str(traceback.format_exc())
            # print('No input came>>', errorMessage)
            tomul=0
            return ((tomul,1),errorMessage,errorTraceback)


    def outputForGlobalAverage2D(self,tempdata7):
        try:
            tempdata7=self.convertToStandardJson(tempdata7)
            tomul=tempdata7['properties']['inputDimension'][2]
            return ((1,1,tomul), 'success','success')
        except Exception as e :
            errorMessage='Error while calculating output >> '+ str(e)
            errorTraceback=str(traceback.format_exc())
            # print('No input came')
            tomul=0
            return ((0,0,0),errorMessage,errorTraceback) 

    def outputForReshape(self,tempdata7):
        try:
            # print('>>>>>>>>Reshape', tempdata7)
            tempdata7=self.convertToStandardJson(tempdata7)
            return (tempdata7['properties']['reshapeTarget'],'success','success')
        except Exception as e :
            errorMessage='Error while calculating output >> '+ str(e)
            errorTraceback=str(traceback.format_exc())
            # print('No input came')
            return ((0,0,0),errorMessage,errorTraceback)


    def selectArchitecture(self,checkTemplateID):
        if checkTemplateID=='mobilenetArch':
            pmmlObj = ny.parse(open(settingFilePath+'MobilenetArch.pmml','r'), silence=True)
            templateArch=self.pmmlToJson(settingFilePath+'MobilenetArch.pmml')
        elif checkTemplateID=='vgg16Arch':
            pmmlObj = ny.parse(open(settingFilePath+'vGG16Arch.pmml','r'), silence=True)
            templateArch=self.pmmlToJson(settingFilePath+'vGG16Arch.pmml')
        elif checkTemplateID=='vgg19Arch':
            pmmlObj = ny.parse(open(settingFilePath+'vGG19Arch.pmml','r'), silence=True)
            templateArch=self.pmmlToJson(settingFilePath+'vGG19Arch.pmml')
        return templateArch,pmmlObj


    def addLayertoJson(self,tempData):
        if tempData['layerType'] in ['Input']:
            valRet,messageInfo,traceBack=self.outputForInput(tempData)
            [j for j in tempData['properties'] if j['id']=='outputDimension' ][0]['value']=valRet
            [j for j in tempData['properties'] if j['id']=='inputDimension' ][0]['value']=valRet
        elif tempData['layerType'] in ['Reshape']:
            valRet,messageInfo,traceBack=self.outputForReshape(tempData)
            [j for j in tempData['properties'] if j['id']=='outputDimension' ][0]['value']=valRet
        elif tempData['layerType'] in ['Activation','Dropout']:
            # print ('$$$$$$$$$$$$$  Activation',tempData)
            valRet,messageInfo,traceBack=self.outputForInput(tempData)
            [j for j in tempData['properties'] if j['id']=='outputDimension' ][0]['value']=valRet
        elif tempData['layerType'] in ['BatchNormalization']:
            valRet,messageInfo,traceBack=self.outputForInput(tempData)
            [j for j in tempData['properties'] if j['id']=='outputDimension' ][0]['value']=valRet
        elif tempData['layerType'] in ['Conv2D']:
            valRet,messageInfo,traceBack=self.outputForConv2D(tempData)
            [j for j in tempData['properties'] if j['id']=='outputDimension' ][0]['value']=valRet
        elif tempData['layerType'] in ['DepthwiseConv2D']:
            valRet,messageInfo,traceBack=self.outputForDepthWiseConv2D(tempData)
            [j for j in tempData['properties'] if j['id']=='outputDimension' ][0]['value']=valRet
        elif tempData['layerType'] in ['Flatten']:
            valRet,messageInfo,traceBack=self.outputForFlatten(tempData)
            [j for j in tempData['properties'] if j['id']=='outputDimension' ][0]['value']=valRet
        elif tempData['layerType'] in ['ZeroPadding2D']:
            valRet,messageInfo,traceBack=self.outputFor2DPadding(tempData)
            [j for j in tempData['properties'] if j['id']=='outputDimension' ][0]['value']=valRet
        elif tempData['layerType'] in ['ZeroPadding1D']:
            valRet,messageInfo,traceBack=self.outputFor1DPadding(tempData)
            [j for j in tempData['properties'] if j['id']=='outputDimension' ][0]['value']=valRet
        elif tempData['layerType'] in ['Dense']:
            valRet,messageInfo,traceBack=self.outputForDense(tempData)
            [j for j in tempData['properties'] if j['id']=='outputDimension' ][0]['value']=valRet
        elif tempData['layerType'] in ['GlobalAveragePooling2D']:
            valRet,messageInfo,traceBack=self.outputForGlobalAverage2D(tempData)
            [j for j in tempData['properties'] if j['id']=='outputDimension' ][0]['value']=valRet
        elif tempData['layerType'] in ['MaxPooling2D', 'AveragePooling2D']:
            valRet,messageInfo,traceBack=self.outputForMaxPooling2D(tempData)
            [j for j in tempData['properties'] if j['id']=='outputDimension' ][0]['value']=valRet
        elif tempData['layerType'] in ['MaxPooling1D','AveragePooling1D']:
            valRet,messageInfo,traceBack=self.outputForMaxPooling1D(tempData)
            [j for j in tempData['properties'] if j['id']=='outputDimension' ][0]['value']=valRet
        # print ('NyokaUtilities $$$$$$$$$$$$$tempData',tempData)
        if messageInfo != 'success':
            tempData['errorMessage']=messageInfo
            tempData['errorTraceback']=traceBack
        return tempData


    ###################Below script is to get detaisl from a PMML file########################

    def getDataFields(self,tempObj):
        fieldNames=[]
        temp=tempObj['DataDictionary']
        temp=temp.get_DataField()
        for j in temp:
            fieldNames.append(j.name)
        return {'Column Names': fieldNames}


    def getHeaderInfo(self,tempObj):
        temp=tempObj['Header']
        tempDict={}
        tempDict['Time File Created']=temp.Timestamp.get_valueOf_()
        tempDict['Description']=temp.description
        return tempDict

    def getInfoNearestNeighborModel(self,tempObj):
        temp=tempObj['NearestNeighborModel'][0]
        tempDict={}
        tempDict['Model information']=[]
        tempDict['Model information'].append({'Algorithm Name':temp.algorithmName})
        tempDict['Model information'].append({'Function Type':temp.functionName})
        tempDict['Model information'].append({'Model Name':temp.modelName})
        tempDict['Model information'].append({'Number Of Neighbours':temp.numberOfNeighbors})
        return tempDict

    def getInfoOfDeepNetwork(self,tempObj):
        temp=tempObj['DeepNetwork'][0]
        tempDict={}
        tempDict['DeepNetwork information']=[]
        tempDict['DeepNetwork information'].append({'Function Type':temp.functionName})
        tempDict['DeepNetwork information'].append({'Model Name':temp.modelName})
        tempDict['DeepNetwork information'].append({'Number Of Layers':temp.numberOfLayers})
        return tempDict

    def getInfoMiningModel(self,tempObj):
        temp=tempObj['MiningModel'][0]
        tempDict={}
        tempDict['Model information']=[]
        tempDict['Model information'].append({'Function Type':temp.functionName})
        tempDict['Model information'].append({'Model Name':temp.modelName})
        if temp.Segmentation.multipleModelMethod=='modelChain':
            tempDict['Model information'].append({'Number of trees':len(temp.Segmentation.Segment[0].MiningModel.Segmentation.Segment)})
        else:
            tempDict['Model information'].append({'Number of trees':len(temp.Segmentation.Segment)})
        tempDict['Model information'].append({'Model Method':temp.Segmentation.multipleModelMethod})
        return tempDict



    def getInfoSupportVectorMachineModel(self,tempObj):
        temp=tempObj['SupportVectorMachineModel'][0]
        tempDict={}
        tempDict['Model information']=[]
        tempDict['Model information'].append({'Function Type':temp.functionName})
        tempDict['Model information'].append({'Model Name':temp.modelName})
        tempDict['Model information'].append({'Model Kernel  description':temp.RadialBasisKernelType.description})
        tempDict['Model information'].append({'Model Method':temp.classificationMethod})
        return tempDict


    def getInfoTreeModel(self,tempObj):
        temp=tempObj['TreeModel'][0]
        tempDict={}
        tempDict['Model information']=[]
        tempDict['Model information'].append({'Function Type':temp.functionName})
        tempDict['Model information'].append({'Model Name':temp.modelName})
        return tempDict

    def getInfoLinearModel(self,tempObj):
        temp=tempObj['RegressionModel'][0]
        tempDict={}
        tempDict['Model information']=[]
        tempDict['Model information'].append({'Function Type':temp.functionName})
        tempDict['Model information'].append({'Model Name':temp.modelName})
        return tempDict


    def getInfoOfNaiveBayesModel(self,tempObj):
        temp=tempObj['NaiveBayesModel'][0]
        tempDict={}
        tempDict['Model information']=[]
        tempDict['Model information'].append({'Function Type':temp.functionName})
        tempDict['Model information'].append({'Model Name':temp.modelName})
        return tempDict
    
    def getInfoOfAnomalyDetectionModel(self,tempObj):
        temp=tempObj['AnomalyDetectionModel'][0]
        tempDict={}
        tempDict['Model information']=[]
        tempDict['Model information'].append({'Function Type':temp.functionName})
        tempDict['Model information'].append({'Model Name':temp.modelName})
        tempDict['Model information'].append({'Algorithm Type':temp.algorithmType})
        return tempDict
    

    def changeStructure(self,mm):
        allInfo={}
        allInfo['information']=[]
        for j in mm:
            if j in ['Model information','DeepNetwork information']:
                if j =='Model information':
                    allInfo['modelGeneratedFrom']='SKLearn'
                else:
                    allInfo['modelGeneratedFrom']='DeepNetwork'
                for k in mm[j]:
                    for l in k:
                        tempDict={}
                        tempDict['property']=l
                        tempDict['value']=k[l]
                        allInfo['information'].append(tempDict)
            else:
                tempDict={}
                tempDict['property']=j
                tempDict['value']=mm[j]
                allInfo['information'].append(tempDict)

        if 'type' in mm:
            if mm['type']=='multi':
                allInfo['modelGeneratedFrom']='Workflow'


        return allInfo



    def pmmlToJson(self,filePath):
        pmmlObj=ny.parse(filePath,silence=True)
        pmmlDictObj=pmmlObj.__dict__

        # print ('0'*100,pmmlObj.get_type())

        if pmmlObj.get_type()=='multi':
            print ('came to Workflow')
            # print('*'*100)

            # print(PMMLMODELSTORAGE)
            # print('*'*100)
            
            import pathlib
            from trainModel.mergeTrainingV2 import TrainingViewModels
            pmmlFileObj=pathlib.Path(filePath)
            pmmlFileForKey=pmmlFileObj.name.replace(pmmlFileObj.suffix,'')
            from trainModel.mergeTrainingV2 import  NewModelOperations
            NewModelOperations().loadExecutionModel(filePath)
            modelInformation=PMMLMODELSTORAGE[pmmlFileForKey]
            # print ('PMMLMODELSTORAGE after >>>>>>>>>>> ',PMMLMODELSTORAGE)
            # print (modelInformation)

            toexp=TrainingViewModels().restructureModelInforForExportDict(modelInformation)
            # print ('toexp'*20)
            # print ('toexportDictN >>>>>>>> ',toexp)
            
            import copy,json

            tempSec={"name":"Section", "layerId":"Section",
            "children":[], "itemType":"FOLDING", "icon":"mdi mdi-group", "class":"wide",
            "modelType":"Workflow", "id":"id", "sectionId":"modName", "layerIndex":None,'connectionLayerId':None}

            tempData={"name":"Data","icon":"mdi mdi-database-plus","itemType":"DATA","layerId":None,
            "trainable":False,"modelType":"Workflow","id":None,"layerIndex":None,"connectionLayerId":None,
            "url":None,"filePath":None}

            tempCode={"name":"Code","icon":"mdi mdi-code-braces","itemType":"CODE","layerId":None,
            "trainable":False,"modelType":"Workflow","id":"K2PVI4HZ3NBGF","layerIndex":None,"connectionLayerId":None,
            "url":None,"filePath":None, "taskType":None,"scriptOutput":None,"scriptPurpose":None}

            tempModel={"name":"Model","icon":"mdi mdi-xml","itemType":"MODEL","layerId":None,"trainable":False,
                    "modelType":"Workflow","id":None,"layerIndex":None,"connectionLayerId":None,
                    "url":None,"filePath":None,"taskType":None}

            # toexp={'K2PSSUKYFRSMF': {'hyperparameters': None, 
            #                    'data': 'C:/Users/swsh/Desktop/ZMODGit/ZMOD/ZMOD/Data/newData2', 
            #                    'preProcessingScript': {'scripts': ['def addVal(x):\n    return x\n'], 'scriptpurpose': ['trainAndscore'], 'scriptOutput': ['DATA'], 'scriptPath': ['C:/Users/swsh/Desktop/ZMODGit/ZMOD/ZMOD/Code/scriptToTest.py']}, 
            #                    'modelObj': None, 
            #                    'pipelineObj': None, 
            #                    'featuresUsed': ['cylinders', 'displacement', 'horsepower', 'weight', 'acceleration'], 
            #                    'targetName': 'mpg', 
            #                    'postProcessingScript': {'scripts': [], 'scriptpurpose': [], 'scriptOutput': [], 'scriptPath': []}, 
            #                    'taskType': 'trainAndscore', 
            #                    'modelPath': 'C:\\Users\\swsh\\Desktop\\ZMODGit\\ZMOD\\ZMOD\\Models\\autoML2.pmml'}}


            workflowArch=[]
            for modTemp in list(toexp.keys()):
                temSecCop=copy.deepcopy(tempSec)#.copy()
                temSecCop['sectionId']=modTemp
                temSecCop["layerId"]=modTemp
                if toexp[modTemp]['data'] != None:
                    dataInfo=copy.deepcopy(tempData)
                    import pathlib
                    fileName=pathlib.Path(toexp[modTemp]['data']).name
                    dataInfo['layerId']=fileName
                    dataInfo['url']='/Data/'+fileName
                    dataInfo['filePath']=toexp[modTemp]['data']
                    temSecCop['children'].append(dataInfo)
                for numSc,sC in enumerate(toexp[modTemp]['preProcessingScript']['scriptPath']):
                    codeInfo=copy.deepcopy(tempCode)
                    fileName=pathlib.Path(toexp[modTemp]['preProcessingScript']['scriptPath'][numSc]).name
                    codeInfo['layerId']=fileName
                    codeInfo['url']='/Code/'+fileName
                    codeInfo['filePath']=toexp[modTemp]['preProcessingScript']['scriptPath'][numSc]
                    codeInfo['taskType']='PREPROCESSING'
                    codeInfo['scriptOutput']=toexp[modTemp]['preProcessingScript']['scriptOutput'][numSc]
                    codeInfo['scriptPurpose']=toexp[modTemp]['preProcessingScript']['scriptpurpose'][numSc]
                    temSecCop['children'].append(codeInfo)
                    
                
                modtempC=copy.deepcopy(tempModel)
                fileName=pathlib.Path(toexp[modTemp]['modelPath']).name
                modtempC['layerId']=fileName
                modtempC['url']='/Model/'+fileName
                modtempC['filePath']=toexp[modTemp]['modelPath']
                modtempC['taskType']=toexp[modTemp]['taskType']
                temSecCop['children'].append(modtempC)
                
                
                for numSc,sC in enumerate(toexp[modTemp]['postProcessingScript']['scriptPath']):
                    codeInfo=copy.deepcopy(tempCode)
                    fileName=pathlib.Path(toexp[modTemp]['postProcessingScript']['scriptPath'][numSc]).name
                    codeInfo['layerId']=fileName
                    codeInfo['url']='/Code/'+fileName
                    codeInfo['filePath']=toexp[modTemp]['postProcessingScript']['scriptPath'][numSc]
                    codeInfo['taskType']='POSTPROCESSING'
                    codeInfo['scriptOutput']=toexp[modTemp]['postProcessingScript']['scriptOutput'][numSc]
                    codeInfo['scriptPurpose']=toexp[modTemp]['postProcessingScript']['scriptpurpose'][numSc]
                    temSecCop['children'].append(codeInfo)
                    
                workflowArch.append(temSecCop)
                
            from random import choice
            from string import ascii_uppercase

            for num,i in enumerate(workflowArch):
                if i['itemType']=='FOLDING':
                    i['layerIndex']=num
                    i['id']=''.join(choice(ascii_uppercase) for i in range(12))
                    for num2,j in enumerate(i['children']):
                        j['layerIndex']=num2
                        j['id']=''.join(choice(ascii_uppercase) for i in range(12))
                else:
                    i['layerIndex']=num
                    i['id']=''.join(choice(ascii_uppercase) for i in range(12))
            # print ('l'*200)
            # print ('workflowArch',workflowArch)
            return workflowArch
        else:
            overAll=[]

            deepObject=pmmlDictObj['DeepNetwork'][0]
            listOfNetworkLayer=deepObject.NetworkLayer
            for lay in listOfNetworkLayer:
                networkDict=lay.__dict__
                tempDict={}
                tempDict['layerParam']={}
                tempDict['netParam']={}
                for j in networkDict:
                    if networkDict[j] is not None:
                        if j not in [ 'original_tagname_','LayerWeights','LayerParameters','Extension','LayerBias']:
                            tempDict['netParam'][j]=networkDict[j]
                        layerDict=networkDict['LayerParameters'].__dict__                    
                        for kk in layerDict:
                            if layerDict[kk] is not None:
                                if kk not in [ 'original_tagname_','Extension']:
                                    try:
                                        evalVal=list(ast.literal_eval(layerDict[kk]))
                                    except:
                                        evalVal=layerDict[kk]
                                    tempDict['layerParam'][kk]=evalVal
                        tempDict['layerParam']['trainable']=False if layerDict['trainable'] == False else True

                        if len(networkDict['Extension']) > 0:
                            ttt=networkDict['Extension'][0]
                            sectionVal=ttt.get_value()
                            import ast
                            tempDict['sectionId']=ast.literal_eval(sectionVal)['sectionId']
                        else:
                            tempDict['sectionId']=None
                overAll.append(tempDict)

            allLayers=MEMORY_OF_LAYERS['layerinfo'][0]['layers']
            listOFLayersName=[j['name'] for j in MEMORY_OF_LAYERS['layerinfo'][0]['layers']]
            architecture=[]
            for tempLay in overAll:
                import copy
                tempSpace=copy.deepcopy(allLayers[listOFLayersName.index(tempLay['netParam']['layerType'])])
                
                layerPARA=tempLay['layerParam']
                netWorkPARA=tempLay['netParam']
                for j in netWorkPARA:
                    try:
                        tempSpace[j]=netWorkPARA[j]
                    except:
                        pass

                for k in layerPARA:
                    for k2 in tempSpace['properties']:
                        if k2['id']==k:
                            k2['value']=layerPARA[k]
                            
                try:
                    tempSpace['sectionId']=tempLay['sectionId']
                except:
                    pass
                tempSpace['trainable']=layerPARA['trainable']
                architecture.append(tempSpace)
            
            forLoopSection=[j['sectionId'] for j in architecture]
            # print ('forLoopSection $$$$$$$$$$$$$$$',forLoopSection)
            tempSection={'children': [],'class': 'wide','icon': 'mdi mdi-group','id': '',
            'itemType': 'FOLDING','layerId': 'Section','layerIndex': '','name': 'Section',
            'sectionId': '',"sectionCollapse":True}

            import copy

            newarchitecture=[]
            tempSectionA=copy.deepcopy(tempSection)
            for num,secInfo in enumerate(forLoopSection):
                if secInfo is None:
                    newarchitecture.append(architecture[num])
                else:
                    if (num+1 < len(forLoopSection)) and (forLoopSection[num]==forLoopSection[num+1]):
                        tempSectionA['children'].append(architecture[num])
                    else:
                        tempSectionA['children'].append(architecture[num])
                        tempSectionA['sectionId']=secInfo
                        tempSectionA['layerId']='Section_'+str(num)
                        tempSectionA['name']='Section_'+str(num)
                        newarchitecture.append(tempSectionA)
                        tempSectionA=copy.deepcopy(tempSection)
            
            hd=pmmlDictObj['Header']
            scrptVal=pmmlDictObj['script']
            DataVal=pmmlDictObj['Data']
            import ast,pathlib
            try:
                try:
                    dataUrl=DataVal[0].filePath
                except:
                    dataUrl='Some issue'
                print ('$$$$$$$$$$$$$$$$$$$$$$',dataUrl)
                if dataUrl !='Some issue':
                    fObj=pathlib.Path(dataUrl)
                    dataCon={'icon': 'mdi mdi-database-plus','id': 'NNN',
                    'itemType': 'DATA','layerId':fObj.name ,'layerIndex': 0,'name': 'Data','url': dataUrl}
                    newarchitecture.insert(0,dataCon)

                    for counT,sc in enumerate(scrptVal):
                        import pathlib
                        scriptPurpose=sc.scriptPurpose
                        modelVal=sc.for_
                        classVal=sc.class_
                        filePathUrl=sc.filePath
                        fObjScrpt=pathlib.Path(filePathUrl)
                        scriptCon=  {"name": "Code","icon": "mdi mdi-code-braces","itemType": "CODE","modelFor":modelVal,
                            "layerId": fObjScrpt.name,"scriptPurpose":scriptPurpose,'url':filePathUrl,"layerIndex": "NA",'useFor':classVal}
                        newarchitecture.insert(counT+1,scriptCon)
                else:
                    pass

            except Exception as e:
                for counT,sc in enumerate(scrptVal):
                    scriptUrl=sc.class_
                    import pathlib
                    fObjScrpt=pathlib.Path(scriptUrl)
                    scriptCon=  {"name": "Code","icon": "mdi mdi-code-braces","itemType": "CODE",
                        "layerId": fObjScrpt.name,'url':scriptUrl,"layerIndex": "NA"}
                    newarchitecture.insert(counT,scriptCon)
                print (e,'some error occured')

            for num,i in enumerate(newarchitecture):
                if i['itemType']=='FOLDING':
                    i['layerIndex']=num
                    i['id']=''.join(choice(ascii_uppercase) for i in range(12))
                    for num2,j in enumerate(i['children']):
                        j['layerIndex']=num2
                        j['id']=''.join(choice(ascii_uppercase) for i in range(12))
                else:
                    i['layerIndex']=num
                    from random import choice
                    from string import ascii_uppercase
                    i['id']=''.join(choice(ascii_uppercase) for i in range(12))
            
            return newarchitecture


    #####################Add Update layer Utility Functions

    def checkItemType(self,inputDict):
        return inputDict['itemType']

    def checkChildren(self,inputDict):
        try:
            kk= inputDict['children']
            return True
        except:
            return False

    def getIndexOfInput(self,inputDict):
        return inputDict['layerIndex']

    def getIdOfInput(self,inputDict):
        return inputDict['id']

    def getIdOfSection(self,inputDict):
        try:
            return inputDict['sectionId']
        except:
            return None

    def addindex(self,inputDict):
        inputDict['layerIndex']=inputDict['layerIndex']+1
        return inputDict

    def getTemplateId(processTheInput):
        try:
            return processTheInput['templateId']
        except:
            return None

    def detailsofExistingArch(self,existingArch):
        listOFIndices=[i['layerIndex'] for i in existingArch]
        listOFIDS=[]
        listOfIdOFSections=[]
        listOfIdOFLayers=[]
        for j in existingArch:
            listOfIdOFLayers.append(j['id'])
            if j['itemType']=='FOLDING':
                for k in j['children']:
                    # print ('###################Came')
                    listOFIDS.append(k['id'])
                    listOfIdOFSections.append(k['id'])
            else:
                listOFIDS.append(j['id'])
        return (listOFIDS,listOFIndices,listOfIdOFSections,listOfIdOFLayers)

    def getLayerType(self,processTheInput):
        # print ('processTheInput',processTheInput)
        try:
            if processTheInput['itemType'] =='FOLDING':
                return 'SECTION'
            elif processTheInput['itemType']=='TEMPLATE':
                return 'TEMPLATE'
            elif processTheInput['itemType'] == 'LAYER':
                try:
                    kk=processTheInput['sectionId']
                    if kk != None:
                        return 'SECTION'
                    else:
                        return 'LAYER'
                except:
                    return 'LAYER'
            else:
                return 'LAYER'
        except:
            if processTheInput['itemType']=='TEMPLATE':
                return 'TEMPLATE'
            else:
                return 'LAYER'
            
        
    def checkAboutChildren(self,processTheInput):
        try:
            val=processTheInput['children']
            return True
        except:
            return False
        
    def hasSectionID(self,processTheInput):
        try:
            processTheInput['sectionId']
            return True
        except:
            False

    def detailsofSectionArch(self,sectionArch):
        listOFIDS=[i['id'] for i in sectionArch['children']]
        listOFIndices=[i['layerIndex'] for i in sectionArch['children']]
        listOFIdIndex=[(i['layerIndex'],i['id']) for i in sectionArch['children']]
        return (listOFIDS,listOFIndices,listOFIdIndex)
            
    def makeModification(self,existingArch,processTheInput):
        indexInObj=self.getIndexOfInput(processTheInput)
        newArch=[]
        for lay in existingArch:
            _layIndex=self.getIndexOfInput(lay)
            if _layIndex==indexInObj:
                # print ('>>>>{} Index {} is equal to layer'.format(_layIndex,indexInObj))
                newArch.append(processTheInput.copy())
                lay1=self.addindex(lay)
                newArch.append(lay1.copy())
            elif _layIndex < indexInObj:
                # print ('>>>>{} Index {} is greater to layer'.format(_layIndex,indexInObj))
                newArch.append(lay.copy())
                # newArch.append(processTheInput.copy())
            elif _layIndex > indexInObj:
                # print ('>>>>{} Index {} is lesser to layer'.format(_layIndex,indexInObj))
                lay1=self.addindex(lay)
                newArch.append(lay1.copy())
                
        return newArch