# from django.test import TestCase
import unittest
import requests, os, json, sys, logging
from django.http import JsonResponse
from scoring.scoringClass import Scoring

class TestScoring(unittest.TestCase):

	@classmethod
	def setUpClass(self):
		logging.info("******* Running Test Cases for Scoring Class *******")

	def test_01_listOfLoadedModels(self):
		logging.info("Test Case : Get list of loaded models.")
		result = Scoring.getListOfModelinMemory()
		self.assertEqual(len(json.loads(result.__dict__['_container'][0])), 0)
		logging.info("PASSED")


	def test_02_loadModelForCorrectness(self):
		logging.info("Test Case : Load a model into memory. (1)")
		filePath = os.path.abspath('testUseCase/supportdata/NewTrialModel.pmml')
		result = Scoring.loadModelfile(filePath)
		self.assertEqual(result.status_code, 200)
		self.assertEqual(json.loads(result.__dict__['_container'][0])['keytoModel'], 'NewTrialModel')
		self.assertEqual(json.loads(result.__dict__['_container'][0])['message'], 'Model loaded successfully')
		result = Scoring.getListOfModelinMemory()
		self.assertEqual(len(json.loads(result.__dict__['_container'][0])), 1)
		logging.info("PASSED")


	def test_03_loadModelForError(self):
		logging.info("Test Case : Load a model into memory. (2)")
		filePath = os.path.abspath('testUseCase/supportdata/errorPmml.pmml')
		result = Scoring.loadModelfile(filePath)
		self.assertEqual(result.status_code, 500)
		self.assertEqual(json.loads(result.__dict__['_container'][0])['keytoModel'], None)
		self.assertEqual(json.loads(result.__dict__['_container'][0])['message'], 'Model loading failed, please contact Admin')
		result = Scoring.getListOfModelinMemory()
		self.assertEqual(len(json.loads(result.__dict__['_container'][0])), 1)
		logging.info("PASSED")



	def test_04_unloadModelForError(self):
		logging.info("Test Case : Remove a loaded model from memory. (1)")
		modelName = 'id'
		result = Scoring.removeModelfromMemory(modelName)
		self.assertEqual(result.status_code, 500)
		self.assertEqual('message' in json.loads(result.__dict__['_container'][0]), True)
		self.assertEqual(json.loads(result.__dict__['_container'][0])['message'], 'Not able to locate, make sure the model was loaded')
		result = Scoring.getListOfModelinMemory()
		self.assertEqual(len(json.loads(result.__dict__['_container'][0])), 1)
		logging.info("PASSED")


	def test_05_unloadModelForCorrectness(self):
		logging.info("Test Case : Remove a loaded model from memory. (2)")
		modelName = 'NewTrialModel'
		result = Scoring.removeModelfromMemory(modelName)
		self.assertEqual(result.status_code, 200)
		self.assertEqual('message' in json.loads(result.__dict__['_container'][0]), True)
		self.assertEqual(json.loads(result.__dict__['_container'][0])['message'], 'Model unloaded successfully, now it will not be available for predictions.')
		result = Scoring.getListOfModelinMemory()
		self.assertEqual(len(json.loads(result.__dict__['_container'][0])), 0)
		logging.info("PASSED")



	def test_06_scoreCsvDataWithNN(self):
		logging.info("Test Case : Score csv data with NN model.")
		filePath = os.path.abspath('testUseCase/supportdata/irisNN.pmml')
		result = Scoring.loadModelfile(filePath)
		modelName = 'irisNN'
		filePath = os.path.abspath('testUseCase/supportdata/iris_test.csv')
		result = Scoring.predicttestdata(filePath,modelName)
		result = json.loads(result.__dict__['_container'][0])
		self.assertEqual('result' in result, True)
		self.assertEqual(result['result'].endswith('.txt'), True)
		logging.info("PASSED")



	def test_07_scoreCsvDataWithSKL(self):
		logging.info("Test Case : Score csv data with SKL model.")
		filePath = os.path.abspath('testUseCase/supportdata/irisSKL.pmml')
		result = Scoring.loadModelfile(filePath)
		modelName = 'irisSKL'
		filePath = os.path.abspath('testUseCase/supportdata/iris_test.csv')
		result = Scoring.predicttestdata(filePath,modelName)
		result = json.loads(result.__dict__['_container'][0])
		self.assertEqual('result' in result, True)
		self.assertEqual(result['result'].endswith('.csv'), True)
		logging.info("PASSED")



	def test_08_scoreJsonDataWithSKL(self):
		logging.info("Test Case : Score json data with SKL model.")
		filePath = os.path.abspath('testUseCase/supportdata/irisSKL.pmml')
		result = Scoring.loadModelfile(filePath)
		modelName = 'irisSKL'
		filePath = os.path.abspath('testUseCase/supportdata/iris_test.json')
		result = Scoring.predicttestdata(filePath,modelName)
		result = json.loads(result.__dict__['_container'][0])
		self.assertEqual('result' in result, True)
		self.assertEqual(result['result'].endswith('.txt'), True)
		logging.info("PASSED")



	def test_09_scoreJsonDataWithNN(self):
		logging.info("Test Case : Score json data with NN model.")
		filePath = os.path.abspath('testUseCase/supportdata/irisNN.pmml')
		result = Scoring.loadModelfile(filePath)
		modelName = 'irisNN'
		filePath = os.path.abspath('testUseCase/supportdata/iris_test.json')
		result = Scoring.predicttestdata(filePath,modelName)
		result = json.loads(result.__dict__['_container'][0])
		self.assertEqual('result' in result, True)
		self.assertEqual(result['result'].endswith('.txt'), True)
		logging.info("PASSED")
		

	def test_10_scoreSignleRecordWithNN(self):
		logging.info("Test Case : Score single record with NN model.")
		filePath = os.path.abspath('testUseCase/supportdata/irisNN.pmml')
		result = Scoring.loadModelfile(filePath)

		modelName = 'irisNN'
		data = json.loads('{"sepal_length":4,"sepal_width":5,"petal_length":3,"petal_width":5}')
		result = Scoring.predicttestdata(None,modelName,data)
		result = json.loads(result.__dict__['_container'][0])
		self.assertEqual('result' in result, True)
		self.assertEqual(result['result'].endswith('.txt'), True)
		logging.info("PASSED")


	def test_11_scoreSignleRecordWithSKL(self):
		logging.info("Test Case : Score single record with SKL model.")
		filePath = os.path.abspath('testUseCase/supportdata/irisSKL.pmml')
		result = Scoring.loadModelfile(filePath)

		modelName = 'irisSKL'
		data = json.loads('{"sepal_length":4,"sepal_width":5,"petal_length":3,"petal_width":5}')
		result = Scoring.predicttestdata(None,modelName,data)
		result = json.loads(result.__dict__['_container'][0])
		self.assertEqual('result' in result, True)
		self.assertEqual(result['result'].endswith('.txt'), True)
		logging.info("PASSED")


	@classmethod
	def tearDownClass(self):
		logging.info("******* Finished Test Cases for Scoring Class *******\n")

	
