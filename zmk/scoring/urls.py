# from django.contrib import admin
# from django.urls import path
# from django.conf.urls import *
# from transferLearning import views
# # from nyokaserver import views
# from django.conf.urls.static import static
# from django.conf import settings
# from scoring.scoringClass import Scoring
# from scoring.views import ScoreView,ModelsView,ModelOperationView
# from django.views.decorators.csrf import csrf_exempt

# urlpatterns=[
# 	# path('getListofModels',Scoring.getListOfModelinMemory,name ='getListofModels'),
#     # path('loadModel',Scoring.loadModelfile,name ='loadModel'),
#     # path('unloadModel',Scoring.removeModelfromMemory,name ='unloadModel'),
#     # path('predicttestdata',Scoring.predicttestdata,name ='predicttestdata'),
#     # url(r'^models/?(?P<param>\w+|)',csrf_exempt(ScoreView.as_view())),
#     path('models',csrf_exempt(ModelsView.as_view())),
#     path('models/<modelName>',csrf_exempt(ModelOperationView.as_view())),
#     path('models/<modelName>/score',csrf_exempt(ScoreView.as_view())),
# ]