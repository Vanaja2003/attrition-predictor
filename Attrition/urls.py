from django.urls import path
from .views import Attrition_rate_finder, home, prediction_history, insights

urlpatterns = [
    path('', home, name='home'),
    path('show_attrition/', Attrition_rate_finder, name='attrition_show'),
    path('history/', prediction_history, name='prediction_history'),
    path('insights/', insights, name='insights'),
    # path('results-attrition/', results, name='results_show'),
]