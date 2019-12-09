# from django.test import TestCase
import unittest
import requests, os, json,sys
from django.http import JsonResponse
from utility.utilityClass import Utility
import logging

class TestUtility(unittest.TestCase):

	@classmethod
	def setUpClass(self):
		logging.info("******* Running Test Cases for Utility Class *******")


	def test_1_downloadJSONFile(self):
		logging.info("Test Case : Test download file for json file.")
		content = {'content':'This is a Test File'}
		with open('testUseCase/supportdata/test.json','w') as ff:
			ff.write(json.dumps(content))
		
		filePath = os.path.abspath('testUseCase/supportdata/test.json')
		
		result = Utility.downloadPMML(filePath)
		self.assertEqual(result.status_code, 200)
		self.assertEqual(json.loads(result.__dict__['_container'][0])['content'],'This is a Test File')
		self.assertEqual(result.__dict__['_headers']['content-type'][1], 'application/json')
		os.remove('testUseCase/supportdata/test.json')
		logging.info("PASSED")


	def test_2_downloadCSVFile(self):
		logging.info("Test Case : Test download file for csv file.")
		with open('testUseCase/supportdata/test.csv','w') as ff:
			ff.write('This,is,a,Test,File')
		
		filePath = os.path.abspath('testUseCase/supportdata/test.csv')
		
		result = Utility.downloadPMML(filePath)
		self.assertEqual(result.status_code, 200)
		self.assertEqual(result.__dict__['_container'][0].decode('utf-8'),'This,is,a,Test,File')
		self.assertEqual(result.__dict__['_headers']['content-type'][1], 'text/csv')
		os.remove('testUseCase/supportdata/test.csv')
		logging.info("PASSED")


	def test_3_downloadPMMLFile(self):
		logging.info("Test Case : Test download file for pmml file.")
		with open('testUseCase/supportdata/test.pmml','w') as ff:
			ff.write('<?xml version="1.0" encoding="UTF-8"?>')

		filePath = os.path.abspath('testUseCase/supportdata/test.pmml')
		result = Utility.downloadPMML(filePath)
		self.assertEqual(result.status_code, 200)
		self.assertEqual(result.__dict__['_container'][0].decode('utf-8'),'<?xml version="1.0" encoding="UTF-8"?>')
		self.assertEqual(result.__dict__['_headers']['content-type'][1], 'application/xml')
		os.remove('testUseCase/supportdata/test.pmml')
		logging.info("PASSED")

	
	@classmethod
	def tearDownClass(self):
		logging.info("******* Finished Test Cases for Utility Class *******\n")