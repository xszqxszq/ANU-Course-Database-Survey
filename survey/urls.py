from django.urls import path
from . import views

urlpatterns = [
	path('view', views.view),
	path('submit', views.submit),
	path('create', views.create),
	path('manage', views.manage),
	path('end', views.end),
	path('delete', views.delete),
	path('records', views.records),
	path('analysis', views.analysis),
]