# dataUtillity.py

from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
import requests, json
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view,schema
import subprocess
from django.utils.encoding import smart_str
import os,ast, signal
from string import ascii_uppercase
from random import choice
from utility.utilityClass import RUNNING_TASK_MEMORY
from trainModel import autoMLutilities
from operator import itemgetter
# from SwaggerSchema.schemas import ( removeTaskSwagger, downloadPMMLSwaager )
global RUNNING_TASK_MEMORY

from trainModel import kerasUtilities
kerasUtilities = kerasUtilities.KerasUtilities()


import os
import datetime
import json
import cv2
import imutils
import numpy as np

import random
import shutil
from string import ascii_uppercase
from random import choice
logFolder='./logs/'
statusfileLocation = ''
noOfImagegenerated = 0

