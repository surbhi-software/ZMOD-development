# utilities.py

# from nyokaBase.keras.keras_model_to_pmml import KerasToPmml
from nyokaBase.keras.pmml_to_keras_model import GenerateKerasModel 
from nyokaBase import PMML43Ext as ny
from keras.preprocessing.image import ImageDataGenerator

from keras.preprocessing import image
import os,json,ast
from random import choice
from string import ascii_uppercase

from tensorflow import Graph, Session
import tensorflow as tf
from string import ascii_uppercase
from random import choice
from utility.utilityClass import RUNNING_TASK_MEMORY
import datetime
import skimage
import numpy as np

global PMMLMODELSTORAGE

PMMLMODELSTORAGE={}

class KerasUtilities:


    def updateStatusOfTraining(self,filePath,updatedStatus,info_dict=None,top_level=None):
        sFile=open(filePath,'r')
        sFileText=sFile.read()
        sFile.close()
        data_details=json.loads(sFileText)
        data_details['status']=updatedStatus
        if top_level:
            for key, val in top_level.items():
                data_details[key]=val
        if info_dict:
            data_details['information']=[]
            for key, val in info_dict.items():
                data_details['information'].append({'property':key,'value':val})
        with open(filePath,'w') as filetosave:
            json.dump(data_details, filetosave)
        return 'Success'

    def updateStatusKeyOfTraining(self,filePath,keyTop,keyIn,updatedStatus):
        sFile=open(filePath,'r')
        sFileText=sFile.read()
        sFile.close()
        data_details=json.loads(sFileText)
        # print (data_details)
        # print (type(data_details))
        information=data_details[keyTop]
        propList=[i['property'] for i in information].index('Number of Images generated')
        information[propList]['value']=updatedStatus
        data_details[keyTop]=information
        with open(filePath,'w') as filetosave:
            json.dump(data_details, filetosave)
        return 'Success'

    def updateStatusofProcess(self,filePath,updatedStatus):
        sFile=open(filePath,'r')
        sFileText=sFile.read()
        sFile.close()
        data_details=json.loads(sFileText)
        data_details['status']=updatedStatus
        if updatedStatus=='Complete':
                data_details['completedOn']=str(datetime.datetime.now())
        with open(filePath,'w') as filetosave:
            json.dump(data_details, filetosave)
        return 'Success'

    def getPredClasses(self,nyoka_pmml_obj):
        targetVar = self.getTargetVariable(nyoka_pmml_obj)
        tempObj=nyoka_pmml_obj.get_DataDictionary()
        if str(tempObj) != 'None':
            predClasses = list()
            for dataField in tempObj.get_DataField():
                if dataField.name == targetVar:
                    for val in dataField.get_Value():
                        predClasses.append(val.get_value())
        else:
            predClasses=[]
        # predClasses=[eleData.get_value() for dataFobj in tempObj.get_DataField() for eleData in dataFobj.get_Value()]
    #     predClasses={j:k for j,k in enumerate(predClasses)}
        return predClasses

    


    def loadPMMLmodel(self,filepath,idforData=None):

        def readScriptFromPMML(scrptCode,useForVal):
            code=None
            for num,sc in enumerate(scrptCode):
                useFor=sc.for_
                # print ('>>>>>>>UUUUUU>>>>>>>',useFor,useForVal)
                
                if useFor==useForVal:
                    scripCode=sc.get_valueOf_()
                    # print (scripCode)
                    code = scripCode.lstrip('\n')
                    lines = []
                    code = scripCode.lstrip('\n')
                    leading_spaces = len(code) - len(code.lstrip(' '))
                    for line in code.split('\n'):
                        lines.append(line[leading_spaces:])
                    code = '\n'.join(lines)
            return code


        global PMMLMODELSTORAGE
        try:
            print ('step 1',filepath)
            pmmlName=os.path.basename(filepath).split('.')[0]
            nyoka_pmml_obj = ny.parse(filepath, True)
            pmmlObj=nyoka_pmml_obj.__dict__
            try:
                checkMRCNN=nyoka_pmml_obj.DeepNetwork[0].Extension[0].name == 'config'
            except:
                checkMRCNN=False
            #MaskRcnn model
            if (nyoka_pmml_obj.DeepNetwork)  and (checkMRCNN==True):
                from nyokaBase.mrcnn import pmml_to_maskrcnn
                from nyokaBase.mrcnn import model as modellib
                predClasses=self.getPredClasses(nyoka_pmml_obj)
                modelFolder='./logs/MaskRCNNWei_'+''.join(choice(ascii_uppercase) for i in range(12))+'/'
                self.checkCreatePath(modelFolder)
                model_graph = Graph()
                with model_graph.as_default():
                    tf_session = Session()
                    with tf_session.as_default():
                        modelRecon=pmml_to_maskrcnn.GenerateMaskRcnnModel(nyoka_pmml_obj)
                        weight_file = modelFolder+'/dumpedWeights.h5'
                        modelRecon.model.keras_model.save_weights(weight_file)
                        MODEL_DIR=modelFolder
                        model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=modelRecon.config)
                        model.load_weights(weight_file,by_name=True)
                        model_graph = tf.get_default_graph()
                # pmmlName = pmmlName
                PMMLMODELSTORAGE[pmmlName]={}
                PMMLMODELSTORAGE[pmmlName]['model']=model
                PMMLMODELSTORAGE[pmmlName]['modelType']='MRCNN'
                PMMLMODELSTORAGE[pmmlName]['model_graph']=model_graph
                PMMLMODELSTORAGE[pmmlName]['predClasses']=list(predClasses)
                PMMLMODELSTORAGE[pmmlName]['tf_session']=tf_session
                modelType='MRCNN'
                

            #DeepNetwokr Model
            elif nyoka_pmml_obj.DeepNetwork:
                hdInfo=pmmlObj['Header']
                try:
                    hdExtDet=ast.literal_eval(hdInfo.Extension[0].get_value())
                except:
                    pass
                
                print ('step 2')
                predClasses=self.getPredClasses(nyoka_pmml_obj)
                print ('step 3')
                newNet=nyoka_pmml_obj.DeepNetwork[0]
                print ('step 4')
                scrptCode=nyoka_pmml_obj.script
                # print ('Step 4.1 ',scrptCode)
                
                
                try:
                    preCode=readScriptFromPMML(scrptCode,'TEST')
                except:
                    preCode=None
                try:
                    postCode=readScriptFromPMML(scrptCode,'POSTPROCESSING')
                except:
                    postCode=None
                    
                model_graph = Graph()
                with model_graph.as_default():
                    tf_session = Session()
                    with tf_session.as_default():
                        print ('step 5')
                        from nyokaBase.keras.pmml_to_keras_model import GenerateKerasModel
                        print ('step 5.1')
                        model_net = GenerateKerasModel(nyoka_pmml_obj)
                        print ('step 5.2')
                        model = model_net.model
                        model_graph = tf.get_default_graph()
                        print ('step 6')
                inputShapevals=[inpuShape.value for inpuShape in list(model.input.shape)]
                PMMLMODELSTORAGE[pmmlName]={}
                PMMLMODELSTORAGE[pmmlName]['model']=model
                PMMLMODELSTORAGE[pmmlName]['predClasses']=predClasses
                PMMLMODELSTORAGE[pmmlName]['preProcessScript']=preCode
                PMMLMODELSTORAGE[pmmlName]['postProcessScript']=postCode
                try:
                    PMMLMODELSTORAGE[pmmlName]['scriptOutput']=hdExtDet['scriptOutput']
                except:
                    PMMLMODELSTORAGE[pmmlName]['scriptOutput']=''
                print ('step 7')
                try:
                    PMMLMODELSTORAGE[pmmlName]['inputShape']=inputShapevals
                except:
                    PMMLMODELSTORAGE[pmmlName]['inputShape']='CheckSomeissue'
                PMMLMODELSTORAGE[pmmlName]['status']='loaded'
                # print ('step 8')
                PMMLMODELSTORAGE[pmmlName]['model_graph']=model_graph
                PMMLMODELSTORAGE[pmmlName]['tf_session']=tf_session
                PMMLMODELSTORAGE[pmmlName]['modelType']='kerasM'
                modelType='kerasM'
                # print ('###################',PMMLMODELSTORAGE)
            #Sklearn Model
            else:
                print ('Next Step 2 >>>>>>>>>>>>')
                from nyokaBase.reconstruct.pmml_to_pipeline_model import generate_skl_model
                print ('Next Step 3 >>>>>>>>>>>>')
                sklModelPipeline=generate_skl_model(filepath)
                print ('Next Step 4 >>>>>>>>>>>>')
                # if hasattr(sklModelPipeline.steps[-1][-1],'classes_'):
                #     print ('sklModelPipeline.steps[-1][-1] >>> ',sklModelPipeline.steps[-1][-1])
                #     predClasses=sklModelPipeline.steps[-1][-1].classes_
                # else:
                try:
                    predClasses=self.getPredClasses(nyoka_pmml_obj)
                except:
                    predClasses=[]
                print ('Next Step 5 >>>>>>>>>>>>')
                targetVar = self.getTargetVariable(nyoka_pmml_obj)
                PMMLMODELSTORAGE[pmmlName]={}
                PMMLMODELSTORAGE[pmmlName]['model']=sklModelPipeline
                PMMLMODELSTORAGE[pmmlName]['predClasses']=list(predClasses)
                PMMLMODELSTORAGE[pmmlName]['targetVar']=targetVar
                PMMLMODELSTORAGE[pmmlName]['modelType']='sklearnM'
                modelType='sklearnM'
            return (pmmlName,'Success',modelType)
        except Exception as e:
            print(str(e))
            import traceback
            print(str(traceback.format_exc()))
            return (pmmlName, 'Failure',None)


    def getTargetVariable(self,nyoka_pmml_obj):
        main_model = None
        targetVar=''
        if nyoka_pmml_obj.MiningModel:
            main_model=nyoka_pmml_obj.MiningModel[0]
        elif nyoka_pmml_obj.TreeModel:
            main_model=nyoka_pmml_obj.TreeModel[0]
        elif nyoka_pmml_obj.SupportVectorMachineModel:
            main_model=nyoka_pmml_obj.SupportVectorMachineModel[0]
        elif nyoka_pmml_obj.DeepNetwork:
            main_model=nyoka_pmml_obj.DeepNetwork[0]
        elif nyoka_pmml_obj.RegressionModel:
            main_model=nyoka_pmml_obj.RegressionModel[0]
        elif nyoka_pmml_obj.NeuralNetwork:
            main_model=nyoka_pmml_obj.NeuralNetwork[0]
        elif nyoka_pmml_obj.NaiveBayesModel:
            main_model=nyoka_pmml_obj.NaiveBayesModel[0]
        elif nyoka_pmml_obj.NearestNeighborModel:
            main_model=nyoka_pmml_obj.NearestNeighborModel[0]
        elif nyoka_pmml_obj.AnomalyDetectionModel:
            main_model=nyoka_pmml_obj.AnomalyDetectionModel[0]

        for miningField_ in main_model.MiningSchema.MiningField:
            if miningField_.usageType == 'target':
                targetVar = miningField_.name
            else:
                targetVar=None
        return targetVar


    def deleteLoadedModelfromMemory(self,modelname):
        global PMMLMODELSTORAGE
        # pmmlName=os.path.basename(modelFile).split('.')[0]
        del PMMLMODELSTORAGE[modelname]
        return ('Success')


    def detectObject(self,filePath, modelName):
        global PMMLMODELSTORAGE
        pmmlstoragepointer=modelName.replace('.pmml','')
        pointerObj=PMMLMODELSTORAGE[pmmlstoragepointer]
        model_graph = pointerObj['model_graph']
        tf_session = pointerObj['tf_session']
        with model_graph.as_default():
            with tf_session.as_default():
                model=pointerObj['model']
                image = skimage.io.imread(filePath)
                result = model.detect([image],verbose=1)
        for key,val in result[0].items():
            result[0][key] = val.tolist()
        # target_path='./logs/'+''.join(choice(ascii_uppercase) for i in range(12))+'/'
        # kerasUtilities.checkCreatePath(target_path)
        # resafile=target_path+'result.txt'
        # with open(resafile,'w') as ff:
        #   json.dump(result, ff)
        data_details = result[0]
        return data_details

    def predictImagedata(self,pmmlstoragepointer,testimage):
        # print ('Came to image prediction')
        global PMMLMODELSTORAGE

        pointerObj=PMMLMODELSTORAGE[pmmlstoragepointer]
        # print ('pointerObj',pointerObj)
        model_graph = pointerObj['model_graph']
        tf_session = pointerObj['tf_session']
        with model_graph.as_default():
            with tf_session.as_default():
                model=PMMLMODELSTORAGE[pmmlstoragepointer]['model']
                predClasses=PMMLMODELSTORAGE[pmmlstoragepointer]['predClasses']
                inputShapevals=PMMLMODELSTORAGE[pmmlstoragepointer]['inputShape']
                # print (inputShapevals)
                img_height, img_width=inputShapevals[1:3]
                img = image.load_img(testimage, target_size=(img_height, img_width))
                x = image.img_to_array(img)
                x=x/255
                x=x.reshape(1,img_height, img_width,3)
                predi=model.predict(x)
                # print(' >>>>>>>>>>>>>>> predi ',predi,predClasses)
                if len(predClasses)==0:
                    predClasses=['class_'+str(i) for i in range(len(np.ravel(predi)))]
                targetResult= {j:str(float(k)) for j,k in zip(predClasses,list(predi[0]))}

        target_path='./logs/'+''.join(choice(ascii_uppercase) for i in range(12))+'/'
        self.checkCreatePath(target_path)
        target_path=target_path+'temp.txt'

        # resafile='./logs/'+'temp.txt'
        # print('result>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',targetResult)
        with open(target_path,'w') as fila:
            json.dump(targetResult,fila)
        return target_path
        # except:
        #     return("Something didn't went well")

    def predictCustomCodedata(self,pmmlstoragepointer,filpath,scriptOutput):
        global PMMLMODELSTORAGE
        pointerObj=PMMLMODELSTORAGE[pmmlstoragepointer]
        codePart=pointerObj['preProcessScript']
        fnaMe='./trainModel/testPreprocessing.py'
        with open(fnaMe,'w') as k:
            k.write(codePart)
        # print ('Code File written')
        import importlib.util
        spec=importlib.util.spec_from_file_location('preProcessing',fnaMe)
        preProcessing=spec.loader.load_module()
        from preProcessing import preProcessing
        from string import ascii_uppercase
        from random import choice

        if scriptOutput == 'IMAGE':
            target_path2='./logs/'+''.join(choice(ascii_uppercase) for i in range(12))+'/'
            target_path=target_path2+'/test/'
            self.checkCreatePath(target_path2)
            self.checkCreatePath(target_path)
            preProcessing(filpath,target_path)
            # print ('saving done')

            listOfFiles=os.listdir(target_path)
            if len(listOfFiles)>100:
                tempRunMemory=self.predictFolderDataInBatch(pmmlstoragepointer,target_path2,len(listOfFiles))
                tempRunMemory['inTask']=True
                return tempRunMemory
            else:
                targetResult=self.predictFolderdata(pmmlstoragepointer,target_path2)
        elif scriptOutput == 'DATA':
            testData=preProcessing(filpath)
            targetResult=self.predictFiledata(pmmlstoragepointer,testData)

        try:
            os.remove(fnaMe)
        except:
            pass
            
        return targetResult

    def predictFiledata(self,pmmlstoragepointer,testData, modelType=None):
        print('$$$$$$$$$$$$$$$$$$ PredictFileData $$$$$$$$$$$$$$$')
        global PMMLMODELSTORAGE
        pointerObj=PMMLMODELSTORAGE[pmmlstoragepointer]
        target_path='./logs/'+''.join(choice(ascii_uppercase) for i in range(12))+'/'
        self.checkCreatePath(target_path)
        if modelType =="sklearnM":
            print ('Came to sklearn part')
            model=pointerObj['model']
            predClasses=pointerObj['predClasses']
            targetVar=pointerObj['targetVar']
            pred=model.predict(testData)
            import pandas as pd
            if pointerObj['extenFile'] == '.json':
                targetResult={}
                resafile=target_path+'result.txt'
                for idx, data in enumerate(pred):
                    if 'int32' in str(type(data)):
                        data=int(data)
                    targetResult[idx]=data

                with open(resafile,'w') as fila:
                    json.dump(targetResult,fila)
            else:
            # tempOutput=pd.DataFrame(data=pred, columns=[targetVar])
                testData['predicted_'+targetVar]=pred
            # tempOutput.to_csv(resafile, index=False)
                resafile=target_path+'result.csv'
                testData.to_csv(resafile, index=False)
        else:
            model_graph = pointerObj['model_graph']
            tf_session = pointerObj['tf_session']
            with model_graph.as_default():
                with tf_session.as_default():
                    model=PMMLMODELSTORAGE[pmmlstoragepointer]['model']
                    predClasses=PMMLMODELSTORAGE[pmmlstoragepointer]['predClasses']
                    inputShapevals=PMMLMODELSTORAGE[pmmlstoragepointer]['inputShape']
                    pred=model.predict(testData.values)
            targetResult={}
            for idx, data in enumerate(pred):
                if predClasses == []:
                    try:
                        data = float(data[0])
                    except:
                        data = float(data)
                    targetResult[idx]=data
                else:
                    targetResult[idx]={k:float(v) for k,v in zip(predClasses, data)}
            # targetResult=pred
            resafile=target_path+'result.txt'
            # print('result>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',targetResult)
            with open(resafile,'w') as fila:
                json.dump(targetResult,fila)
        return resafile


    def predictFiledataReturnJson(self,pmmlstoragepointer,testData, modelType=None):
        # print('$$$$$$$$$$$$$$$$$$ PredictFileData $$$$$$$$$$$$$$$')
        global PMMLMODELSTORAGE
        pointerObj=PMMLMODELSTORAGE[pmmlstoragepointer]
        target_path='./logs/'+''.join(choice(ascii_uppercase) for i in range(12))+'/'
        self.checkCreatePath(target_path)
        if modelType and modelType=="sklearnM":
            model=pointerObj['model']
            predClasses=pointerObj['predClasses']
            targetVar=pointerObj['targetVar']
            if len(predClasses) >1:
                pred=model.predict_proba(testData)
                seraSera=[]
                for i in scores:
                    seraSera.append({k:j for k,j in zip(['1','2'],i)})
                resaRes={'predictions':seraSera}
            else:
                pred=model.predict(testData)
                resaRes={'predictions':pred.tolist()}
        
            
        else:
            model_graph = pointerObj['model_graph']
            tf_session = pointerObj['tf_session']
            with model_graph.as_default():
                with tf_session.as_default():
                    model=PMMLMODELSTORAGE[pmmlstoragepointer]['model']
                    predClasses=PMMLMODELSTORAGE[pmmlstoragepointer]['predClasses']
                    inputShapevals=PMMLMODELSTORAGE[pmmlstoragepointer]['inputShape']
                    pred=model.predict(testData.values)

            if len(predClasses) > 1:
                seraSera=[]
                for i in scores:
                    seraSera.append({k:j for k,j in zip(['1','2'],i)})
                resaRes={'predictions':seraSera}
            else:
                resaRes={'predictions':pred}
            
        return resaRes

    def predictDataWithPostScript(self,pmmlstoragepointer,filpath,scriptOutput):

        print ('Step 1.1')
        global PMMLMODELSTORAGE
        pointerObj=PMMLMODELSTORAGE[pmmlstoragepointer]
        #####################>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>###############
        codePart=pointerObj['preProcessScript']
        print ('Step 1.2')
        fnaMe='./trainModel/testPreprocessing.py'
        with open(fnaMe,'w') as k:
            k.write(codePart)
        print ('Code File written Pre Process')
        import importlib.util
        spec=importlib.util.spec_from_file_location('preProcessing',fnaMe)
        preProcessing=spec.loader.load_module()

        print ('Step 1.3')

        #####################>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>###############

        codePart2=pointerObj['postProcessScript']
        fnaMe2='./trainModel/testPostprocessing.py'
        with open(fnaMe2,'w') as k:
            k.write(codePart2)
        print ('Code File written POST Process')
        spec2=importlib.util.spec_from_file_location('postProcessing',fnaMe2)
        postProcessing=spec2.loader.load_module()

        print ('Step 1.4')

        #####################>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>###############
        from preProcessing import preProcessing
        from postProcessing import postProcessing
        from string import ascii_uppercase
        from random import choice

        print ('Step 1.5')

        if scriptOutput == 'IMAGE':
            target_path2='./logs/'+''.join(choice(ascii_uppercase) for i in range(12))+'/'
            target_path=target_path2+'/test/'
            self.checkCreatePath(target_path2)
            self.checkCreatePath(target_path)
            print ('Step 1.6')
            preProcessing(filpath,target_path)
            print ('Step 1.7')
            print (' Image chunk saving done')

            print ('Step 1.8')
            listOfFiles=os.listdir(target_path)
            if len(listOfFiles)>1000000:
                tempRunMemory=self.predictFolderDataInBatch(pmmlstoragepointer,target_path2,len(listOfFiles))
                tempRunMemory['inTask']=True
                return tempRunMemory
            else:
                targetResult=self.predictFolderdata(pmmlstoragepointer,target_path2)

            print ('Step 1.9')

            # outputOfPreScript=open(targetResult,'r').read()
            # outputOfPreScript=json.loads(outputOfPreScript)

            print ('Step 1.10')

            target_path3='./logs/'+''.join(choice(ascii_uppercase) for i in range(12))+'/'
            self.checkCreatePath(target_path3)

            print ('Step 1.11')
            outPutAfterPostProcess=postProcessing(filpath,targetResult,target_path3)
            print ('Step 1.12')

        elif scriptOutput == 'DATA':
            print ('Use case need to be discussed')

        try:
            os.remove(fnaMe2)
        except:
            pass
        try:
            os.remove(fnaMe)
        except:
            pass
        return outPutAfterPostProcess

    def predictDataWithOnlyPostScript(self,pmmlstoragepointer,filpath,extenFile):
        import importlib.util
        print ('Step 11.1')
        global PMMLMODELSTORAGE
        pointerObj=PMMLMODELSTORAGE[pmmlstoragepointer]
        #####################>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>###############

        codePart2=pointerObj['postProcessScript']
        fnaMe2='./trainModel/testPostprocessing.py'
        with open(fnaMe2,'w') as k:
            k.write(codePart2)
        print ('Code File written POST Process')
        spec2=importlib.util.spec_from_file_location('postProcessing',fnaMe2)
        postProcessing=spec2.loader.load_module()

        print ('Step 11.2')
        #####################>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>###############
        from postProcessing import postProcessing
        from string import ascii_uppercase
        from random import choice

        print ('Step 11.5')



        if extenFile in ['.jpg','.JPG','.png','.PNG']:
            target_path2='./logs/'+''.join(choice(ascii_uppercase) for i in range(12))+'/'
            target_path=target_path2+'/test/'
            self.checkCreatePath(target_path2)
            self.checkCreatePath(target_path)
            print ('Step 11.6')
            targetResult=self.predictImagedata(pmmlstoragepointer,filpath)

            print ('Step 11.9')

            target_path3='./logs/'+''.join(choice(ascii_uppercase) for i in range(12))+'/'
            self.checkCreatePath(target_path3)

            print ('Step 11.11')
            outPutAfterPostProcess=postProcessing(targetResult)
            print ('Step 11.12')

        elif scriptOutput == 'DATA':
            print ('Use case need to be discussed')

        try:
            os.remove(fnaMe2)
        except:
            pass
        return outPutAfterPostProcess



    def predictFolderdata(self,pmmlstoragepointer,filpath,statusfileLocation=None):

        import os
        stepForval=len(os.listdir(filpath+'/test'))
        print (stepForval,'))))))))))))))))))))))))))))))))))))))')
        global PMMLMODELSTORAGE
        pointerObj=PMMLMODELSTORAGE[pmmlstoragepointer]
        from string import ascii_uppercase
        from random import choice

        target_path='./logs/'+''.join(choice(ascii_uppercase) for i in range(12))+'/'
        self.checkCreatePath(target_path)
        model_graph = pointerObj['model_graph']
        tf_session = pointerObj['tf_session']
        with model_graph.as_default():
            with tf_session.as_default():
                model=PMMLMODELSTORAGE[pmmlstoragepointer]['model']
                predClasses=PMMLMODELSTORAGE[pmmlstoragepointer]['predClasses']
                inputShapevals=PMMLMODELSTORAGE[pmmlstoragepointer]['inputShape']
                img_height, img_width=inputShapevals[1:3]
                test_datagen = ImageDataGenerator(rescale=1. / 255)
                test_generator = test_datagen.flow_from_directory(shuffle=False,
                                        directory=filpath,target_size=(img_height, img_width),
                                        color_mode="rgb",batch_size=1,class_mode=None,)
                # test_generator.reset()
                pred=model.predict_generator(test_generator,verbose=1,steps=stepForval)
                # print(' >>>>>>>>>>>>>>> predi ',pred)
        # {j:float(k) for j,k in zip(predClasses,list(pred))}
        listOfFiles=os.listdir(filpath)
        filpath=filpath+'/'+listOfFiles[0]
        listOfFiles=os.listdir(filpath)
        targetResult={}
        for tempFile,pr in zip(listOfFiles,list(pred)):
            import pathlib
            expel=pathlib.Path(tempFile).suffix
            tempFile=tempFile.replace(expel,'')
            tempFile=tempFile.replace('id_','')
            tempres={j:float(k) for j,k in zip(predClasses,list(pr))}
            targetResult[tempFile]=tempres
        resafile=target_path+'result.txt'
        with open(resafile,'w') as fila:
            json.dump(targetResult,fila)
        if statusfileLocation:
            info_dict = {
                "No of files scored":stepForval,
                "Classes":predClasses,
                "Image Shape":test_generator.image_shape,
                "Image Foramt":test_generator.save_format,
                "Color Mode":test_generator.color_mode
                }
            top_dict={
                "fileLocation":resafile
            }
            self.updateStatusOfTraining(statusfileLocation,'Complete',info_dict=info_dict,top_level=top_dict)
        return resafile


    def predictFolderDataInBatch(self,pmmlstroragepointer,filpath,numFile):
        from threading import Thread

        idforData=''.join(choice(ascii_uppercase) for i in range(12))
        saveStatus='./logs/'+idforData+'/'
        self.checkCreatePath(saveStatus)
        statusfileLocation=saveStatus+'status.txt'
        with open(statusfileLocation,'w') as filetosave:
            json.dump({}, filetosave)
        
        prc = Thread(target=self.predictFolderdata,args=(pmmlstroragepointer,filpath,statusfileLocation))
        prc.start()
        pID = prc.ident
        tempRunMemory={'idforData': idforData,
			'status': 'Scoring Failed' if pID==-1 else 'In Progress',
			'createdOn': str(datetime.datetime.now()),
			'type': 'BatchScore',
			'pid':pID,
            'newPMMLFileName':pmmlstroragepointer,
            'information':[
                {'property':'No of files to be scored', 'value':numFile}
            ]}
        RUNNING_TASK_MEMORY.append(tempRunMemory)
        with open(statusfileLocation,'w') as filetosave:
            json.dump(tempRunMemory, filetosave)
        return tempRunMemory
        



    settingFilePath='settingFiles/'
    def tensorboardInfo(self):
        import pandas as pd
        portInfo=pd.read_csv(settingFilePath+'tensorboardPort.txt')
        inda=portInfo[portInfo['runPortsUsage']=='inactive'].index[0]
        portInfo['runPortsUsage'].loc[inda]='active'
        portUsed=portInfo['runPorts'].loc[inda]
        portInfo.to_csv(settingFilePath+'tensorboardPort.txt',index=False)
        return (int(portUsed))

    def checkCreatePath(self,folderPath):
        try:
            if os.path.exists(folderPath):
                return ('path exist')
            else:
                os.makedirs(folderPath)
                return ('path created')
        except:
            os.makedirs(folderPath)
            return ('path created')

    ########################Nyoka Load into Keras#######################################
