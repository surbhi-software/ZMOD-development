
import sys
sys.path.insert(0,'.')

import pandas as pd
import keras
import numpy as np
import pandas
from keras.models import Sequential
from keras.layers import Dense
from sklearn.pipeline import Pipeline
from keras.models import Model
from keras.layers import *
import json, requests, os


def loadModelToZmk(filePath):
    url='http://localhost:8000/api/v1/models'
    param={'filePath':filePath}
    res=requests.post(url,param)
    res=json.loads(res.text)
    return res

print('\n:::::::::::Test for Simple DNN :::::::::::::::::::\n\n')
path = os.getcwd()+'/'+'testUseCase/supportdata/' 

data=pd.read_csv(path+'mpg_data_example.csv')
data = data.drop(['car name'],axis=1)
cola=data.columns
X=cola[:-1]
Y=cola[-1]

data=data.fillna(0)

inp= Input(shape=(7,))
x= Dense(50,activation='relu')(inp)
predictions = Dense(1, activation="relu")(x)
model = Model(input = inp, output = predictions)
model.compile(loss='mean_squared_error', optimizer='adam')

print('\n>>>> Model created\n')

model.fit(data[X].values,data[Y].values)


from nyokaBase.keras import keras_model_to_pmml as KPMML
pmmlObj=KPMML.KerasToPmml(model,0)

path2= os.getcwd()+'/'+'testUseCase/expandable/' +'simpleDNN.pmml'

pmmlObj.export(open(path2,'w'),0)

print('\n>>>> PMML generated\n')


resp=loadModelToZmk(path2)
print(resp)
if not resp['keytoModel']:
    print('\n>>>> Model load failed\n')
    import sys
    sys.exit(1)
print('\n>>>> Model load successful\n')

from nyokaBase.keras import pmml_to_keras_model as PMMLK
import nyokaBase.PMML43Ext as nyc

newpmmlObj=nyc.parse(path2,silence=True)

newpmmlModel=PMMLK.GenerateKerasModel(newpmmlObj)

print('\n>>>> Model reconstruction success\n')

newpmmlModel=newpmmlModel.model

mLayers=model.layers
mLayers2=newpmmlModel.layers

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
print('\n>>>>Number of mismatched layerWeights : ',sum(weightsInfo),'\n')