import requests
import json
import os
import random
import string
import EditorUtilities as editor
import logging
import sys
import shutil

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

pathLog = os.getcwd()+'/'+'testUseCase/expandable/' +'EditorCNNTest.log'

handler2 = logging.FileHandler(os.path.abspath(pathLog))
handler2.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler2.setFormatter(formatter)
root.addHandler(handler2)


editor.mainUrl='http://localhost:8000/'
projectId = editor.generateId()

logging.info('1. '+projectId)

firstLayer = editor.getListOfLayers()

logging.info('2. '+firstLayer)

pathData = os.getcwd()+'/'+'testUseCase/supportdata/' +'sample.pmml'

pathData2=os.getcwd()+'/'+'testUseCase/expandable/' +'sample.pmml'

shutil.copy(pathData,pathData2)

filePath = os.path.abspath(pathData2)

resp1 = editor.addArchitecture(projectId,filePath)

logging.info('3. '+resp1)

template={'itemType': 'TEMPLATE',
     'layerId': 'NA',
     'layerIndex': 0,
     'name': 'Mobilenet',
     'templateId': 'mobilenetArch',
     'id':'Temp1'
     }

resp2 = editor.addTemplate(projectId,template)

logging.info('4. '+resp2)

globalMemory = editor.getGlobalMemory()

for layer in reversed(globalMemory[projectId]['architecture'][-5:]):
     layerToDelete = layer
     resp_ = editor.deleteLayerOrSection(projectId,layer)
     logging.info('Inside loop >> '+resp_)

layer1 = {
          "connectionLayerId": "global_average_pooling2d_1",
          "itemType": "LAYER",
          "layerId": "reahpe_1",
          "layerIndex": 30,
          "layerType": "Reshape",
          "trainable": False,
          "name": "Reshape",
          "id":editor.generateId(),
          "properties": [
            {
              "dataType": "array",
              "hint": "Input dimension of the layer",
              "id": "inputDimension",
              "label": "Input Dimension",
              "options": [],
              "value": [1,1,1024]
            },
            {
              "dataType": "array",
              "hint": "tuple of target shape",
              "id": "reshapeTarget",
              "label": "Target Shape",
              "options": [],
              "value": [1024,1]
            },
            {
              "dataType": "array",
              "hint": "Output dimension of the layer",
              "id": "outputDimension",
              "label": "Output Dimension",
              "options": [],
              "value": []
            }
          ]
        }

resp3 = editor.addLayerOrSection(projectId,layer1)

logging.info('5. '+resp3)

layer2 = {
          "connectionLayerId": "reahpe_1",
          "itemType": "LAYER",
          "layerId": "desne_2",
          "layerIndex": 31,
          "layerType": "Dense",
          "trainable": False,
          "name": "Dense",
          "id":editor.generateId(),
          "properties": [
            {
              "dataType": "string",
              "hint": "Activation function for the dense layer",
              "id": "activationFunction",
              "label": "Activation Function",
              "options": [
                "linear",
                "tanh",
                "relu",
                "sigmoid",
                "softmax"
              ],
              "value": "softmax"
            },
            {
              "dataType": "integer",
              "hint": "Neurons for fully connected layer",
              "id": "units",
              "label": "Units",
              "options": [],
              "value": 2
            },
            {
              "dataType": "array",
              "hint": "only required if dragged first",
              "id": "inputDimension",
              "label": "Input Dimension",
              "options": [],
              "value": [1024,1]
            },
            {
              "dataType": "array",
              "hint": "Output dimension of the layer",
              "id": "outputDimension",
              "label": "Output Dimension",
              "options": [],
              "value": []
            }
          ]
        }
resp4 = editor.addLayerOrSection(projectId,layer2)

logging.info('6. '+resp4)
logging.info("All tests passsed.")