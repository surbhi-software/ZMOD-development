# from django.contrib import admin
# from django.urls import path
# from django.conf.urls import *
# from transferLearning import views
# # from nyokaserver import views
# from django.conf.urls.static import static
# from django.conf import settings
# from nyokaserver.nyokaServerClass import NyokaServer
# from nyokaserver.views import PMMLView,PMMLOpeartionView,PMMLLayerView,PMMLGlobalView
# from django.views.decorators.csrf import csrf_exempt

# urlpatterns=[
# 	path('listOfLayers',NyokaServer.listOfLayers,name='listOfLayers'),
# 	# path('addArchitecture',NyokaServer.addArchitectureToGlobalMemoryDict,name='addLayerToGlobalMemoryDict'),
#  #    # url(pref+'addPMMLfile$',views2.addLayerToGlobalMemoryDict,name='addLayerToGlobalMemoryDict'),
#  #    path('getGlobal',NyokaServer.getGlobalObject,name='getGlobalObject'),
#  #    path('updateLayer',NyokaServer.updatetoArchitecture,name='updateArchitecture'),
#  #    path('deleteLayer',NyokaServer.deletelayer,name='deletelayer'),
#     # url(r'^pmml/(?P<param>\w+|)',csrf_exempt(PMMLView.as_view())),
#     path('pmml',csrf_exempt(PMMLView.as_view())),
#     path('pmml/<projectID>',csrf_exempt(PMMLOpeartionView.as_view())),
#     path('pmml/getGloabl',csrf_exempt(PMMLGlobalView.as_view())),
#     path('pmml/<projectID>/layer',csrf_exempt(PMMLLayerView.as_view())),
# ]