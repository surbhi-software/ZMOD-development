import coreapi,  coreschema
from rest_framework.schemas import AutoSchema,ManualSchema

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