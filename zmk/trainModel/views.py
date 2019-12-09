from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import View
from datetime import datetime
from multiprocessing import Lock, Process

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view,schema

import requests, json,sys,subprocess, typing,json

from nyokaserver import nyokaUtilities,nyokaPMMLUtilities
# from nyokaBase import PMML43Ext as pml

from trainModel.training import Training
from trainModel.mergeTrainingNN import NeuralNetworkModelTrainer
from utility.utilityClass import Utility
import coreapi,  coreschema
from rest_framework.schemas import AutoSchema,ManualSchema
from rest_framework.decorators import api_view,schema

# Create your views here.

class RunningTaskView(APIView):
	http_method_names=['get']

	def dispatch(self,requests):
		if requests.method=='GET':
			result=self.get(requests)
		else:
			return JsonResponse({},status=405)
		return result

	def get(self,requests):
		return Utility().runningTaskList()

class ModelCompileView(APIView):
	http_method_names=['post']

	def dispatch(self,requests):
		if requests.method=='POST':
			result=self.post(requests)
		else:
			return JsonResponse({},status=405)
		return result

	def post(self,requests):
		filePath = requests.POST.get('filePath')
		from nyokaBase import PMML43Ext as ny
		pmmlObj = ny.parse(open(filePath,'r'),silence=True)
		nn = NeuralNetworkModelTrainer()
		nn.pmmlfileObj = pmmlObj
		returnVal = nn.generateAndCompileModel('mean_squared_error','adam',0.1,['accuracy','f1'],compileTestOnly=True)
		if returnVal.__class__.__name__ == 'dict':
			return JsonResponse(returnVal)
		else:
			return JsonResponse({'status':'Model Compiled Successfully'},status=200)



class RunningTaskOperationView(APIView):
	http_method_names=['get','delete']

	def dispatch(self,requests,id_for_task):
		if requests.method=='GET':
			result=self.get(requests,id_for_task)
		elif requests.method=='DELETE':
			result=self.delete(requests,id_for_task)
		else:
			return JsonResponse({},status=405)
		return result

	def delete(self,requests,id_for_task):
		return Utility.deleteTaskfromMemory(id_for_task)

	def get(self,requests,id_for_task):
		return Training.statusOfModel(id_for_task)

class RunningTaskNameOperationView(APIView):
	http_method_names=['get','delete']

	def dispatch(self,requests,taskName):
		if requests.method=='GET':
			result=self.get(requests,taskName)
		elif requests.method=='DELETE':
			result=self.delete(requests,taskName)
		else:
			return JsonResponse({},status=405)
		return result

	def get(self,requests,taskName):
		return Utility().taskUpdateByTaskName(taskName)

class RunningTaskNameOperationViewIdForData(APIView):
	http_method_names=['get','delete']

	def dispatch(self,requests,taskName,idForData):
		if requests.method=='GET':
			result=self.get(requests,taskName,idForData)
		elif requests.method=='DELETE':
			result=self.delete(requests,taskName,idForData)
		else:
			return JsonResponse({},status=405)
		return result

	def get(self,requests,taskName,idForData):
		return Utility().taskUpdateByTaskNameIdForData(taskName,idForData)


class TrainAutoMLView(APIView):
	http_method_names=['get','post']

	def dispatch(self,requests):
		if requests.method=='GET':
			result=self.get(requests)
		elif requests.method=='POST':
			result=self.post(requests)
		else:
			return JsonResponse({},status=405)
		return result

	def get(self,requests):
		try:
			pathOffile=requests.GET['filePath']
			if not pathOffile:
				raise Exception("Invalid Request Parameter")
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		return Training.autoMLdataprocess(pathOffile)

	def post(self,requests):
		userInput=requests.body
		try:
			userInput=json.loads(userInput)
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		return Training.autoMLtrainModel(userInput)

class TrainAnomalyView(APIView):
	http_method_names=['post']

	def dispatch(self,requests):
		if requests.method=='GET':
			result=self.get(requests)
		elif requests.method=='POST':
			result=self.post(requests)
		else:
			return JsonResponse({},status=405)
		return result


	def post(self,requests):
		userInput=requests.body
		try:
			userInput=json.loads(userInput)
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		return Training.autoAnomalyModel(userInput)



class TrainNNView(APIView):
	http_method_names=['post']

	def dispatch(self,requests):
		if requests.method=='POST':
			result=self.post(requests)
		else:
			return JsonResponse({},status=405)
		return result

	def post(self,requests):
		try:
			requests.body
			# print (requests.POST.get('filePath'))
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		return Training.trainNeuralNetworkModels(requests)


class MRCNNView(APIView):
	http_method_names=['post']

	def dispatch(self,requests):
		if requests.method=='POST':
			result=self.post(requests)
		else:
			return JsonResponse({},status=405)
		return result

	def post(self,requests):
		userInput=requests.body
		try:
			userInput=json.loads(userInput)
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		return Training.trainMRCNN(userInput)