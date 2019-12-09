# pmlokaPMMLUtilities.py


import sys, os
import nyokaBase.PMML43Ext as pml
import ast
import numpy as np
from datetime import datetime

class NyokaPMMLUtilities:

    def convertToStandardJson(self,pp):
        # print ('pp >>>>>>>>> ',pp)
        tempData={}
        tempData['connectionLayerId']=pp['connectionLayerId']
        tempData['itemType']=pp['itemType']
        tempData['layerType']=pp['layerType']
        tempData['connectionLayerId']=pp['connectionLayerId']
        tempData['layerId']=pp['layerId']
        tempData['name']=pp['name']
        try:
            tempData['sectionId']=pp['sectionId']
        except:
            tempData['sectionId']=None
        tempData['properties']={}
        for j in pp['properties']:
            if j['id'] in ['inputDimension','outputDimension','kernel','dilationRate']:
                tempData['properties'][j['id']]=str(tuple(j['value']))
            elif j['id'] in ['stride','poolSize']:
                if len(j['value']) == 1:
                    tempData['properties'][j['id']] = str(tuple([j['value'], j['value']]))
                else:
                    tempData['properties'][j['id']]=str(tuple(j['value']))
            else:
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


    def outputForConv2D(self,tempData2):
        try:
            # print('outputForConv2D PMMLUtilities', tempData2)
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
                padding=self.calculatePadding(wid,wid,widStri,widFil)
                widthOutput=self.calculateOutputSize(wid,widStri,widFil,padding)
                heightOutput=self.calculateOutputSize(heig,heigStri,heigFil,padding)
            if featureMaps==None:
                return '({},{},{})'.format(widthOutput,heightOutput,channel)
            else:
                return '({},{},{})'.format(widthOutput,heightOutput,featureMaps)
        except:
            # print('No input came')
            widthOutput,heightOutput,featureMaps=0,0,0
            return '({},{},{})'.format(widthOutput,heightOutput,featureMaps)
        
        
    def outputForInput(self,inputDimension):
        return inputDimension['properties']['inputDimension']


    def outputForFlatten(self,tempData4):
        try:
            # print('>>>>>> input ', tempData4['properties']['inputDimension'])
            # print('>>>>>> output ', tempData4['properties']['outputDimension'])
            val=tempData4['properties']['outputDimension']
            return val
        except:
            # print('No input came PMML')
            return (0,0)


    def outputForPadding(self,tempData6):
        try:
            width,height,channel=tempData6['properties']['inputDimension']
            top_pad, bottom_pad,left_pad, right_pad=tempData6['properties']['paddingDims']
            width=width+left_pad+right_pad
            height=height+top_pad+bottom_pad
            return '({},{},{})'.format(width,height,channel)
        except:
            # print('No input came')
            width,height,channel=0,0,0
            return '({},{},{})'.format(width,height,channel)


    def outputForDense(self,tempdata7):
        # print ('$$$$$$$$$$$$$$ Dense 001',tempdata7)
        try:
            tomul=tempdata7['properties']['units']
            return '({},1)'.format(tomul) 
        except:
            # print('No input came')
            tomul=0
            return '({},1)'.format(tomul) 

    def weightBiasDense(self,tempdata):
        try:
            xSide=ast.literal_eval(tempdata['properties']['inputDimension'])[0]
            ySide=ast.literal_eval(tempdata['properties']['outputDimension'])[0]
            return ('({},{})'.format(xSide,ySide),'({},1)'.format(ySide))
        except:
            # print('No input came')
            xSide,ySide=0,0
            return ('({},{})'.format(xSide,ySide),'({},1)'.format(ySide))


    def weightConvo(self,tempdata):
        try:
            # print('weightConvo PMMLUtilities', tempdata)
            xSide=ast.literal_eval(tempdata['properties']['inputDimension'])[2]
            ySide=ast.literal_eval(tempdata['properties']['outputDimension'])[2]
            fx,fy=ast.literal_eval(tempdata['properties']['kernel'])
            if xSide==ySide:
                return '({},{},{},1)'.format(fx,fy,xSide)
            else:
                return '({},{},{},{})'.format(fx,fy,xSide,ySide)
        except:
            # print('No input came')
            fx,fy,xSide,ySide=0,0,0,0
            return '({},{},{},{})'.format(fx,fy,xSide,ySide)

        
        
    def weightBatchNormalization(self,tempdata):
        try:
            xSide=tempdata['properties']['inputDimension'][2]
            return '(4,{},1)'.format(xSide)
        except:
            # print('No input came')
            xSide=0
            return '(4,{},1)'.format(xSide)


    def addLayer(self,tempData):
        # print ('addLayerPMML 00000111>>>> ',tempData)
        tempLayerBiasobject=pml.LayerBias(content=[])
        tempBia=tempLayerBiasobject.__dict__
        tempBia['weightsFlattenAxis']="0"
        
        tempLayerWeightobject=pml.LayerWeights(content=[])
        tempWei=tempLayerWeightobject.__dict__
        tempWei['weightsFlattenAxis']="0"
        
        if tempData['layerType'] in ['Input']:
            tempData['properties']['outputDimension']=self.outputForInput(tempData)
        if tempData['layerType'] in ['Dropout']:
            if tempData['properties']['dropoutRate']=='':
                tempData['properties']['dropoutRate']='0'
            tempData['properties']['outputDimension']=self.outputForInput(tempData)
        elif tempData['layerType'] in ['BatchNormalization']:
            tempData['properties']['outputDimension']=self.outputForInput(tempData)
            tempWei['weightsShape']=self.weightBatchNormalization(tempData)
        elif tempData['layerType'] in ['Activation']:
            tempData['properties']['outputDimension']=tempData['properties']['inputDimension']
        elif tempData['layerType'] in ['Conv2D','DepthwiseConv2D']:
            tempData['properties']['outputDimension']=self.outputForFlatten(tempData)
            tempWei['weightsShape']=self.weightConvo(tempData)
        elif tempData['layerType'] in ['Flatten','GlobalAveragePooling2D']:
            tempData['properties']['outputDimension']=self.outputForFlatten(tempData)
        elif tempData['layerType'] in ['MaxPooling2D','AveragePooling2D']:
            tempData['properties']['outputDimension']=self.outputForFlatten(tempData)
        elif tempData['layerType'] in ['MaxPooling1D','AveragePooling1D']:
            tempData['properties']['outputDimension']=self.outputForFlatten(tempData)
            tempData['properties']['poolSize'] = str(tempData['properties']['poolSize'])
            tempData['properties']['stride'] = str(tempData['properties']['stride'])
        elif tempData['layerType'] in ['Reshape']:
            tempData['properties']['outputDimension']=self.outputForFlatten(tempData)
            tempData['properties']['reshapeTarget'] = str(tuple(tempData['properties']['reshapeTarget']))
        elif tempData['layerType'] in ['ZeroPadding2D','ZeroPadding1D']:
            tempData['properties']['outputDimension']=self.outputForFlatten(tempData)
            if len(tempData['properties']['paddingDims']) == 4:
                top_pad, bottom_pad, left_pad, right_pad = tempData['properties']['paddingDims']
                tempData['properties']['paddingDims'] = ((top_pad, bottom_pad), (left_pad, right_pad))
            elif len(tempData['properties']['paddingDims']) == 1:
                pad = tempData['properties']['paddingDims'][0]
                tempData['properties']['paddingDims'] = (pad, pad)
            tempData['properties']['paddingDims']=str(tuple(tempData['properties']['paddingDims']))
        elif tempData['layerType'] in ['Dense']:
            if tempData['properties']['activationFunction'] == "relu":
                tempData['properties']['activationFunction'] = "rectifier"
            elif tempData['properties']['activationFunction'] == "tanh":
                tempData['properties']['activationFunction'] = "tanch"
             
            tempData['properties']['outputDimension']=self.outputForDense(tempData)
            tempWei['weightsShape']=self.weightBiasDense(tempData)[0]
            tempBia['weightsShape']=self.weightBiasDense(tempData)[1]
        # print ('$$$$$$$$$$$$$$$tempData',tempData)
        tempLayerobject=pml.LayerParameters()
        tempvals=tempLayerobject.__dict__
        for j in list(tempvals.keys()):
            try:
                tempvals[j]=tempData['properties'][j]
            except:
                pass
            
        if tempData['sectionId'] == None:
            
            if tempData['layerType'] == 'Input':
                input_filed_name = "base64String"
                kk=pml.NetworkLayer(inputFieldName=input_filed_name, layerType=tempData['layerType'],layerId=tempData['layerId'],connectionLayerId=tempData['connectionLayerId'],LayerParameters=tempLayerobject)
            elif tempData['layerType'] == 'Dense':

                kk=pml.NetworkLayer(layerType=tempData['layerType'],layerId=tempData['layerId'],\
                                   connectionLayerId=tempData['connectionLayerId'],\
                                   LayerParameters=tempLayerobject,LayerWeights=tempLayerWeightobject,LayerBias=tempLayerBiasobject)
            elif tempData['layerType'] in ['Conv2D','DepthwiseConv2D','BatchNormalization'] :
                kk=pml.NetworkLayer(layerType=tempData['layerType'],layerId=tempData['layerId'],\
                                   connectionLayerId=tempData['connectionLayerId'],\
                                   LayerParameters=tempLayerobject,LayerWeights=tempLayerWeightobject)
            else:
                kk=pml.NetworkLayer(layerType=tempData['layerType'],layerId=tempData['layerId'],\
                                   connectionLayerId=tempData['connectionLayerId'],\
                                   LayerParameters=tempLayerobject)
                
        else:
            extensionInfo=[pml.Extension(value={'sectionId':tempData['sectionId']},anytypeobjs_=[''])]
            if tempData['layerType'] == 'Input':
                input_filed_name = "base64String"
                kk=pml.NetworkLayer(inputFieldName=input_filed_name,Extension=[extensionInfo], layerType=tempData['layerType'],\
                                   layerId=tempData['layerId'],connectionLayerId=tempData['connectionLayerId'],\
                                   LayerParameters=tempLayerobject)
            elif tempData['layerType'] == 'Dense':

                kk=pml.NetworkLayer(layerType=tempData['layerType'],layerId=tempData['layerId'],Extension=extensionInfo,\
                                   connectionLayerId=tempData['connectionLayerId'],\
                                   LayerParameters=tempLayerobject,LayerWeights=tempLayerWeightobject,LayerBias=tempLayerBiasobject)
            elif tempData['layerType'] in ['Conv2D','DepthwiseConv2D','BatchNormalization'] :

                kk=pml.NetworkLayer(layerType=tempData['layerType'],layerId=tempData['layerId'],Extension=extensionInfo,\
                                   connectionLayerId=tempData['connectionLayerId'],\
                                   LayerParameters=tempLayerobject,LayerWeights=tempLayerWeightobject)
            else:
                kk=pml.NetworkLayer(layerType=tempData['layerType'],layerId=tempData['layerId'],Extension=extensionInfo,\
                                   connectionLayerId=tempData['connectionLayerId'],\
                                   LayerParameters=tempLayerobject)

        return kk



    def getPmml(self,architecture):

        fName='classification'
        lenOfArch=len(architecture)
        mName='Keras Model'

        netWorkInfo=[]
        scriptVal=[]
        extensionInfoForData=[pml.Extension(value=[],anytypeobjs_=[''])]
        dataVal={}
        for counta,j in enumerate(architecture):
            if counta==0:
                someConectionId='na'
            else:
                someConectionId=tempConId
            if j['itemType'] in ['CODE']:
                # print ('##################',j)
                scriptFile=open(j['filePath'],'r')
                scriptCode=scriptFile.read()
                scriptCode=scriptCode.replace('<','&lt;')
                scriptInfo={}
                scrptVal=[]
                # dataVal['scriptUrl']=j['url']
                useFor=j['useFor']
                extensionInfoForScript=[pml.Extension(value=scrptVal,anytypeobjs_=[''])]
                scrp=pml.script(content=scriptCode,Extension=extensionInfoForScript,for_=useFor)
                scriptVal.append(scrp)
                tempConId=None
            elif j['itemType'] in ['DATA']:
                try:
                    dataVal['dataUrl']=j['filePath']
                    extensionInfoForData=[pml.Extension(value=dataVal,anytypeobjs_=[''])]
                except:
                    pass
                tempConId=None

                
            elif j['itemType']=='FOLDING':
        #         print (j)
                for k in j['children']:
                    tempdata7=self.convertToStandardJson(k)
                    tempdata7['connectionLayerId']=someConectionId
                    tempConId=tempdata7['layerId']
                    pp=addLayer(tempdata7)
                    netWorkInfo.append(pp)
                    someConectionId=tempConId
            else:
                # print ('Start of tamasha$$$$$$$$$$',j)
                tempdata7=self.convertToStandardJson(j)
                tempdata7['connectionLayerId']=someConectionId
                tempConId=tempdata7['layerId']
                # print ('pakda', tempdata7)
                pp=self.addLayer(tempdata7)
                netWorkInfo.append(pp)

        kk=pml.DeepNetwork(modelName=mName,functionName=fName,NetworkLayer=netWorkInfo,numberOfLayers=lenOfArch)
        tt=pml.Timestamp(datetime.now())
        hd=pml.Header(copyright="Copyright (c) 2018 Software AG",Extension=extensionInfoForData,
                description="Neural Network Model",
                Timestamp=pml.Timestamp(datetime.now()))

        jj=pml.PMML(version="4.3Ext",script=scriptVal,Header=hd,DeepNetwork=[kk])
        return jj


    def writePMML(self,architecture,fileName):

        # parser = argparse.ArgumentParser(description='To write PMML')
        # parser.add_argument('--fileName',required=True, help='Name of the project to keep tracking')
        # parser.add_argument('--architecture',required=True, help='Type of Model building exercise (Regression/Classification)')

        # fileName=args.fileName
        # architecture=args.architecture
        jj = self.getPmml(architecture)
        fff=open(fileName,'w')

        jj.export(fff,0)



    # if __name__== "__main__":
    #   writePMML()