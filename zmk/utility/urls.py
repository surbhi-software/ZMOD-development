# from django.contrib import admin
# from django.urls import path
# from django.conf.urls import *
# from transferLearning import views
# # from nyokaserver import views
# from django.conf.urls.static import static
# from django.conf import settings
# from utility.views import UtilityView
# from django.views.decorators.csrf import csrf_exempt

# urlpatterns=[
# 	# path('runningTaskList',Utility.runningTaskList,name='runningTaskList'),
# 	# path('deleteTaskfromMemory', Utility.deleteTaskfromMemory, name='deleteTaskfromMemory'),
#  	# path('downloadFile',Utility.downloadPMML,name='downloadPMML'),
#  	path('downloadFile',csrf_exempt(UtilityView.as_view())),
# ]