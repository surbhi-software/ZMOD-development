from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_swagger import renderers
from rest_framework.schemas import SchemaGenerator
from urllib.parse import urljoin
import yaml
import coreapi


from rest_framework.decorators import renderer_classes, api_view
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
import coreapi
from rest_framework import response
# noinspection PyArgumentList


class CustomSchemaGenerator(SchemaGenerator):
    def get_link(self, path, method, callback, view):
        """Custom the coreapi using the func.__doc__ .

        if __doc__ of the function exsit, use the __doc__ building the coreapi. else use the default serializer.

        __doc__ in yaml format, eg:

        desc: the desc of this api.
        ret: when success invoked, return xxxx
        err: when error occured, return xxxx
        input:
        - name: mobile
          desc: the mobile number
          type: string
          required: true
          location: form
        - name: promotion
          desc: the activity id
          type: int
          required: true
          location: form
        """
        fields = self.get_path_fields(path, method, callback, view)
        yaml_doc = None
        func = getattr(view, view.action) if getattr(view, 'action', None) else None
        if func and func.__doc__:
            try:
                yaml_doc = yaml.load(func.__doc__)
            except:
                yaml_doc = None
        if yaml_doc and 'desc' in yaml_doc:
            desc = yaml_doc.get('desc', '')
            ret = yaml_doc.get('ret', '')
            err = yaml_doc.get('err', '')
            _method_desc = desc + '<br>' + 'return: ' + ret + '<br>' + 'error: ' + err
            params = yaml_doc.get('input', [])
            for i in params:
                _name = i.get('name')
                _desc = i.get('desc')
                _required = i.get('required', True)
                _type = i.get('type', 'string')
                _location = i.get('location', 'form')
                field = coreapi.Field(
                    name=_name,
                    location=_location,
                    required=_required,
                    description=_desc,
                    type=_type
                )
                fields.append(field)
        else:
            _method_desc = func.__doc__ if func and func.__doc__ else ''
            fields += self.get_serializer_fields(path, method, callback, view)
        fields += self.get_pagination_fields(path, method, callback, view)
        fields += self.get_filter_fields(path, method, callback, view)

        if fields and any([field.location in ('form', 'body') for field in fields]):
            encoding = self.get_encoding(path, method, callback, view)
        else:
            encoding = None

        if self.url and path.startswith('/'):
            path = path[1:]

        return coreapi.Link(
            url=urlparse.urljoin(self.url, path),
            action=method.lower(),
            encoding=encoding,
            fields=fields,
            description=_method_desc
        )


class SwaggerSchemaView(APIView):
    exclude_from_schema = True
    permission_classes = [AllowAny]
    renderer_classes = [
        renderers.OpenAPIRenderer,
        renderers.SwaggerUIRenderer
    ]

    def get(self, request):
        generator = CustomSchemaGenerator()
        schema = generator.get_schema(request=request)
        return Response(schema)

import coreapi,  coreschema
from rest_framework.schemas import AutoSchema,ManualSchema

autoMLsendDataSwagger = ManualSchema(fields=[coreapi.Field(name="filePath", required=True, location="formData",
														   type="string",description="filePath here")],
encoding="application/json"
)

autoMLtrainModelSwagger=ManualSchema(fields=[coreapi.Field(name="data", required=True, location="form",
														   type="array",description="list of preprocessing here",),
											 coreapi.Field(name="problem_type", required=True, location="form",
														   type="string", description="ProblemType here"),
											 coreapi.Field(name="target_variable", required=True, location="form",
														   type="string", description="target variable here"),
											 coreapi.Field(name="idforData", required=True, location="form",
														   type="string", description="idForData here"),
											 coreapi.Field(name="newPMMLFileName", required=True, location="form",
														   type="string", description="PMML file name here"),
											 coreapi.Field(name="filePath", required=True, location="form",
														   type="string", description="filePath here"),
											 coreapi.Field(name="parameters", required=True, location="form",
														   type="array",description="parameters here",)],
															encoding="application/json"
															)

statusOfModelSwagger=ManualSchema(fields=[coreapi.Field(name="idforData",required=True,location="formData",
														type="string",description="get the running status of the model")])

removeTaskSwagger=ManualSchema(fields=[coreapi.Field(name="idforData",required=True,location="formData",
														type="string",description="removes the task from the Task Lists")])

trainNeuralNetworkModelsSwagger=ManualSchema(fields=[coreapi.Field(name="pmmlFile", required=True, location="form",
														   type="string",description="path of the PMML file",),
											 coreapi.Field(name="dataFolder", required=True, location="form",
														   type="string", description="path of the data folder"),
											 coreapi.Field(name="filePath", required=True, location="form",
														   type="string", description="path of the PMML file"),
											 coreapi.Field(name="tensorboardLogFolder", required=True, location="form",
														   type="string", description="path of the log folder"),
											 coreapi.Field(name="tensorboardUrl", required=True, location="form",
														   type="string", description="usrl of the tensorboard"),
											 coreapi.Field(name="loss", required=True, location="form",
														   type="string", description="type of loss"),
											 coreapi.Field(name="learningRate", required=True, location="form",
														   type="string",description="learning rate"),
													  coreapi.Field(name="metrics", required=True, location="form",
														   type="array",description="metrics"),
													  coreapi.Field(name="batch_size", required=True, location="form",
														   type="string",description="batch size"),
													  coreapi.Field(name="epoch", required=True, location="form",
														   type="string",description="number of epochs"),
													  coreapi.Field(name="stepPerEpoch", required=True, location="form",
														   type="string",description="number of steps per epochs"),
													  coreapi.Field(name="problemType", required=True, location="form",
														   type="string",description="problem type"),
													  coreapi.Field(name="scriptOutput", required=True, location="form",
														   type="string",description="type of script output"),
													  coreapi.Field(name="testSize", required=True, location="form",
														   type="string",description="test size"),
													  coreapi.Field(name="optimizer", required=True, location="form",
														   type="string",description="optimizer"),
													  ],
encoding="application/json"
)

loadModelSwagger=ManualSchema(fields=[coreapi.Field(name="filepath",required=True,location="formData",
														type="string",description="load the model in Zementis memory")
]

)

predictTestDataSwagger=ManualSchema(fields=[coreapi.Field(name="modelName",required=True,location="formData",
														type="string",description="name of the model"),
											coreapi.Field(name="filePath",required=True,location="formData",
														  type="string",description="location of test file")
									])

unloadModelSwagger=ManualSchema(fields=[coreapi.Field(name="modelname",required=True,location="formData",
													  type="string",description="name of thye model")])

downloadPMMLSwaager=ManualSchema(fields=[coreapi.Field(name="filePath",required=True,location="formData",
													  type="string",description="enter the path of the pmml")])

addArchitectureSwagger = ManualSchema(fields=[coreapi.Field(name="projectID", required=True, location="formData",
														   type="string",description="project ID here"),
                                                           coreapi.Field(name="filePath",required=True,location="formData",
                                                           type="string",description="path of the pmml")],
encoding="application/json"
)


updateLayerSwagger=ManualSchema(fields=[coreapi.Field(name="projectID",required=True,location="form",
type="string",description="projectID here"),
coreapi.Field(name="layerToUpdate",required=True,type="object",location="form",description="layer here")],
encoding="application/json")

deleteLayerSwagger=ManualSchema(fields=[coreapi.Field(name="projectID",required=True,location="form",
type="string",description="projectID here"),
coreapi.Field(name="layerDelete",required=True,type="object",location="form",description="delete layer here")],
encoding="application/json")

getDetailsOfPMMLswagger=ManualSchema(fields=[coreapi.Field(name="filePath",required=True,location="form",
type="string",description="path of the pmml file here")],encoding="application/json")