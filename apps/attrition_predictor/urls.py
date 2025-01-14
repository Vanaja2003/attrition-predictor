from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('predict/', views.predict, name='predict'),
    path('insights/', views.insights, name='insights'),
    path('history/', views.prediction_history, name='prediction_history'),
]
