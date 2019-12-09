
import sys
sys.path.insert(0,'.')



import numpy as np
import keras
import tensorflow as tf
from  keras.utils import multi_gpu_model 
from keras import models
from keras import layers,optimizers
from keras import applications
import json,os,requests



list_of_models = [
    applications.MobileNet(weights = "imagenet", include_top=False,input_shape = (224, 224, 3)),
    applications.InceptionV3(weights = "imagenet", include_top=False,input_shape = (224, 224, 3)),
    applications.ResNet50(weights = "imagenet", include_top=False,input_shape = (224, 224, 3)),
]


def loadModelToZmk(filePath):
    url='http://localhost:8000/api/v1/models'
    param={'filePath':filePath}
    res=requests.post(url,param)
    res=json.loads(res.text)
    return res

for model in list_of_models:
    print('\n:::::::::::Test for ',model.name,' :::::::::::::::::::\n\n')
    x = model.output
    x = layers.Flatten()(x)
    x = layers.Dense(1024, activation="relu")(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(1024, activation="relu")(x)
    predictions = layers.Dense(2, activation="softmax")(x)
    model_final = models.Model(input = model.input, output = predictions)
    model_final.compile(loss = "binary_crossentropy", optimizer = optimizers.SGD(lr=0.0001, momentum=0.9), metrics=["accuracy"])

    print('>>>> Model created')

    from nyokaBase.keras import pmml_to_keras_model as PMMLK
    from nyokaBase.keras import keras_model_to_pmml as KPMML

    path = os.getcwd()
    path = path +'/'+'testUseCase/expandable/' +(model.name).replace('.','_')+'.pmml'
    print (path)


    pmmlObj=KPMML.KerasToPmml(model_final,dataSet='image')
    pmmlObj.export(open(path,'w'),0)

    print('>>>> PMML generated')


    resp=loadModelToZmk(path)
    print(resp)
    if not resp['keytoModel']:
        print('>>>> Model load failed')
        continue
    print('>>>> Model load successful')

    from nyokaBase.keras import pmml_to_keras_model as PMMLK
    import nyokaBase.PMML43Ext as nyc

    newpmmlObj=nyc.parse(path,silence=True)
    newpmmlModel=PMMLK.GenerateKerasModel(newpmmlObj)

    print('>>>> Model reconstruction success')

    newModel=newpmmlModel.model

    mLayers=model_final.layers
    mLayers2=newModel.layers

    weightsInfo = []
    from tqdm import tqdm
    for mL,mL2 in tqdm(zip(mLayers,mLayers2)):
        tp=mL.get_weights()
        tp2=mL2.get_weights()
        try:
            weightsInfo.append(not sum(np.ravel(tp)==np.ravel(tp2))==len(np.ravel(tp)))
        except:
            weightsInfo.append(not sum(np.ravel(tp[0])==np.ravel(tp2[0]))==len(np.ravel(tp[0])))
            weightsInfo.append(not sum(np.ravel(tp[1])==np.ravel(tp2[1]))==len(np.ravel(tp[1])))

    print('>>>>Number of mismatched layerWeights : ',sum(weightsInfo),)