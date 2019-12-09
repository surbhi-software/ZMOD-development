# autoML.py
from sklearn import ensemble,preprocessing,linear_model,tree
from sklearn.pipeline import Pipeline
from sklearn_pandas import DataFrameMapper
import os,json

settingFilePath='settingFiles/'
pathOfStatus='resultStatus/'
SavedModels='SavedModels/'
logFolder='./logs/'

algorithms={
    'Regression': ['All','ExtraTreeRegressor','GradientBoostingRegressor','DecisionTreeRegressor','LinearSVR',\
        'RandomForestRegressor','XGBRegressor','KNeighborsRegressor','LinearRegression','LGBMRegressor'],
    'Classification': ['All','DecisionTreeClassifier','ExtraTreesClassifier','RandomForestClassifier','GradientBoostingClassifier',\
        'KNeighborsClassifier','LinearSVC','LogisticRegression','XGBClassifier','LGBMClassifier'],
    'Anomaly':['IsolationForest','OneClassSVM']
}


optionsForDropdown={
      "changedataTypes": ['None',"Continuous", "Categorical"],
      "imputation_methods": ['None',"Mean", "Median", "Mode"],# "Back fill", "Forward fill"],
      "data_transformation_steps": ["None", "One Hot Encoding", "Label Encoding", "Normalize", "Scaling Standard", "Scaling Min Max", "Scaling Max Absolute"],
      "algorithmTypes":algorithms,
    }

processe_short={'Mean':preprocessing.Imputer(strategy="mean"),
    'Median':preprocessing.Imputer(strategy="median"),
    'Mode':preprocessing.Imputer(strategy="mode"),
    'Scaling Min Max':preprocessing.MinMaxScaler(),
    'Scaling Standard':preprocessing.StandardScaler(),
    'Label Encoding':preprocessing.LabelEncoder(),
    'One Hot Encoding':preprocessing.LabelBinarizer(),
    'Normalize':preprocessing.StandardScaler(),
    'Scaling Max Absolute':preprocessing.MinMaxScaler(),}

class AutoMLUtilities:


    def dataDescription(self,data):
        dataDtype=dict(data.dtypes)
        dataMissingVal=dict(data.isnull().sum())
        dataDetail=[]
        for num,j in enumerate(data.columns):
            tempK={}
            tempK['position']=num+1
            tempK['variable']=j
            tempK['dtype']=str(dataDtype[j])
            tempK['missing_val']=int(dataMissingVal[j])
            if tempK['dtype'] in ['int64','float32','float64']:
            	tempK['changedataType']='Continuous'
            else:
            	tempK['changedataType']='Categorical'
            tempK['imputation_method']='None'
            tempK['data_transformation_step']='None'
            tempK['use_for_model']=True
            dataDetail.append(tempK)
        datatoSend={'data':dataDetail,'options':optionsForDropdown}
        return datatoSend


    def createDataMapper(self,dataPreprocessingsteps,targetVar):
        dataMapperInner=[]
        for stepin in dataPreprocessingsteps:
            tempMappercol=[]
            tempMapperProcess=[]
            if (stepin['use_for_model']==True) & (stepin['variable']!=targetVar):
                tempMappercol.append(stepin['variable'])
                if stepin['imputation_method']!='None':
                    tempMapperProcess.append(processe_short[stepin['imputation_method']])
                if stepin['data_transformation_step']!='None':
                    tempMapperProcess.append(processe_short[stepin['data_transformation_step']])
                if (stepin['data_transformation_step']=='None') & (stepin['imputation_method']=='None'):
                    tempMapperProcess.append(preprocessing.Imputer())
                dataMapperInner.append(tuple([tempMappercol,tempMapperProcess]))

        # print ('$$$$$$$$$$$$$$$',dataMapperInner)
                
        return dataMapperInner

    def createModelData(self,data,mapper1,targetVar):
        pipeline = Pipeline([('feature_mapper', mapper1)])
        dataX=pipeline.fit_transform(data)
        if targetVar is not None:
            targetY=data[targetVar]
            return dataX,targetY
        else:
            return dataX,None


    def progressOfModel(self,logFolder,idforData):
        # print ('Came here')
        projectName=idforData
        projectPath=logFolder+projectName
        tpotFolder=projectPath+'/tpotFolder/'
        listOffiles=os.listdir(tpotFolder)
        overallList=[]
        for num,j in enumerate(listOffiles):
            # print('num in listofFiles',num)
            xx=open(tpotFolder+j,'r')
            genData=xx.read()
            pp=[k for k in genData.split('\n') if 'CV score on the training set was' in k ]
            ll=pp[0].split()[-1].split(':')[-1]
            overallList.append({'modelName':'Generation '+str(num+1),'score':str(ll)})
        print (overallList)
        return overallList

    def readStatusFile(self,projectName):
        projectPath=logFolder+projectName+'/'
        try:
            dataFolder=projectPath+'/dataFolder/'
            statusFile=dataFolder+'status'+'.txt'
            sFile=open(statusFile,'r')
        except:
            statusFile=projectPath+'status'+'.txt'
            # print (statusFile)
            sFile=open(statusFile,'r')
        sFileText=sFile.read()
        sFile.close()
        data_details=json.loads(sFileText)
        return data_details