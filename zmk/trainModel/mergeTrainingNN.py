import pandas  as pd
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

from trainModel.mergeTrainingV2 import TrainingViewModels

selDev="/device:CPU:0"
def gpuCPUSelect(selDev):
	return selDev


class NeuralNetworkModelTrainer:

	def __init__(self):
		self.pathOfData = None
		self.logFolder = 'logs/'
		self.statusFile = None
		self.scriptFilepath = './trainModel/'
		self.trainFolder = None
		self.validationFolder = None
		self.pmmlObj = None
		self.hdExtDet = None
		self.pmmlfileObj = None
		self.lockForStatus = Lock()


	def upDateStatus(self):
		self.lockForStatus.acquire()
		sFile=open(self.statusFile,'r')
		sFileText=sFile.read()
		data_details=json.loads(sFileText)
		sFile.close()
		self.lockForStatus.release()
		return data_details

	def startTensorBoard(self, tensorboardLogFolder):
		print ('tensorboardLogFolder >>>>>>',tensorboardLogFolder)
		tensor_board=keras.callbacks.TensorBoard(log_dir=tensorboardLogFolder, histogram_freq=0,write_graph=True, write_images=False)
		return tensor_board



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


	def updateSectionInfo(self,networkObj):
		originalNetworkLayer = self.pmmlfileObj.DeepNetwork[0].NetworkLayer
		assert len(originalNetworkLayer) == len(networkObj[0].NetworkLayer)
		for index, layer in enumerate(originalNetworkLayer):
			if layer.Extension:
				networkObj[0].NetworkLayer[index].Extension = layer.Extension
		return networkObj

	def updateStatusWithError(self,data_details,statusOFExe,errorMessage,errorTraceback,statusFile):
		print ('came to update status')
		data_details=self.upDateStatus()
		data_details['status']=statusOFExe
		data_details['errorMessage']=errorMessage
		data_details['errorTraceback']=errorTraceback
		print ('12ns',data_details)
		with open(statusFile,'w') as filetosave:
			json.dump(data_details, filetosave)
		return ('done')

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

	def generateAndCompileModel(self, lossType, optimizerName, learningRate, listOfMetrics, compileTestOnly=False):

		def f1(y_true, y_pred):
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
			from nyokaBase.keras.pmml_to_keras_model import GenerateKerasModel
			modelObj=GenerateKerasModel(self.pmmlfileObj)
		except Exception as e:
			if not compileTestOnly:
				data_details=self.upDateStatus()
				self.updateStatusWithError(data_details,'Training Failed','Error while generating Keras Model >> '+ str(e),traceback.format_exc(),self.statusFile)
			else:
				data_details = {}
				self.updateStatusWithError(data_details,'Model Compilation Failed','Error while compiling Model >> '+ str(e),traceback.format_exc(),self.statusFile)
			return data_details
		model=modelObj.model

		try:
		    if 'f1' in listOfMetrics:
		        listOfMetrics.remove('f1')
		        model.compile(optimizer=optiMi, loss=lossType, metrics=listOfMetrics+[f1])
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
		modelObj.model = model
		return modelObj


	def train(self,idforData,pmmlFile,tensorboardLogFolder,hyperParaUser,newNameFile):

		target=TrainingViewModels().trainModel

		print ('>>>>>> Step ',4)
		try:
			# train_prc = Process(target=target,args=(pmmlFile,self.pathOfData,fileName,tensorboardLogFolder,lossType,\
			# 	listOfMetrics,batchSize,epoch,idforData,problemType,scriptOutputPrepro,optimizerName,learningRate,
			# 	datHyperPara,testSize,scrDictObj))
			train_prc=Process(target=target,args=(idforData,pmmlFile,tensorboardLogFolder,hyperParaUser,newNameFile))
			train_prc.start()
		except Exception as e:
			data_details=self.upDateStatus()
			self.updateStatusWithError(data_details,'Training Failed',"Couldn't start the training process >> "+ str(e),traceback.format_exc(),self.statusFile)
			return -1
		return train_prc.ident



	def trainCustomNN(self,pmmlFile,dataFolder,fileName,tensorboardLogFolder,lossType,listOfMetrics,\
		batchSize,epoch,idforData,problemType,scriptOutput,optimizerName,learningRate,datHyperPara,testSize,scrDictObj):
		print ('>>>>>> Step ',5)
		self.trainFolder=dataFolder+'/'+'train/'
		self.validationFolder=dataFolder+'/'+'validation/'

		if os.path.isdir(dataFolder):
			print ('Image Classifier 2nd time')
			# target=self.trainImageClassifierNN
		elif pathlib.Path(self.pathOfData).suffix == '.csv':
			print('Simple DNN')
			sData=pd.read_csv(dataFolder)
			print (scrDictObj)
			nData=scrDictObj['scripts'][0](sData)
			pp=self.trainSimpleDNNObj(nData,fileName,tensorboardLogFolder,lossType,listOfMetrics,\
				problemType,optimizerName,learningRate,datHyperPara,testSize,scrDictObj)
			return pp

	    ##### Split data into test and validation set for training#################################
		trainDataX,testDataX,trainDataY,testDataY=model_selection.train_test_split(data[XVar],data['target'],test_size  =testSize)
		trainDataX,trainDataY,testDataX,testDataY=np.array(trainDataX),np.array(trainDataY),np.array(testDataX),np.array(testDataY)
	    
		kerasUtilities.updateStatusOfTraining(self.statusFile,'Data split in Train validation part')

	    ##### Get script from the PMML file and save and load back#################################
		for num,sc in enumerate(self.pmmlObj['script']):
			useFor=sc.for_
			fnaMe=self.scriptFilepath+'scriptFilepathname_'+useFor+'.py'
			scripCode=sc.get_valueOf_()
			code = scripCode.lstrip('\n')
			lines = []
			code = scripCode.lstrip('\n')
			leading_spaces = len(code) - len(code.lstrip(' '))
			for line in code.split('\n'):
				lines.append(line[leading_spaces:])
			code = '\n'.join(lines)
			with open(fnaMe,'w') as k:
				k.write(code)
			if useFor=='TRAIN':
				import importlib.util
				spec=importlib.util.spec_from_file_location('preProcessing',fnaMe)
		preProcessing=spec.loader.load_module()
		# print ('>>>>>> Step ',7)
		from preProcessing import preProcessing
		def createImages(trainDataX,trainDataY,trainFolder):
			for num,(raw,label) in enumerate(zip(trainDataX,trainDataY)):
				#         print (num,label)
				labelFolder=trainFolder+label+'/'
				try:
					os.mkdir(labelFolder)
				except:
					pass
				namofFile=labelFolder+'id_'+str(num).zfill(8)+'.png'

				imgFile=preProcessing(raw)
				imgFile.save(namofFile)
				# plt.clf()
				# plt.close()
			return 'done'

		kerasUtilities.updateStatusOfTraining(self.statusFile,'Script saved and loaded')

		modelObj = self.generateAndCompileModel(lossType,optimizerName,learningRate,listOfMetrics)
		if modelObj.__class__.__name__ == 'dict':
			return
		model = modelObj.model

	    ##### Crate images and set them for training#################################
		try:
			createImages(trainDataX,trainDataY,self.trainFolder)
			createImages(testDataX,testDataY,self.validationFolder)
		except Exception as e:
			data_details=self.upDateStatus()
			self.updateStatusWithError(data_details,'Training Failed','Error while generating the images >> '+ str(e),traceback.format_exc(),self.statusFile) 
			return

		os.remove(fnaMe)

		kerasUtilities.updateStatusOfTraining(self.statusFile,'Image writing completed')

		img_height, img_width=modelObj.image_input.shape.as_list()[1:3]
		try:
			tGen,vGen,nClass=self.kerasDataPrep(dataFolder,batchSize,img_height,img_width)
		except Exception as e:
			data_details=self.upDateStatus()
			self.updateStatusWithError(data_details,'Training Failed','Error while generating data for Keras >> '+ str(e),traceback.format_exc(),self.statusFile)
			sys.exit()

		tensor_board = self.startTensorBoard(tensorboardLogFolder)
		kerasUtilities.updateStatusOfTraining(self.statusFile,'Training Started')
		try:
			import tensorflow as tf
			with tf.device(gpuCPUSelect(selDev)):
				model.fit_generator(tGen,steps_per_epoch=stepsPerEpoch,epochs=epoch,validation_data=vGen,callbacks=[tensor_board])
		except Exception as e:
			data_details=self.upDateStatus()
			self.updateStatusWithError(data_details,'Training Failed','There is a problem with training parameters >> '+ str(e),traceback.format_exc(),self.statusFile)
			return

		kerasUtilities.updateStatusOfTraining(self.statusFile,'Training Completed')

		predictedClass=list(tGen.class_indices.keys())
		returnVal=self.writePMML(model, predictedClass, fileName, 'image')
		if returnVal == -1:
			return

		kerasUtilities.updateStatusOfTraining(self.statusFile,'PMML file Successfully Saved')

		return 'Success'



	def trainSimpleDNN(self,pmmlFile,dataFolder,fileName,tensorboardLogFolder,lossType,listOfMetrics,\
		batchSize,epoch,idforData,problemType,scriptOutput,optimizerName,learningRate,datHyperPara,testSize,scriptObj):
		print(">>>>>>>>>>>>>>SimpleDNN")
		print('pathofdata>>>>>',self.pathOfData)
		predictedClass=None
		if self.pathOfData is not None:
			targetColumnName = 'target'
			try:
				df = pd.read_csv(self.pathOfData)
				pp=self.trainSimpleDNNObj(self,dataObj,fileName,tensorboardLogFolder,lossType,listOfMetrics,\
					problemType,optimizerName,learningRate,datHyperPara,testSize,scriptObj)
				return pp
			except Exception as e:
				data_details=self.upDateStatus()
				self.updateStatusWithError(data_details,'Training Failed','Error while reading the csv file >> '+ str(e),traceback.format_exc(),self.statusFile)
				return -1


	def trainSimpleDNNObj(self,dataObj,fileName,tensorboardLogFolder,lossType,listOfMetrics,\
			problemType,optimizerName,learningRate,datHyperPara,testSize,scriptObj):
			print(">>>>>>>>>>>>>>SimpleDNN")
			print('pathofdata>>>>>',self.pathOfData)
			predictedClass=None
			targetColumnName = 'target'
			df = dataObj
			indevar=list(df.columns)
			indevar.remove('target')
			targetCol = df[targetColumnName]
			if problemType=='classification':
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

			modelObj = self.generateAndCompileModel(lossType,optimizerName,learningRate,listOfMetrics)
			if modelObj.__class__.__name__ == 'dict':
				return
			model = modelObj.model
			tensor_board = self.startTensorBoard(tensorboardLogFolder)

			##### Train model#################################
			kerasUtilities.updateStatusOfTraining(self.statusFile,'Training Started')

			try:
				import tensorflow as tf
				with tf.device(gpuCPUSelect(selDev)):
					model.fit(x=trainDataX, y=trainDataY, epochs=datHyperPara['epoch'], callbacks=[tensor_board],\
						validation_data=(testDataX, testDataY), steps_per_epoch=stepsPerEpochT, validation_steps=stepsPerEpochV)
			except Exception as e:
				data_details=self.upDateStatus()
				self.updateStatusWithError(data_details,'Training Failed','Error while fitting data to Keras Model >> '+ str(e),traceback.format_exc(),self.statusFile)
				return

			kerasUtilities.updateStatusOfTraining(self.statusFile,'Training Completed')
			try:
				toExportDict={
				'model1':{'data':self.pathOfData,'hyperparameters':datHyperPara,
						'preProcessingScript':scriptObj,
							'pipelineObj':None,'modelObj':model,
							'featuresUsed':indevar,
							'targetName':'target','postProcessingScript':None,'taskType': 'trainAndscore',
						'predictedClasses':predictedClass,'dataSet':None}
							}
				from nyokaBase.skl.skl_to_pmml import model_to_pmml
				model_to_pmml(toExportDict, PMMLFileName=fileName)
				kerasUtilities.updateStatusOfTraining(self.statusFile,'PMML file Successfully Saved')
				return 'Success'
			except Exception as e:
				data_details=self.upDateStatus()
				self.updateStatusWithError(data_details,'Saving File Failed',' '+ str(e),traceback.format_exc(),self.statusFile)
				return -1
