from django.shortcuts import render, redirect
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from .models import AttritionPrediction, Attrition_table
from django.db.models import Avg, Count, Q, Case, When, F, Value
from django.db.models.functions import ExtractMonth

def calculate_risk_score(form_data):
    """Calculate risk score based on multiple factors"""
    score = 0
    max_score = 100  # Maximum possible score
    
    # Experience and Tenure (30 points)
    experience = float(form_data.get('experience', 0))
    if experience < 2:
        score += 15  # New employees are at higher risk
    elif experience < 5:
        score += 10
    
    tenure_mapping = {
        '< =1': 15,
        '1-2': 10,
        '2-5': 5,
        '5-10': 2,
        '>10': 0
    }
    score += tenure_mapping.get(form_data.get('tenure_group', '< =1'), 15)
    
    # Age Factor (15 points)
    age = int(form_data.get('age', 25))
    if age < 25:
        score += 15  # Very young employees tend to change jobs more frequently
    elif age < 30:
        score += 10
    elif age < 35:
        score += 5
    
    # Career Growth Factors (25 points)
    if form_data.get('promoted') != 'Yes':
        score += 15  # Lack of promotion increases risk
    if form_data.get('job_role_match') != 'Yes':
        score += 10  # Poor job-skill match increases risk
        
    # Employee Group (10 points)
    group_mapping = {
        'C': 10,
        'B': 5,
        'A': 0
    }
    score += group_mapping.get(form_data.get('emp_group', 'C'), 10)
    
    # Location and Function (10 points)
    high_risk_locations = ['Bangalore', 'Mumbai', 'Delhi']
    if form_data.get('location') in high_risk_locations:
        score += 5
        
    function_mapping = {
        'Sales': 5,
        'IT': 2,
        'Marketing': 3,
        'HR': 2,
        'Operations': 2
    }
    score += function_mapping.get(form_data.get('function', ''), 3)
    
    # Hiring Source and Other Factors (10 points)
    source_mapping = {
        'Agency': 5,
        'Referral': 2,
        'Direct': 1,
        'Campus': 3
    }
    score += source_mapping.get(form_data.get('hiring_source', ''), 3)
    
    if form_data.get('marital_status') == 'Single':
        score += 5  # Single employees might be more mobile
    
    # Calculate risk percentage
    risk_percentage = (score / max_score) * 100
    
    # Determine risk level
    if risk_percentage >= 70:
        risk_level = 'High Risk'
    elif risk_percentage >= 40:
        risk_level = 'Medium Risk'
    else:
        risk_level = 'Low Risk'
    
    return {
        'is_at_risk': risk_percentage > 50,
        'risk_score': risk_percentage,
        'risk_level': risk_level
    }

def home(request):
    return render(request, 'home.html')

def predict(request):
    context = {}
    if request.method == 'POST':
        try:
            # Get form data with proper type conversion and validation
            form_data = {
                'employee_name': request.POST.get('employee_name', '').strip(),
                'location': request.POST.get('location', '').strip(),
                'emp_group': request.POST.get('emp_group', '').strip(),
                'function': request.POST.get('function', '').strip(),
                'gender': request.POST.get('gender', '').strip(),
                'tenure_group': request.POST.get('tenure_group', '').strip(),
                'experience': float(request.POST.get('experience', 0)),
                'age': int(request.POST.get('age', 25)),
                'marital_status': request.POST.get('marital_status', '').strip(),
                'hiring_source': request.POST.get('hiring_source', '').strip(),
                'promoted': request.POST.get('promoted', 'No'),
                'job_role_match': request.POST.get('job_role_match', 'No')
            }
            
            # Validate required fields
            required_fields = ['employee_name', 'location', 'emp_group', 'function', 
                             'gender', 'tenure_group', 'marital_status', 'hiring_source']
            missing_fields = [field for field in required_fields if not form_data.get(field)]
            
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Validate numeric fields
            if form_data['experience'] < 0:
                raise ValueError("Experience cannot be negative")
            if form_data['age'] < 18:
                raise ValueError("Age must be at least 18")
            
            # Make prediction
            prediction_results = calculate_risk_score(form_data)
            
            # Save prediction to database
            prediction = AttritionPrediction(
                employee_name=form_data['employee_name'],
                location=form_data['location'],
                emp_group=form_data['emp_group'],
                function=form_data['function'],
                gender=form_data['gender'],
                tenure_group=form_data['tenure_group'],
                experience=form_data['experience'],
                age=form_data['age'],
                marital_status=form_data['marital_status'],
                hiring_source=form_data['hiring_source'],
                promoted=form_data['promoted'] == 'Yes',
                job_role_match=form_data['job_role_match'] == 'Yes',
                prediction_result=prediction_results['is_at_risk'],
                risk_level=prediction_results['risk_level'],
                risk_score=prediction_results['risk_score']
            )
            prediction.save()
            
            context = {
                'prediction': prediction,
                'risk_score': round(prediction_results['risk_score'], 1),
                'success': True
            }
            
        except (ValueError, TypeError) as e:
            context = {
                'error': str(e),
                'form_data': form_data
            }
        except Exception as e:
            context = {
                'error': f"An unexpected error occurred: {str(e)}",
                'form_data': form_data
            }
    
    return render(request, 'predict.html', context)

def insights(request):
    predictions = AttritionPrediction.objects.all()
    total_predictions = predictions.count()

    if total_predictions == 0:
        return render(request, 'insights.html', {'total_predictions': 0})

    # Filter for High Risk records
    high_risk = predictions.filter(risk_level__icontains='High').count()
    low_risk = total_predictions - high_risk
    high_risk_percentage = (high_risk / total_predictions) * 100
    low_risk_percentage = (low_risk / total_predictions) * 100

    # Function Analysis - Group by function and aggregate
    functions = predictions.values('function').annotate(
        total=Count('id', distinct=True),
        high_risk=Count('id', filter=Q(risk_level__icontains='High'), distinct=True),
        low_risk=Count('id', filter=~Q(risk_level__icontains='High'), distinct=True)
    ).order_by('function')
    
    for func in functions:
        func['high_risk_percentage'] = (func['high_risk'] / func['total']) * 100
        func['low_risk_percentage'] = (func['low_risk'] / func['total']) * 100

    # Employee Group Analysis
    emp_groups = predictions.values('emp_group').annotate(
        total=Count('id', distinct=True),
        high_risk=Count('id', filter=Q(risk_level__icontains='High'), distinct=True)
    ).order_by('emp_group')
    
    for group in emp_groups:
        group['high_risk_percentage'] = (group['high_risk'] / group['total']) * 100

    # Tenure Group Analysis
    tenure_groups = predictions.values('tenure_group').annotate(
        total=Count('id', distinct=True),
        high_risk=Count('id', filter=Q(risk_level__icontains='High'), distinct=True)
    ).order_by('tenure_group')
    
    for tenure in tenure_groups:
        tenure['high_risk_percentage'] = (tenure['high_risk'] / tenure['total']) * 100

    # High Risk vs Low Risk Metrics
    high_risk_metrics = predictions.filter(risk_level__icontains='High').aggregate(
        avg_age=Avg('age'),
        avg_experience=Avg('experience')
    )

    low_risk_metrics = predictions.exclude(risk_level__icontains='High').aggregate(
        avg_age=Avg('age'),
        avg_experience=Avg('experience')
    )

    context = {
        'total_predictions': total_predictions,
        'high_risk_percentage': high_risk_percentage,
        'low_risk_percentage': low_risk_percentage,
        'function_analysis': functions,
        'emp_group_analysis': emp_groups,
        'tenure_group_analysis': tenure_groups,
        'high_risk_metrics': high_risk_metrics,
        'low_risk_metrics': low_risk_metrics
    }

    return render(request, 'insights.html', context)

def prediction_history(request):
    predictions = AttritionPrediction.objects.all().order_by('-prediction_date')
    return render(request, 'prediction_history.html', {'predictions': predictions})
