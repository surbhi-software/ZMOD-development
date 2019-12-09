# trainAutoML.py


from sklearn_pandas import DataFrameMapper, CategoricalImputer
import pandas as pd
import numpy as np
from sklearn import ensemble,preprocessing,linear_model,tree
from sklearn.pipeline import Pipeline
from tpot import TPOTRegressor,TPOTClassifier
from sklearn.externals import joblib
from trainModel import autoMLutilities
autoMLutilities = autoMLutilities.AutoMLUtilities()
import requests,sys,traceback,argparse,json,time,ast,operator,os

ALGORITHM_NAME_OBJ_DICT = {
    'ExtraTreeRegressor': {
        'sklearn.ensemble.ExtraTreesRegressor': {
            'n_estimators': [100],
            'max_features': np.arange(0.05, 1.01, 0.05),
            'min_samples_split': range(2, 21),
            'min_samples_leaf': range(1, 21),
            'bootstrap': [True, False]
        }
    },
    'GradientBoostingRegressor': {
        'sklearn.ensemble.GradientBoostingRegressor': {
            'n_estimators': [100],
            'loss': ["ls", "lad", "huber", "quantile"],
            'learning_rate': [1e-3, 1e-2, 1e-1, 0.5, 1.],
            'max_depth': range(1, 11),
            'min_samples_split': range(2, 21),
            'min_samples_leaf': range(1, 21),
            'subsample': np.arange(0.05, 1.01, 0.05),
            'max_features': np.arange(0.05, 1.01, 0.05),
            'alpha': [0.75, 0.8, 0.85, 0.9, 0.95, 0.99]
        }
    },
    'DecisionTreeRegressor': {
        'sklearn.tree.DecisionTreeRegressor': {
            'max_depth': range(1, 11),
            'min_samples_split': range(2, 21),
            'min_samples_leaf': range(1, 21)
        }
    },
    'LinearSVR': {
        'sklearn.svm.LinearSVR': {
            'loss': ["epsilon_insensitive", "squared_epsilon_insensitive"],
            'dual': [True, False],
            'tol': [1e-5, 1e-4, 1e-3, 1e-2, 1e-1],
            'C': [1e-4, 1e-3, 1e-2, 1e-1, 0.5, 1., 5., 10., 15., 20., 25.],
            'epsilon': [1e-4, 1e-3, 1e-2, 1e-1, 1.]
        }
    },
    'RandomForestRegressor': {
        'sklearn.ensemble.RandomForestRegressor': {
            'n_estimators': [100],
            'max_features': np.arange(0.05, 1.01, 0.05),
            'min_samples_split': range(2, 21),
            'min_samples_leaf': range(1, 21),
            'bootstrap': [True, False]
        }
    },
    'XGBRegressor': {
        'xgboost.XGBRegressor': {
            'n_estimators': [100],
            'max_depth': range(1, 11),
            'learning_rate': [1e-3, 1e-2, 1e-1, 0.5, 1.],
            'subsample': np.arange(0.05, 1.01, 0.05),
            'min_child_weight': range(1, 21),
            'nthread': [1]
        }
    },
    'DecisionTreeClassifier': {
        'sklearn.tree.DecisionTreeClassifier': {
            'criterion': ["gini", "entropy"],
            'max_depth': range(1, 11),
            'min_samples_split': range(2, 21),
            'min_samples_leaf': range(1, 21)
        }
    },
    'ExtraTreesClassifier': {
        'sklearn.ensemble.ExtraTreesClassifier': {
            'n_estimators': [100],
            'criterion': ["gini", "entropy"],
            'max_features': np.arange(0.05, 1.01, 0.05),
            'min_samples_split': range(2, 21),
            'min_samples_leaf': range(1, 21),
            'bootstrap': [True, False]
        }
    },
    'RandomForestClassifier': {
        'sklearn.ensemble.RandomForestClassifier': {
            'n_estimators': [100],
            'criterion': ["gini", "entropy"],
            'max_features': np.arange(0.05, 1.01, 0.05),
            'min_samples_split': range(2, 21),
            'min_samples_leaf':  range(1, 21),
            'bootstrap': [True, False]
        }
    },
    'GradientBoostingClassifier': {
        'sklearn.ensemble.GradientBoostingClassifier': {
            'n_estimators': [100],
            'learning_rate': [1e-3, 1e-2, 1e-1, 0.5, 1.],
            'max_depth': range(1, 11),
            'min_samples_split': range(2, 21),
            'min_samples_leaf': range(1, 21),
            'subsample': np.arange(0.05, 1.01, 0.05),
            'max_features': np.arange(0.05, 1.01, 0.05)
        }
    },
    'KNeighborsClassifier': {
        'sklearn.neighbors.KNeighborsClassifier': {
            'n_neighbors': range(1, 101),
            'weights': ["uniform", "distance"],
            'p': [1, 2]
        }
    },
    'KNeighborsRegressor': {
        'sklearn.neighbors.KNeighborsRegressor': {
            'n_neighbors': range(1, 101),
            'weights': ["uniform", "distance"],
            'p': [1, 2]
        }
    },
    'LinearSVC': {
       'sklearn.svm.LinearSVC': {
            'penalty': ["l1", "l2"],
            'loss': ["hinge", "squared_hinge"],
            'dual': [True, False],
            'tol': [1e-5, 1e-4, 1e-3, 1e-2, 1e-1],
            'C': [1e-4, 1e-3, 1e-2, 1e-1, 0.5, 1., 5., 10., 15., 20., 25.]
        } 
    },
    'LogisticRegression': {
        'sklearn.linear_model.LogisticRegression': {
            'penalty': ["l1", "l2"],
            'C': [1e-4, 1e-3, 1e-2, 1e-1, 0.5, 1., 5., 10., 15., 20., 25.],
            'dual': [True, False]
        }
    },
    'LinearRegression': {
        'sklearn.linear_model.LinearRegression': {
        }
    },
    'XGBClassifier': {
        'xgboost.XGBClassifier': {
            'n_estimators': [100],
            'max_depth': range(1, 11),
            'learning_rate': [1e-3, 1e-2, 1e-1, 0.5, 1.],
            'subsample': np.arange(0.05, 1.01, 0.05),
            'min_child_weight': range(1, 21),
            'nthread': [1]
        }
    },
    'LGBMRegressor': {
        'lightgbm.LGBMRegressor': {
            'boosting_type': ['gbdt', 'dart'],
            'subsample': np.arange(0.05, 1.01, 0.05),
            # 'min_child_samples': [1, 5, 7, 10, 15, 20, 35, 50, 100, 200, 500, 1000],
            # 'num_leaves': [2, 4, 7, 10, 15, 20, 25, 30, 35, 40, 50, 65, 80, 100, 125, 150, 200, 250, 500], 
            # 'colsample_bytree': [0.7, 0.9, 1.0],
            'learning_rate': [1e-3, 1e-2, 1e-1, 0.5, 1.],
            'n_estimators': [100]
        }
    },
    'LGBMClassifier': {
        'lightgbm.LGBMClassifier': {
            'boosting_type': ['gbdt', 'dart'],
            'subsample': np.arange(0.05, 1.01, 0.05),
            # 'min_child_samples': [1, 5, 7, 10, 15, 20, 35, 50, 100, 200, 500, 1000],
            # 'num_leaves': [2, 4, 7, 10, 15, 20, 25, 30, 35, 40, 50, 65, 80, 100, 125, 150, 200, 250, 500], 
            # 'colsample_bytree': [0.7, 0.9, 1.0],
            'learning_rate': [1e-3, 1e-2, 1e-1, 0.5, 1.],
            'n_estimators': [100]
        }
    }

}

PREPROCESSINGS = {
    'sklearn.preprocessing.MaxAbsScaler': {
    },

    'sklearn.preprocessing.MinMaxScaler': {
    },

    'sklearn.decomposition.PCA': {
        'svd_solver': ['randomized'],
        'iterated_power': range(1, 11)
    },

    'sklearn.preprocessing.PolynomialFeatures': {
        'degree': [2],
        'include_bias': [False],
        'interaction_only': [False]
    },

    'sklearn.preprocessing.StandardScaler': {
    },

    'tpot.builtins.OneHotEncoder': {
        'minimum_fraction': [0.05, 0.1, 0.15, 0.2, 0.25],
        'sparse': [False]
    },
    'sklearn.preprocessing.Normalizer': {
        'norm': ['l1', 'l2', 'max']
    },
    'sklearn.decomposition.PCA': {
        'svd_solver': ['randomized'],
        'iterated_power': range(1, 11)
    },
    'sklearn.preprocessing.PolynomialFeatures': {
        'degree': [2],
        'include_bias': [False],
        'interaction_only': [False]
    },
    'sklearn.preprocessing.RobustScaler': {
    },

    'sklearn.preprocessing.StandardScaler': {
    },
    'tpot.builtins.OneHotEncoder': {
        'minimum_fraction': [0.05, 0.1, 0.15, 0.2, 0.25],
        'sparse': [False]
    }
}




class AutoMLTrainer:

    def __init__(self, algorithms, problemType='Classification'):
        self.problemType = problemType
        self.generations = 2
        self.population_size = 20
        self.offspring_size = 10
        self.mutation_rate = 0.9
        self.crossover_rate = 0.1
        if self.problemType == 'Classification':
            self.scoring = 'accuracy'
        else:
            self.scoring = 'neg_mean_squared_error'
        self.cv = 5
        self.subsample = 1.0
        self.n_jobs = 1
        self.max_time_mins = None
        self.max_eval_time_mins = 5
        self.random_state = None
        self.warm_start = False
        self.memory =None
        self.early_stop = None
        self.periodic_checkpoint_folder=None
        self.config_dict = self.get_config_dict(algorithms)

    def get_config_dict(self, algorithms):
        config_dict = {}
        for algo in algorithms:
            config_dict.update(ALGORITHM_NAME_OBJ_DICT[algo])
        config_dict.update(PREPROCESSINGS)
        # print('config dict contains >>>>',config_dict)
        return config_dict


    def get_dict(self):
        dict_ = { key:value for key, value in self.__dict__.items() }
        return dict_

    def trainModel(self, data, logFolder, newPMMLFileName, lock, kwargs):
        if 'generation' in kwargs['parameters']:
            self.generations = kwargs['parameters']['generation']
        if 'population_size' in kwargs['parameters']:
            self.population_size = kwargs['parameters']['population_size']
        if 'offspring_size' in kwargs['parameters']:
            self.offspring_size = kwargs['parameters']['offspring_size']
        if 'mutation_rate' in kwargs['parameters']:
            self.mutation_rate = kwargs['parameters']['mutation_rate']
        if 'crossover_rate' in kwargs['parameters']:
            self.crossover_rate = kwargs['parameters']['crossover_rate']
        if 'scoring' in kwargs['parameters']:
            self.scoring = kwargs['parameters']['scoring']
        if 'config_dict' in kwargs['parameters']:
            self.config_dict = kwargs['parameters']['config_dict']
        if 'cv' in kwargs['parameters']:
            self.cv = kwargs['parameters']['cv']
        if 'subsample' in kwargs['parameters']:
            self.subsample = kwargs['parameters']['subsample']
        if 'n_jobs' in kwargs['parameters']:
            self.n_jobs = kwargs['parameters']['n_jobs']
        if 'max_time_mins' in kwargs['parameters']:
            self.max_time_mins = kwargs['parameters']['max_time_mins']
        if 'max_eval_time_mins' in kwargs['parameters']:
            self.max_eval_time_mins = kwargs['parameters']['max_eval_time_mins']
        if 'random_state' in kwargs['parameters']:
            self.random_state = kwargs['parameters']['random_state']
        if 'warm_start' in kwargs['parameters']:
            self.warm_start = kwargs['parameters']['warm_start']
        if 'memory' in kwargs['parameters']:
            self.memory = kwargs['parameters']['memory']
        if 'early_stop' in kwargs['parameters']:
            self.early_stop = kwargs['parameters']['early_stop']

        paramToTrainModel=kwargs['data']
        idforData=kwargs['idforData']
        dataPath=kwargs['filePath']
        targetVar=kwargs['target_variable']

        projectName=idforData
        projectPath=logFolder+projectName
        dataFolder=projectPath+'/dataFolder/'
        tpotFolder=projectPath+'/tpotFolder/'
        self.periodic_checkpoint_folder=tpotFolder
        statusfileLocation=dataFolder+'status'+'.txt'

        def upDateStatus():
            lock.acquire()
            sFile=open(statusfileLocation,'r')
            sFileText=sFile.read()
            lock.release()
            data_details=json.loads(sFileText)
            return data_details

        try:
            dataMapperInner=autoMLutilities.createDataMapper(paramToTrainModel,targetVar)
        except Exception as e:
            data_details=upDateStatus()
            data_details['status']='Training Failed'
            data_details['errorMessage']='Error while creating DataFrameMapper >> '+ str(e)
            data_details['errorTraceback']=traceback.format_exc()
            with open(statusfileLocation,'w') as filetosave:
                json.dump(data_details, filetosave)
            # sys.exit()
            return


        mapper1=DataFrameMapper(dataMapperInner)

        # print ('mapper1 >>>>>>>>>>> ',mapper1)
        featureVar=list(data.columns)
        try:
            featureVar.remove(targetVar)
        except Exception as e:
            # print('errorrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr')
            data_details=upDateStatus()
            data_details['status']='Training Failed'
            data_details['errorMessage']='Target variable is not in the dataset'
            data_details['errorTraceback']=traceback.format_exc()
            with open(statusfileLocation,'w') as filetosave:
                json.dump(data_details, filetosave)
            # sys.exit()
            return
        try:
            dataX,dataY=autoMLutilities.createModelData(data,mapper1,targetVar)
        except Exception as e:
            data_details=upDateStatus()
            data_details['status']='Training Failed'
            data_details['errorMessage']='Error while preparing Data >> '+ str(e)
            data_details['errorTraceback']=traceback.format_exc()
            with open(statusfileLocation,'w') as filetosave:
                json.dump(data_details, filetosave)
            # sys.exit()
            return

        data_details=upDateStatus()
        data_details['listOfModelAccuracy']=[]
        data_details['pmmlFilelocation']=''

        with open(statusfileLocation,'w') as filetosave:
            json.dump(data_details, filetosave)

        
        newdataX=dataX
        newdataY=dataY
        param_dict = self.get_dict()
        del param_dict['problemType']
        # print ('Step >>> 1')
        procComp=True
        while procComp:
            try:
                if self.problemType=='Regression':
                    # print ('Enter the training with param',param_dict)
                    tpot = TPOTRegressor(**param_dict)
                    tpot.fit(newdataX, newdataY)
                    pp=tpot.fitted_pipeline_
                    pp=pp.steps
                elif self.problemType=='Classification':
                    tpot = TPOTClassifier(**param_dict)
                    tpot.fit(newdataX, newdataY)
                    pp=tpot.fitted_pipeline_
                    pp=pp.steps
                # print('>>>>>>>>> Training Complete')
            except Exception as e:
                data_details=upDateStatus()
                data_details['status']='Training Failed'
                data_details['errorMessage']='Error in parameter settings >> '+ str(e)
                data_details['errorTraceback']=traceback.format_exc()
                with open(statusfileLocation,'w') as filetosave:
                    json.dump(data_details, filetosave)
                # sys.exit()
                return
            joblib.dump(pp,dataFolder+'tpotPipeline.pkl')
            prePipeline=mapper1
            pipelineList=[('feature_mapper',prePipeline)]
            pipelineList.append(pp[-1])
            
            # statusFile=dataFolder+'status'+'.txt'
            with open(statusfileLocation,'r') as sFile:
                sFileText=sFile.read()
            data_details=json.loads(sFileText)
            data_details['status']='In Progress'
            with open(statusfileLocation,'w') as filetosave:
                json.dump(data_details, filetosave)

            finalPipe=Pipeline(pipelineList)
            finalPipe.fit(data[featureVar],data[targetVar])
            # print ('finalPipe >>>>> ',finalPipe)

            finalPMMLfile=dataFolder+newPMMLFileName
            # finalPMMLfile='../ZMOD/Models/'+newPMMLFileName
            finalpklfile=dataFolder+newPMMLFileName+'.pkl'
            joblib.dump(finalPipe,finalpklfile)
            toExportDict={
                            'model1':{'data':None,'hyperparameters':None,'preProcessingScript':None,
                                'pipelineObj':Pipeline(finalPipe.steps[:-1]),'modelObj':finalPipe.steps[-1][1],
                                'featuresUsed':featureVar,
                                'targetName':targetVar,'postProcessingScript':None,'taskType': 'score'}
                        }
            try:
                # print ('toExportDict >>>>>>>>>>>> ',toExportDict)
                from nyokaBase.skl.skl_to_pmml import model_to_pmml
                model_to_pmml(toExportDict, PMMLFileName=finalPMMLfile)
                print ('>>>>>>>>>>>>>>>>>>>>>>> Success')
                procComp=False
            except:
                procComp=True
                print ('>>>>>>>>>>>>>>>>>>>>>>> Failed Saving Trying again')
            
        model_accuracy=[]

        # print ('Came here')

        for num,i in enumerate(tpot.evaluated_individuals_):
            k= {'modelDetail':i,'modelName':i.split("(")[0],'score':round(tpot.evaluated_individuals_[i]['internal_cv_score'],4),'bestmodel':0}
            model_accuracy.append(k)
        model_accuracy.sort(key=operator.itemgetter('score'),reverse=True)
        model_accuracy[0]['bestmodel']=1

        with open(statusfileLocation,'r') as sFile:
            sFileText=sFile.read()
        data_details=json.loads(sFileText)
        data_details['status']='Complete'
        data_details['pmmlFilelocation']=finalPMMLfile
        data_details['listOfModelAccuracy']=model_accuracy
        print ('data_details >>>>>>>>>>> ',data_details.keys())
        with open(statusfileLocation,'w') as filetosave:
            json.dump(data_details, filetosave)

class AnomalyTrainer:

    def __init__(self, algorithms, problemType='Classification'):
        self.problemType = problemType
    def get_dict(self):
        dict_ = { key:value for key, value in self.__dict__.items() }
        return dict_

    def trainAnomalyModel(self, data, logFolder, newPMMLFileName, lock, kwargs):

        print ('here'*20,kwargs)
        paramToTrainModel=kwargs['data']
        idforData=kwargs['idforData']
        dataPath=kwargs['filePath']
        try:
            targetVar=kwargs['target_variable']
        except:
            targetVar=None
        algorithmToUse=kwargs['parameters']['algorithm']

        projectName=idforData
        projectPath=logFolder+projectName
        dataFolder=projectPath+'/dataFolder/'
        statusfileLocation=dataFolder+'status'+'.txt'

        def upDateStatus():
            lock.acquire()
            sFile=open(statusfileLocation,'r')
            sFileText=sFile.read()
            lock.release()
            data_details=json.loads(sFileText)
            return data_details

        try:
            dataMapperInner=autoMLutilities.createDataMapper(paramToTrainModel,targetVar)
        except Exception as e:
            data_details=upDateStatus()
            data_details['status']='Training Failed'
            data_details['errorMessage']='Error while creating DataFrameMapper >> '+ str(e)
            data_details['errorTraceback']=traceback.format_exc()
            with open(statusfileLocation,'w') as filetosave:
                json.dump(data_details, filetosave)
            # sys.exit()
            return


        mapper1=DataFrameMapper(dataMapperInner)
        featureVar=list(data.columns)

        if algorithmToUse=='IsolationForest':
            print ('came here')
            from sklearn import ensemble
            modelT=ensemble.IsolationForest()
        elif algorithmToUse == 'OneClassSVM':
            from sklearn import svm
            modelT=svm.OneClassSVM()
        elif algorithmToUse == 'LinearSVR':
            print ('Came to SVR')
            from sklearn import svm
            modelT=svm.LinearSVR()
        # else:
        #     data_details=upDateStatus()
        #     data_details['status']='Training Failed'
        #     data_details['errorMessage']='Model not supported >> '
        #     data_details['errorTraceback']='None'
        #     with open(statusfileLocation,'w') as filetosave:
        #         json.dump(data_details, filetosave)
        #     # sys.exit()
        #     return

        try:
            print ('training started')
            pipeline = Pipeline([('feature_mapper', mapper1),('model',modelT)])
            pipelObj=pipeline.fit(data)
            print ('training completed')
       
        except Exception as e:
            data_details=upDateStatus()
            data_details['status']='Training Failed'
            data_details['errorMessage']='Error while preparing Data and training model >> '+ str(e)
            data_details['errorTraceback']=traceback.format_exc()
            with open(statusfileLocation,'w') as filetosave:
                json.dump(data_details, filetosave)
            # sys.exit()
            return

        data_details=upDateStatus()
        data_details['listOfModelAccuracy']=[]
        data_details['pmmlFilelocation']=''

        with open(statusfileLocation,'w') as filetosave:
            json.dump(data_details, filetosave)

        finalPMMLfile='../ZMOD/Models/'+newPMMLFileName
        toExportDict={
                        'model1':{'data':None,'hyperparameters':None,'preProcessingScript':None,
                            'pipelineObj':Pipeline(pipelObj.steps[:-1]),'modelObj':pipelObj.steps[-1][1],
                            'featuresUsed':featureVar,
                            'targetName':None,'postProcessingScript':None,'taskType': 'score'}
                    }
        try:
            print ('toExportDict >>>>>>>>>>>> ',toExportDict)
            from nyokaBase.skl.skl_to_pmml import model_to_pmml
            model_to_pmml(toExportDict, PMMLFileName=finalPMMLfile)
            print ('>>>>>>>>>>>>>>>>>>>>>>> Success')
        except Exception as e:
            data_details=upDateStatus()
            data_details['status']='Training Failed'
            data_details['errorMessage']='Error while Saving Model >> '+ str(e)
            data_details['errorTraceback']=traceback.format_exc()
            with open(statusfileLocation,'w') as filetosave:
                json.dump(data_details, filetosave)
            # sys.exit()
            return
            print ('>>>>>>>>>>>>>>>>>>>>>>> Failed Saving Trying again')

        with open(statusfileLocation,'r') as sFile:
            sFileText=sFile.read()
        model_accuracy=[]
        data_details=json.loads(sFileText)
        data_details['status']='Complete'
        data_details['pmmlFilelocation']=finalPMMLfile
        data_details['listOfModelAccuracy']=model_accuracy
        with open(statusfileLocation,'w') as filetosave:
            json.dump(data_details, filetosave)
