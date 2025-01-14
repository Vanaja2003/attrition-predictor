from django.db import models
from django.utils import timezone

class Attrition_table(models.Model):
    table_id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, blank=True, max_length=200)
    location = models.CharField(null=True, blank=True, max_length=50)
    emp_group = models.CharField(null=True, blank=True, max_length=20)
    function = models.CharField(null=True, blank=True, max_length=20)
    gender = models.CharField(null=True, blank=True, max_length=10)
    tenure_group = models.CharField(null=True, blank=True, max_length=10, default="< =1")
    experience = models.FloatField(null=True, blank=True, default=0.0)
    maritial = models.CharField(null=True, blank=True, max_length=30)
    age = models.FloatField(null=True, blank=True, default=25.0)
    hiring_source = models.CharField(max_length=40)
    promoted_before = models.CharField(null=True, blank=True, max_length=40)
    job_role = models.CharField(null=True, blank=True, max_length=10)

    def __str__(self):
        return self.name


class AttritionPrediction(models.Model):
    employee_name = models.CharField(max_length=100, default='Unknown')
    location = models.CharField(max_length=50, default='Unknown')
    emp_group = models.CharField(max_length=10, default='C')
    function = models.CharField(max_length=50, default='Unknown')
    gender = models.CharField(max_length=10, default='Unknown')
    tenure_group = models.CharField(max_length=20, default='< =1')
    experience = models.FloatField(default=0.0)
    age = models.IntegerField(default=25)
    marital_status = models.CharField(max_length=20, default='Unknown')
    hiring_source = models.CharField(max_length=50, default='Direct')
    promoted = models.BooleanField(default=False)
    job_role_match = models.BooleanField(default=False)
    prediction_result = models.BooleanField(default=False)
    risk_level = models.CharField(max_length=20, default='Medium Risk')
    risk_score = models.FloatField(default=50.0)
    prediction_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.employee_name} - {self.risk_level}"

    class Meta:
        ordering = ['-prediction_date']

    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.experience < 0:
            raise ValidationError({'experience': 'Experience cannot be negative'})
        
        if self.age < 18:
            raise ValidationError({'age': 'Age must be at least 18'})
        
        if self.emp_group not in ['A', 'B', 'C']:
            raise ValidationError({'emp_group': 'Invalid employee group'})
            
        if self.tenure_group not in ['< =1', '1-2', '2-5', '5-10', '>10']:
            raise ValidationError({'tenure_group': 'Invalid tenure group'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
