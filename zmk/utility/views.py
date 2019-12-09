from django.shortcuts import render

# Create your views here.
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
from nyokaBase import PMML43Ext as pml

from utility.utilityClass import Utility
from django.template import Context, loader


from utility.codeUtilityClass import CodeUtilityClass


class CodeUtilityView(APIView):
	http_method_names=['get','post']

	def dispatch(self,requests):
		if requests.method=='GET':
			result=self.get(requests)
		elif requests.method=='POST':
			result=self.post(requests)
		return result

	def post(self,requests):
		filePath = json.loads(requests.body)['filePath']
		print (filePath)
		params=[]
		return CodeUtilityClass.executeCode(filePath,params)

class CodeUtilityView2View(APIView):
	http_method_names=['post','get']

	def dispatch(self,requests,scriptName):
		if requests.method=='POST':
			result=self.post(requests,scriptName)
		# if requests.method=='GET':
		# 	result=self.get(requests)
		else:
			return JsonResponse({},status=405)
		return result

	def post(self,requests,scriptName):
		try:
			jsonData = json.loads(requests.body)['jsonRecord']
			if not jsonData:
				raise Exception("Invalid Request Parameter")
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		return CodeUtilityClass().executeFeatureScript(scriptName,jsonData)

class SwaggerView(APIView):
	http_method_names=['get']

	def dispatch(self,requests):
		if requests.method in ['GET','HEAD']:
			result=self.get(requests)
		return result

	def get(self,request):
		# template = loader.get_template("index.html")
		return render(request, 'index.html')
		# return HttpResponse(template.render())


class SwaggerUtilityView(APIView):
	http_method_names=['get']

	def dispatch(self,requests):
		if requests.method in ['GET','HEAD']:
			result=self.get(requests)
		return result
		
	def get(self,requests):
		import json
		ff = json.load(open('./settingFiles/swagger.json','r'))
		return JsonResponse(ff, status=200)


class UtilityView(APIView):
	http_method_names=['get','post']

	def dispatch(self,requests):
		if requests.method=='GET':
			result=self.get(requests)
		elif requests.method=='POST':
			result=self.post(requests)
		else:
			return JsonResponse({},status=405)
		return result

	def post(self,requests):
		try:
			oldFile = requests.POST.get('oldFilePath')
			if not oldFile:
				raise Exception("Invalid Request Parameter")
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)

		try:
			newFile = requests.POST.get('newFilePath')
		except:
			newFile = None
		return Utility.convertZMKtoZS(oldFile,newFile)

	def get(self,requests):
		try:
			filePath=requests.GET['filePath']
			if not filePath:
				raise Exception("Invalid Request Parameter")
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		
		return Utility.downloadPMML(filePath)





class ImageGeneratorUtilityView(APIView):

	http_method_names = ['post']

	def post(self,requests):
		userInput=requests.body
		try:
			userInput=json.loads(userInput)
		except:
			return JsonResponse({'error':'Invalid Request Parameter'},status=400)
		dataGen = DataGenerationUtility()
		return dataGen.generateImage(userInput)