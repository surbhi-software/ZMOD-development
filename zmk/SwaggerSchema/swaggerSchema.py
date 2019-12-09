from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_swagger import renderers
from rest_framework.schemas import SchemaGenerator
import yaml
import coreapi


from rest_framework.decorators import renderer_classes, api_view
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
import coreapi
from rest_framework import response
import json



@api_view()
@renderer_classes([SwaggerUIRenderer, OpenAPIRenderer])
def schema_view(request):
    schema = coreapi.Document(
    title='Zementis Modeler',
    url='http://localhost:8000',
    content={
        'Model': {
            'listOfModels': coreapi.Link(
                url='/api/v1/models',
                action='get',
                description='Get the list of loaded models.'
            ),
            'loadModel': coreapi.Link(
                url='/api/v1/models',
                action='post',
                fields=[
                    coreapi.Field(
                        name='filePath',
                        required=True,
                        location='formData',
                        description='Path of the model (PMML) to be loaded.'
                    )
                ],
                description='Loads a model into memory for scoring data.'
            ),
            'unloadModel': coreapi.Link(
                url='/api/v1/models/{modelName}',
                action='delete',
                fields=[
                    coreapi.Field(
                        name='modelName',
                        required=True,
                        location='path',
                        description='Name of the model to be unloaded.'
                    )
                ],
                description='Unloads a model from memory.'
            ),
            'scoreMultipleData': coreapi.Link(
                url='/api/v1/models/{modelName}/score',
                action='post',
                fields=[
                    coreapi.Field(
                        name='modelName',
                        required=True,
                        location='path',
                        description='Name of the loaded model to be used for scoring.'
                    ),
                    coreapi.Field(
                        name='filePath',
                        required=False,
                        location='formData',
                        description='Path of the data file to be predicted.'
                    )
                ],
                description='Prediction of multiple record data.'
            ),
            'scoreSingleData': coreapi.Link(
                url='/api/v1/models/{modelName}/score',
                action='get',
                fields=[
                    coreapi.Field(
                        name='modelName',
                        required=True,
                        location='path',
                        description='Name of the loaded model to be used for scoring.'
                    ),
                    coreapi.Field(
                        name='jsonRecord',
                        required=False,
                        location='query',
                        description='The record in json format.\nExample: {"sepal_length":5,"sepal_width":4,"petal_length":4,"petal_width":5}'
                    )
                ],
                description='Prediction of single record data.'
            )
        },
        'PMML':{
            'getDetailsOfPMML': coreapi.Link(
                url='/api/v1/pmml',
                action='get',
                fields=[
                    coreapi.Field(
                        name='filePath',
                        required=True,
                        location='query',
                        description='The path of the PMML'
                    )
                ],
                description='Returns the details of a PMML'
            ),
            'getGlobal': coreapi.Link(
                url='/api/v1/pmml/getGlobal/memory',
                action='get',
                description='Returns all available models (PMMLs) in JSON format.'
            ),
            'addArchitechToGlobalMemory': coreapi.Link(
                url='/api/v1/pmml/{projectID}',
                action='post',
                fields=[
                    coreapi.Field(
                        name='projectID',
                        required=True,
                        location='path',
                        description='Create an unique project Id for that PMML.'
                    ),
                    coreapi.Field(
                        name='filePath',
                        required=True,
                        location='formData',
                        description='Path of the PMML file.'
                    )
                ],
                description='Adds the PMML to the global memory as JSON.'
            ),
            'addOrUpdateLayer': coreapi.Link(
                url='/api/v1/pmml/{projectID}/layer',
                action='put',
                fields=[
                    coreapi.Field(
                        name='projectID',
                        required=True,
                        location='path',
                        description='Project id for the PMML model.'
                    ),
                    coreapi.Field(
                        name='layerToUpdate',
                        required=True,
                        location='body',
                        description='The JSON payload of the layer/section/template to be added/update.'
                    )
                ],
                description='For Modifying a DeepNetwork PMML. Adds or updates a layer/section/template.'
            ),
            'deleteLayer': coreapi.Link(
                url='/api/v1/pmml/{projectID}/layer',
                action='delete',
                fields=[
                    coreapi.Field(
                        name='projectID',
                        required=True,
                        location='path',
                        description='Project id for the PMML model.'
                    ),
                    coreapi.Field(
                        name='layerDelete',
                        required=True,
                        location='body',
                        description='The JSON payload of the layer/section to be deleted.'
                    )
                ],
                description='Deletes a layer/section from the PMML model.'
            )
            
        },
        'Running Tasks':{
            'runningTasksList': coreapi.Link(
                url='/api/v1/runningTasks',
                action='get',
                description='Get a list of running tasks.'
            ),
            'statusOfModel': coreapi.Link(
                url='/api/v1/runningTasks/{id_for_task}',
                action='get',
                fields=[
                    coreapi.Field(
                        name='id_for_task',
                        required=True,
                        location='path',
                        description='Id for the task.'
                    )
                ],
                description='Get the status of a running task.'
            ),
            'deleteTask': coreapi.Link(
                url='/api/v1/runningTasks/{id_for_task}',
                action='delete',
                fields=[
                    coreapi.Field(
                        name='id_for_task',
                        required=True,
                        location='path',
                        description='Id for the task'
                    )
                ],
                description='Removes a task from the running tasks list.'
            )
        },
        'Train Model':{
            'autoMLsendData': coreapi.Link(
                url='/api/v1/trainAutoMLModel',
                action='get',
                fields=[
                    coreapi.Field(
                        name='filePath',
                        required=True,
                        location='query',
                        description='Path of the data file to be uploaded'
                    )
                ],
                description='Uploads data for AutoML.'
            ),
            'trainAutoML': coreapi.Link(
                url='/api/v1/trainAutoMLModel',
                action='post',
                fields=[
                    coreapi.Field(
                        name='payload',
                        required=True,
                        location='body',
                        description='Payload for training of AutoML. (Pass the JSON payload)'
                    )
                ],
                description='For a given dataset, generates a model using AutoML.'
            ),
            'trainNNModel': coreapi.Link(
                url='/api/v1/trainNNModel',
                action='post',
                fields=[
                    coreapi.Field(
                        name='payload',
                        required=True,
                        location='body',
                        description='Payload for training of DeepNetwork Model. (Pass the JSON payload)'
                    )
                ],
                description='Trains a DeepNetwork model.'
            )
        },
        'Utility': {
            'downloadFile': coreapi.Link(
                url='/api/v1/downloadFile',
                action='get',
                fields=[
                    coreapi.Field(
                        name='filePath',
                        required=True,
                        location='query',
                        description='Path of the file to be downloaded.'
                    )
                ],
                description='Downloads a file.'
            ),
            'listOfLayers': coreapi.Link(
                url='/api/v1/listOfLayers',
                action='get',
                description='Returns a list of layers and architectures supported by Zementis Modeler.'
            )
        }

        
    }
)

    # schema = generator.get_schema(request)
    return response.Response(schema)