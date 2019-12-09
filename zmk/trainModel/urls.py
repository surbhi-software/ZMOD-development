# from django.contrib import admin
# from django.urls import path
# from django.conf.urls import *
# from transferLearning import views
# # from nyokaserver import views
# from django.conf.urls.static import static
# from django.conf import settings
# from trainModel.views import RunningTaskView,TrainAutoMLView,RunningTaskOperationView,TrainNNView
# from django.views.decorators.csrf import csrf_exempt
# from trainModel.training import Training


# urlpatterns=[

# 	# (? url(r'^pmml/(?P<param>\w+|)',csrf_exempt(PMMLView.as_view())),)
# 	# url(r'^runningTasks/?(?P<param>\w+|)',csrf_exempt(RunningTaskView.as_view())),
# 	# url(r'^trainModel/?(?P<param>\w+|)',csrf_exempt(TrainModelView.as_view())),
#     # path('runningTasks',csrf_exempt(RunningTaskView.as_view())),
# 	# path('runningTasks',RunningTaskView.trainNeuralNetworkModels,name='trainNeuralNetworkModels'),
#     # path('autoMLsenddata',Training.autoMLdataprocess,name ='autoMLdataprocess'),
#     # path('autoMLTrainModel',Training.autoMLtrainModel,name ='autoMLTrainModel'),
# 	path('runningTasks',csrf_exempt(RunningTaskView.as_view())),
# 	path('runningTasks/<id_for_task>',csrf_exempt(RunningTaskOperationView.as_view())),
# 	path('trainAutoMLModel',csrf_exempt(TrainAutoMLView.as_view())),
# 	path('trainNNModel',csrf_exempt(TrainNNView.as_view())),
# ]