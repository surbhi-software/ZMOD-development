from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import View
import json

from datetime import datetime
from multiprocessing import Lock, Process

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view,schema

import requests, json,sys,subprocess, typing

from nyokaserver import nyokaUtilities,nyokaPMMLUtilities
# from nyokaBase import PMML43Ext as pml
from executionEngine.modelOperation import NewModelOperations,NewScoringView,NewScoringDataView,NewTrainingView,CodeExecutionFeatureCalc

class ModelOperation2View(APIView):
	http_method_names=['post','get']

	def dispatch(self,requests):
		if requests.method=='POST':
			result=self.post(requests)
		# elif requests.method=='GET':
		# 	result=self.get(requests)
		else:
			return JsonResponse({},status=405)
		return result

	# def get(self,requests):
	# 	try:
	# 		jsonData = json.loads(requests.GET['jsonRecord'])
	# 		if not jsonData:
	# 			raise Exception("Invalid Request Parameter")
	# 	except:
	# 		return JsonResponse({'error':'Invalid Request Parameter'},status=400)
	# 	return NewModelOperations().predictTestDataWithModification(None,modelName,jsonData)


	def post(self,requests):
		# print (modelName)
		try:
			filePath=requests.POST.get('filePath')
			if not filePath:
				raise Exception("Invalid Request Parameter")
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		return NewModelOperations().loadExecutionModel(filePath)

class NewScoreOperation2View(APIView):
	http_method_names=['post','get']

	def dispatch(self,requests,modelName):
		# if requests.method=='POST':
		# 	result=self.post(requests)
		if requests.method=='GET':
			result=self.get(requests,modelName)
		else:
			return JsonResponse({},status=405)
		return result

	def get(self,requests,modelName):
		print (modelName)
		try:
			jsonData = json.loads(requests.GET['jsonRecord'])
			if not jsonData:
				raise Exception("Invalid Request Parameter")
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		return NewScoringView().wrapperForNewLogic(modelName,jsonData)


class NewScoreOperation2ViewLong(APIView):
	http_method_names=['post','get']

	def dispatch(self,requests,modelName):
		# if requests.method=='POST':
		# 	result=self.post(requests)
		if requests.method=='GET':
			result=self.get(requests,modelName)
		else:
			return JsonResponse({},status=405)
		return result

	def get(self,requests,modelName):
		print (modelName)
		try:
			jsonData = json.loads(requests.GET['jsonRecord'])
			if not jsonData:
				raise Exception("Invalid Request Parameter")
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		return NewScoringDataView().scoreJsonRecordsLongProcess(modelName,jsonData)


	# def post(self,requests):
	# 	# print (modelName)
	# 	try:
	# 		filePath=requests.POST.get('filePath')
	# 		if not filePath:
	# 			raise Exception("Invalid Request Parameter")
	# 	except:
	# 		return JsonResponse({'error':'Invalid Request Parameter'},status=400)
	# 	return NewModelOperations().loadExecutionModel(filePath)

class NewTrainOperation2View(APIView):
	http_method_names=['post','get']

	def dispatch(self,requests,modelName):
		# if requests.method=='POST':
		# 	result=self.post(requests)
		if requests.method=='GET':
			result=self.get(requests,modelName)
		else:
			return JsonResponse({},status=405)
		return result

	def get(self,requests,modelName):
		print (modelName)
		return NewTrainingView().trainAllModel(modelName)



class NewCodeOperation2View(APIView):
	http_method_names=['post','get']

	def dispatch(self,requests):
		# if requests.method=='POST':
		# 	result=self.post(requests)
		if requests.method=='GET':
			result=self.get(requests)
		else:
			return JsonResponse({},status=405)
		return result

	def get(self,requests):
		filePath = requests.GET['filePath']
		return CodeExecutionFeatureCalc().loadCodeForExec(filePath)

class NewCodeExecution2View(APIView):
	http_method_names=['post','get']

	def dispatch(self,requests,scriptName):
		print ('aya idhr >>>>>>>>>>>>>>')
		if requests.method=='GET':
			result=self.get(requests,scriptName)
		# if requests.method=='GET':
		# 	result=self.get(requests)
		else:
			return JsonResponse({},status=405)
		return result

	def get(self,requests,scriptName):
		print (scriptName)
		try:
			jsonData = json.loads(requests.GET['jsonRecord'])
			if not jsonData:
				raise Exception("Invalid Request Parameter")
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		return CodeExecutionFeatureCalc().executeFeatureScript(scriptName,jsonData)