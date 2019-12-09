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
from scoring.scoringClass import Scoring,NewScoringView
from trainModel.mergeTrainingV2 import NewModelOperations



class ModelsView(APIView):
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
		return Scoring.getListOfModelinMemory()

	def post(self,requests):
		try:
			filePath=requests.POST.get('filePath')
			idfordata=requests.POST.get('idforData')
			if not filePath:
				raise Exception("Invalid Request Parameter")
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		print('filpath >>>>>>>>>>>>>>>> ',filePath)
		return NewModelOperations().loadExecutionModel(filePath)
		# return Scoring().loadModelfile(filePath,idfordata)


class ModelOperationView(APIView):
	http_method_names=['delete']

	def dispatch(self,requests,modelName):
		if requests.method=='DELETE':
			result=self.delete(requests,modelName)
		else:
			return JsonResponse({},status=405)
		return result

	def delete(self,requests,modelName):
		print('>>>>>>>>>>>>>>',modelName)
		return Scoring().removeModelfromMemory(modelName)



class ScoreView(APIView):
	http_method_names=['post','get']

	def dispatch(self,requests,modelName):
		if requests.method=='POST':
			result=self.post(requests,modelName)
		elif requests.method=='GET':
			result=self.get(requests,modelName)
		else:
			return JsonResponse({},status=405)
		return result

	def get(self,requests,modelName):
		try:
			jsonData = json.loads(requests.GET['jsonRecord'])
			if not jsonData:
				raise Exception("Invalid Request Parameter")
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		return NewScoringView().wrapperForNewLogic(modelName,jsonData,None)


	def post(self,requests,modelName):
		modelName=modelName[:-5]
		print (modelName)
		try:
			filePath=requests.POST.get('filePath')
			# print (filePath*3)
			if not filePath:
				raise Exception("Invalid Request Parameter")
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		return NewScoringView().wrapperForNewLogic(modelName,None,filePath)


# class ObjDetectionScoreView(APIView):
# 	http_method_names=['post','get']

# 	def dispatch(self,requests,modelName):
# 		if requests.method=='POST':
# 			result=self.post(requests,modelName)
# 		else:
# 			return JsonResponse({},status=405)
# 		return result

# 	def post(self,requests,modelName):
# 		try:
# 			filePath=requests.POST.get('filePath')
# 			if not filePath:
# 				raise Exception("Invalid Request Parameter")
# 		except:
# 			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
# 		return Scoring.detectObject(filePath,modelName)


			

class ScoreViewReturnJson(APIView):
	http_method_names=['get']

	def dispatch(self,requests,modelName):
		if requests.method=='POST':
			result=self.post(requests,modelName)
		elif requests.method=='GET':
			result=self.get(requests,modelName)
		else:
			return JsonResponse({},status=405)
		return result

	def get(self,requests,modelName):
		try:
			jsonData = json.loads(requests.GET['jsonRecord'])
			if not jsonData:
				raise Exception("Invalid Request Parameter")
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		return Scoring().predictTestDataWithModificationReturnJson(None,modelName,jsonData)
