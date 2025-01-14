from django.db import models
from django.utils import timezone

class PredictionHistory(models.Model):
    employee_name = models.CharField(max_length=100)
    age = models.IntegerField()
    department = models.CharField(max_length=50)
    job_role = models.CharField(max_length=100)
    monthly_income = models.FloatField()
    years_at_company = models.FloatField()
    job_satisfaction = models.IntegerField()
    work_life_balance = models.IntegerField()
    prediction_result = models.BooleanField()  # True for high risk, False for low risk
    prediction_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-prediction_date']  # Show newest predictions first

    def __str__(self):
        return f"{self.employee_name} - {'High Risk' if self.prediction_result else 'Low Risk'}"
