from django.urls import path
from django.conf.urls.static import static
from .views import Attrition_rate_finder, results
from django.conf import settings

urlpatterns = [
    path('show_attrition/', Attrition_rate_finder, name='attrition_show'),
    path('results-attrition/', results, name='results_show'),
    ]

urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)