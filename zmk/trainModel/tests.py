# from django.test import TestCase
import unittest
import requests, os, json, sys
from django.http import JsonResponse
from trainModel.training import Training
from utility.utilityClass import Utility
import logging

class TestTrainModel(unittest.TestCase):

	@classmethod
	def setUpClass(self):
		logging.info("******* Running Test Cases for TrainModel Class *******")

	def test_1_runningTasksList(self):
		logging.info("Test Case : Get all running tasks.")
		result = Utility.runningTaskList()
		self.assertEqual(result.status_code,200)
		self.assertEqual('runningTask' in json.loads(result.__dict__['_container'][0]), True)
		self.assertEqual(len(json.loads(result.__dict__['_container'][0])['runningTask']),0)
		logging.info("PASSED")


	def test_2_statusOfRunningTask(self):
		logging.info("Test Case : Get status of a running tasks.")
		idforData = 'id'
		self.assertRaises(FileNotFoundError, Training.statusOfModel, idforData)
		logging.info("PASSED")


	def test_3_deleteARunningTask(self):
		logging.info("Test Case : Deleting a running tasks.")
		idforData = 'id'
		result = Utility.deleteTaskfromMemory(idforData)
		self.assertEqual('idforData' in json.loads(result.__dict__['_container'][0]), True)
		self.assertEqual('message' in json.loads(result.__dict__['_container'][0]), True)
		self.assertEqual(json.loads(result.__dict__['_container'][0])['idforData'], 'id')
		self.assertEqual(json.loads(result.__dict__['_container'][0])['message'], 'Something went wrong. Please contact Admin')
		logging.info("PASSED")


	def test_4_AutoMLSendData(self):
		logging.info("Test Case : Send data for AutoML.")
		filePath = os.path.abspath('testUseCase/supportdata/mpg_data_example2.csv')
		result = Training.autoMLdataprocess(filePath)
		self.assertEqual('idforData' in json.loads(result.__dict__['_container'][0]), True)
		logging.info("PASSED")


	def test_5_AutoMLTrain(self):
		logging.info("Test Case : Perform preprocessing and train AutoML model.")
		filePath = os.path.abspath('testUseCase/supportdata/mpg_data_example2.csv')
		result = Training.autoMLdataprocess(filePath)
		tempa = json.loads(result.__dict__['_container'][0])
		newPMMLFileName = 'xyz.pmml'
		target_variable = 'mpg'
		true=True
		false=False
		dataPreprocessingsteps={"data":[{"position":1,"variable":"mpg","dtype":"float64","missing_val":0,"changedataType":"Continuous","imputation_method":"None","data_transformation_step":"None","use_for_model":true},
		{"position":2,"variable":"cylinders","dtype":"int64","missing_val":0,"changedataType":"Continuous","imputation_method":"None","data_transformation_step":"None","use_for_model":true},
		{"position":3,"variable":"displacement","dtype":"float64","missing_val":0,"changedataType":"Continuous","imputation_method":"None","data_transformation_step":"None","use_for_model":true},
		{"position":4,"variable":"horsepower","dtype":"float64","missing_val":6,"changedataType":"Continuous","imputation_method":"Mean","data_transformation_step":"None","use_for_model":true},
		{"position":5,"variable":"weight","dtype":"int64","missing_val":0,"changedataType":"Continuous","imputation_method":"None","data_transformation_step":"None","use_for_model":true},
		{"position":6,"variable":"acceleration","dtype":"float64","missing_val":0,"changedataType":"Continuous","imputation_method":"None","data_transformation_step":"None","use_for_model":true},
		{"position":7,"variable":"model year","dtype":"int64","missing_val":0,"changedataType":"Categorical","imputation_method":"None","data_transformation_step":"None","use_for_model":true},
		{"position":8,"variable":"origin","dtype":"int64","missing_val":0,"changedataType":"Categorical","imputation_method":"None","data_transformation_step":"One Hot Encoding","use_for_model":true},
		{"position":9,"variable":"car name","dtype":"object","missing_val":0,"changedataType":"Categorical","imputation_method":"None","data_transformation_step":"None","use_for_model":false}
		],"problem_type":"Regression","target_variable":target_variable,"idforData":tempa['idforData'],'newPMMLFileName':newPMMLFileName,'filePath':filePath,"parameters": []
		}
		result2 = Training.autoMLtrainModel(dataPreprocessingsteps)
		result2 = json.loads(result2.__dict__['_container'][0])
		self.assertEqual('pID' in result2, True)
		self.assertEqual('status' in result2, True)
		self.assertEqual('newPMMLFileName' in result2, True)
		self.assertEqual('targetVar' in result2, True)
		self.assertEqual('problem_type' in result2, True)
		self.assertEqual('idforData' in result2, True)
		self.assertEqual(result2['status'], 'In Progress')
		self.assertEqual(result2['newPMMLFileName'], newPMMLFileName)
		self.assertEqual(result2['targetVar'], target_variable)
		self.assertEqual(result2['idforData'], tempa['idforData'])


		result = Utility.runningTaskList()
		self.assertEqual(result.status_code,200)
		self.assertEqual('runningTask' in json.loads(result.__dict__['_container'][0]), True)
		self.assertEqual(len(json.loads(result.__dict__['_container'][0])['runningTask']),1)

		idforData = tempa['idforData']
		result = Training.statusOfModel(idforData)
		self.assertEqual(result.status_code,200)
		result = json.loads(result.__dict__['_container'][0])
		self.assertEqual('pID' in result, True)
		self.assertEqual('status' in result, True)
		self.assertEqual('idforData' in result, True)

		idforData = tempa['idforData']
		result = Utility.deleteTaskfromMemory(idforData)
		self.assertEqual('idforData' in json.loads(result.__dict__['_container'][0]), True)
		self.assertEqual('message' in json.loads(result.__dict__['_container'][0]), True)
		self.assertEqual(json.loads(result.__dict__['_container'][0])['idforData'], tempa['idforData'])
		self.assertEqual(json.loads(result.__dict__['_container'][0])['message'], 'Deleted successfully')

		result = Utility.runningTaskList()
		self.assertEqual(result.status_code,200)
		self.assertEqual('runningTask' in json.loads(result.__dict__['_container'][0]), True)
		self.assertEqual(len(json.loads(result.__dict__['_container'][0])['runningTask']),0)
		logging.info("PASSED")


	def test_6_trainNNModel(self):
		logging.info("Test Case : Train NN model.")
		filePath = 'testUseCase/supportdata/irisNN.pmml'
		logFolder = 'testUseCase/supportdata/logs'
		payload={"batchSize":15,
            "epoch":10,
            "stepPerEpoch":10,
            "learningRate":0.001,
            "loss":"categorical_crossentropy",
            "metrics":["accuracy"],
            "optimizer":"Adam",
            "testSize":0.3,
            "scriptOutput":"NA",
            "problemType":"classification",
            "filePath":os.path.abspath(filePath),
            "tensorboardLogFolder":os.path.abspath(logFolder),
            "tensorboardUrl":'',
            'dataFolder':''}
		result = Training.trainNeuralNetworkModels(payload)
		result = json.loads(result.__dict__['_container'][0])
		self.assertEqual(result['pmmlFile'], filePath.split('/')[-1].replace('.pmml',''))
		self.assertEqual(result['idforData'], filePath.split('/')[-1].replace('.pmml',''))
		self.assertEqual(result['status'], 'In Progress')
		self.assertEqual('pID' in result, True)
		Utility.deleteTaskfromMemory(result['idforData'])
		logging.info("PASSED")


	def test_7_compileModel(self):
		logging.info("Test Case : Compile a model.(1)")
		filePath = 'testUseCase/supportdata/irisNN.pmml'
		from nyokaBase import PMML43Ext as ny
		pmmlObj = ny.parse(open(filePath,'r'),silence=True)
		from trainModel.mergeTrainingNN import NeuralNetworkModelTrainer
		nn = NeuralNetworkModelTrainer()
		nn.pmmlfileObj = pmmlObj
		returnVal = nn.generateAndCompileModel('mean_squared_error','adam',0.1,['accuracy','f1'],compileTestOnly=True)
		self.assertEqual('nyoka_pmml' in returnVal.__dict__, True)
		self.assertEqual('model' in returnVal.__dict__, True)
		self.assertEqual(returnVal.nyoka_pmml.__class__.__name__, 'PMML')
		self.assertEqual(returnVal.__class__.__name__,'GenerateKerasModel')


	def test_8_compileModel(self):
		logging.info("Test Case : Compile a model.(2)")
		filePath = 'testUseCase/supportdata/from_sklearn.pmml'
		from nyokaBase import PMML43Ext as ny
		pmmlObj = ny.parse(open(filePath,'r'),silence=True)
		from trainModel.mergeTrainingNN import NeuralNetworkModelTrainer
		nn = NeuralNetworkModelTrainer()
		nn.pmmlfileObj = pmmlObj
		returnVal = nn.generateAndCompileModel('mean_squared_error','adam',0.1,['accuracy','f1'],compileTestOnly=True)
		self.assertEqual('status' in returnVal, True)
		self.assertEqual('errorMessage' in returnVal, True)
		self.assertEqual('errorTraceback' in returnVal, True)
		self.assertEqual(returnVal['status'],'Model Compilation Failed')


	@classmethod
	def tearDownClass(self):
		logging.info("******* Finished Test Cases for Train Model Class *******\n")

		
