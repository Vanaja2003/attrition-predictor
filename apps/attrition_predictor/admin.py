from django.contrib import admin
from apps.attrition_predictor.models import Attrition_table, AttritionPrediction

@admin.register(Attrition_table)
class AttritionTableAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'emp_group', 'function', 'gender', 'age', 'experience')
    search_fields = ('name', 'location', 'emp_group')
    list_filter = ('location', 'emp_group', 'function', 'gender')

@admin.register(AttritionPrediction)
class AttritionPredictionAdmin(admin.ModelAdmin):
    list_display = ('employee_name', 'location', 'emp_group', 'function', 'prediction_result', 'prediction_date')
    search_fields = ('employee_name', 'location', 'emp_group')
    list_filter = ('prediction_result', 'location', 'emp_group', 'function')
    readonly_fields = ('prediction_date',)
    ordering = ('-prediction_date',)
