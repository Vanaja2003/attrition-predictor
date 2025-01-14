from django.shortcuts import render, redirect
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from .models import PredictionHistory
from django.db.models import Avg, Count, Q, Case, When, F, Value
from django.db.models.functions import ExtractMonth

def calculate_risk_score(form_data):
    """Calculate risk score based on multiple factors"""
    score = 0
    
    # Job Satisfaction and Work-Life Balance (40% weight)
    satisfaction_score = (5 - form_data['job_satisfaction']) * 10  # 1-4 scale inverted
    work_life_score = (5 - form_data['work_life_balance']) * 10   # 1-4 scale inverted
    score += (satisfaction_score + work_life_score) * 0.4
    
    # Salary Factors (30% weight)
    if form_data['monthly_income'] < 4000:
        score += 30
    elif form_data['monthly_income'] < 6000:
        score += 20
    elif form_data['monthly_income'] < 8000:
        score += 10
        
    # Years at Company (20% weight)
    if form_data['years_at_company'] < 2:
        score += 20
    elif form_data['years_at_company'] < 4:
        score += 10
    
    # Department Risk Factors (10% weight)
    high_risk_departments = ['sales', 'it']  # Departments with historically higher turnover
    if form_data['department'].lower() in high_risk_departments:
        score += 10
        
    return score > 50  # Return True if risk score > 50%

def home(request):
    return render(request, 'home.html')

def predict(request):
    prediction_result = None
    if request.method == 'POST':
        # Get form data
        form_data = {
            'employee_name': request.POST.get('employee_name'),
            'age': int(request.POST.get('age')),
            'department': request.POST.get('department'),
            'job_role': request.POST.get('job_role'),
            'monthly_income': float(request.POST.get('monthly_income')),
            'years_at_company': float(request.POST.get('years_at_company')),
            'job_satisfaction': int(request.POST.get('job_satisfaction')),
            'work_life_balance': int(request.POST.get('work_life_balance'))
        }
        
        # Calculate prediction using the new risk score function
        prediction_result = calculate_risk_score(form_data)
        
        # Save prediction to history
        PredictionHistory.objects.create(
            employee_name=form_data['employee_name'],
            age=form_data['age'],
            department=form_data['department'],
            job_role=form_data['job_role'],
            monthly_income=form_data['monthly_income'],
            years_at_company=form_data['years_at_company'],
            job_satisfaction=form_data['job_satisfaction'],
            work_life_balance=form_data['work_life_balance'],
            prediction_result=prediction_result
        )
        
    return render(request, 'predict.html', {'prediction_result': prediction_result})

def insights(request):
    # Get total predictions
    total_predictions = PredictionHistory.objects.count()
    high_risk_count = PredictionHistory.objects.filter(prediction_result=True).count()
    
    if total_predictions > 0:
        # Calculate percentages
        high_risk_percentage = (high_risk_count / total_predictions) * 100
        low_risk_percentage = 100 - high_risk_percentage

        # Department-wise analysis using aggregation
        department_analysis = (
            PredictionHistory.objects.values('department')
            .annotate(
                total=Count('id'),
                high_risk=Count(Case(When(prediction_result=True, then=1))),
                low_risk=Count(Case(When(prediction_result=False, then=1)))
            )
            .order_by('-total')
        )

        # Calculate percentages for each department
        for dept in department_analysis:
            dept['high_risk_percentage'] = (dept['high_risk'] / dept['total'] * 100)
            dept['low_risk_percentage'] = (dept['low_risk'] / dept['total'] * 100)

        # Sort by high risk percentage
        department_analysis = sorted(department_analysis, key=lambda x: x['high_risk_percentage'], reverse=True)

        # Average metrics for high risk vs low risk
        high_risk_metrics = PredictionHistory.objects.filter(prediction_result=True).aggregate(
            avg_age=Avg('age'),
            avg_income=Avg('monthly_income'),
            avg_years=Avg('years_at_company'),
            avg_satisfaction=Avg('job_satisfaction'),
            avg_work_life=Avg('work_life_balance')
        )

        low_risk_metrics = PredictionHistory.objects.filter(prediction_result=False).aggregate(
            avg_age=Avg('age'),
            avg_income=Avg('monthly_income'),
            avg_years=Avg('years_at_company'),
            avg_satisfaction=Avg('job_satisfaction'),
            avg_work_life=Avg('work_life_balance')
        )

        context = {
            'total_predictions': total_predictions,
            'high_risk_percentage': high_risk_percentage,
            'low_risk_percentage': low_risk_percentage,
            'department_analysis': department_analysis,
            'high_risk_metrics': high_risk_metrics,
            'low_risk_metrics': low_risk_metrics,
        }
    else:
        context = {
            'total_predictions': 0
        }

    return render(request, 'insights.html', context)

def prediction_history(request):
    history = PredictionHistory.objects.all()
    return render(request, 'prediction_history.html', {'predictions': history})
