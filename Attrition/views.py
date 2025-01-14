from django.shortcuts import render, redirect
import pandas as pd
import pickle, os, random
import traceback
from django.http import HttpResponse, JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncMonth
from .models import AttritionPrediction
from django.utils import timezone
from django.db.models import Q

def home(request):
    return render(request, 'home.html')

# Finding attrition rate:
def Attrition_rate_finder(request):
    results = None
    try:
        print("Method:", request.method)
        if request.method == 'POST':
            print("POST data:", request.POST)
            if request.POST.get('attrition_button'):
                name = request.POST.get('Person Name', '')
                location = request.POST.get('location', '')
                emp_group = request.POST.get('emp-group', '')
                function = request.POST.get('function', '')
                gender = request.POST.get('gender', '')
                tenure_group = request.POST.get('tenure group', '')
                experience = request.POST.get('experience', '')
                age = request.POST.get('age', '')
                Maritial = request.POST.get('Marital', '')
                Hiring = request.POST.get('Hiring', '')
                Promoted = request.POST.get('Promoted', '')
                Job = request.POST.get('Job', '')
                
                print(f"Received data: name={name}, location={location}, emp_group={emp_group}, function={function}")
                print(f"gender={gender}, tenure_group={tenure_group}, experience={experience}, age={age}")
                print(f"Maritial={Maritial}, Hiring={Hiring}, Promoted={Promoted}, Job={Job}")

                # Convert Promoted and Job to binary values
                Promoted_bool = Promoted == 'Yes'
                Job_bool = Job == 'Yes'

                prediction = Finder(name, location, emp_group, function, gender, tenure_group,
                                          experience, age, Maritial, Hiring, Promoted, Job)
                print("Prediction results:", prediction)
                
                if prediction is not None:
                    results = "Yes" if prediction[0] else "No"
                    print("Final results:", results)

                    try:
                        # Save prediction to database
                        prediction_obj = AttritionPrediction.objects.create(
                            employee_name=name,
                            location=location,
                            emp_group=emp_group,
                            function=function,
                            gender=gender,
                            tenure_group=tenure_group,
                            experience=float(experience),
                            age=int(age),
                            marital_status=Maritial,
                            hiring_source=Hiring,
                            promoted=Promoted_bool,
                            job_role_match=Job_bool,
                            prediction_result=prediction[0]
                        )
                        print(f"Prediction saved to database with ID: {prediction_obj.id}")
                    except Exception as e:
                        print(f"Error saving prediction to database: {str(e)}")
                        print(traceback.format_exc())
                else:
                    print("Prediction returned None")
                    results = None

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'result': results,
                    'success': True
                })
            
            return render(request, 'attrition_form.html', {'result': results})
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': str(e),
                'success': False
            })
        return render(request, 'attrition_form.html', {'error': str(e)})
    
    return render(request, 'attrition_form.html')

def prediction_history(request):
    try:
        # Get all predictions ordered by date (newest first)
        predictions = AttritionPrediction.objects.all().order_by('-prediction_date')
        print(f"Found {predictions.count()} predictions")
        for pred in predictions[:5]:  # Print first 5 predictions for debugging
            print(f"Prediction: {pred.employee_name} - {pred.prediction_result}")
        return render(request, 'prediction_history.html', {'predictions': predictions})
    except Exception as e:
        print("Error in prediction_history:", str(e))
        print(traceback.format_exc())
        return render(request, 'prediction_history.html', {'error': str(e)})

def insights(request):
    # Calculate various insights
    total_predictions = AttritionPrediction.objects.count()
    at_risk_count = AttritionPrediction.objects.filter(prediction_result=True).count()
    not_at_risk_count = total_predictions - at_risk_count
    
    # Risk percentage
    risk_percentage = (at_risk_count / total_predictions * 100) if total_predictions > 0 else 0
    
    # Monthly trend
    monthly_predictions = (
        AttritionPrediction.objects
        .annotate(month=TruncMonth('prediction_date'))
        .values('month')
        .annotate(total=Count('id'), at_risk=Count('id', filter=Q(prediction_result=True)))
        .order_by('month')
    )
    
    # Department-wise analysis
    department_analysis = (
        AttritionPrediction.objects
        .values('function')
        .annotate(total=Count('id'), at_risk=Count('id', filter=Q(prediction_result=True)))
        .order_by('function')
    )
    
    # Age group analysis
    def get_age_group(age):
        if age < 25: return '<25'
        elif age < 35: return '25-35'
        elif age < 45: return '35-45'
        else: return '45+'
    
    age_analysis = []
    for group in ['<25', '25-35', '35-45', '45+']:
        if group == '<25':
            queryset = AttritionPrediction.objects.filter(age__lt=25)
        elif group == '25-35':
            queryset = AttritionPrediction.objects.filter(age__gte=25, age__lt=35)
        elif group == '35-45':
            queryset = AttritionPrediction.objects.filter(age__gte=35, age__lt=45)
        else:
            queryset = AttritionPrediction.objects.filter(age__gte=45)
        
        total = queryset.count()
        at_risk = queryset.filter(prediction_result=True).count()
        age_analysis.append({
            'group': group,
            'total': total,
            'at_risk': at_risk,
            'percentage': (at_risk / total * 100) if total > 0 else 0
        })
    
    context = {
        'total_predictions': total_predictions,
        'at_risk_count': at_risk_count,
        'not_at_risk_count': not_at_risk_count,
        'risk_percentage': risk_percentage,
        'monthly_predictions': monthly_predictions,
        'department_analysis': department_analysis,
        'age_analysis': age_analysis,
    }
    
    print("Insights data:", context)
    return render(request, 'insights.html', context)

def Finder(name, location, emp_group, function, gender, tenure_group,
                                  experience, age, Maritial, Hiring, Promoted, Job):
    try:
        if name != "":
            # Convert location to numeric value
            location_map = {
                'Bangalore': '5',
                'Pune': '3',
                'New Delhi': '1',
                'Chennai': '7',
                'Noida': '6',
                'Hyderabad': '4',
                'Madurai': '2'
            }
            location_numeric = location_map.get(location, '1')  # Default to '1' if location not found
            
            df = pd.DataFrame(columns=['id', 'Experience (YY.MM)', 'Age in YY.', 'New Location',
                                       'New Promotion', 'New Job Role Match', 'Agency', 'Direct',
                                       'Employee Referral', 'Marr.', 'Single', 'other status', 'B1', 'B2',
                                       'B3', 'other group', '< =1', '> 1 & < =3', 'Operation', 'Sales',
                                       'Support', 'Female', 'Male', 'other'])

            HiringSource = HiringPeep(Hiring)
            Maritial_Status = MStatus(Maritial)
            EmpGrp = EmployeeGrp(emp_group)
            tengrp = TenureGrp(tenure_group)
            func = FunctionName(function)
            gen = Gender(gender)
            count = Co()
            df2 = pd.DataFrame([{
                'id': count,
                'Experience (YY.MM)': float(experience),
                'Age in YY.': float(age),
                'New Location': int(location_numeric),
                'New Promotion': int(Promoted == 'Yes'),
                'New Job Role Match': int(Job == 'Yes'),
                'Agency': HiringSource[0],
                'Direct': HiringSource[1],
                'Employee Referral': HiringSource[2],
                'Marr.': Maritial_Status[0],
                'Single': Maritial_Status[1],
                'other status': Maritial_Status[2],
                'B1': EmpGrp[0],
                'B2': EmpGrp[1],
                'B3': EmpGrp[2],
                'other group': EmpGrp[3],
                '< =1': tengrp[0],
                '> 1 & < =3': tengrp[1],
                'Operation': func[0],
                'Sales': func[1],
                'Support': func[2],
                'Female': gen[0],
                'Male': gen[1],
                'other': gen[2]
            }])

            df = pd.concat([df, df2], ignore_index=True)
            print("DataFrame for prediction:", df)

            # load the model from disk
            filename = os.path.join(os.path.dirname(__file__), 'finalized_model.pickle')
            loaded_model = pickle.load(open(filename, 'rb'))
            res = loaded_model.predict(df)
            print("Model prediction:", res)

            return res

        else:
            return None
    except Exception as e:
        print("Error in Finder:", str(e))
        print("Traceback:", traceback.format_exc())
        return None

def Co():
    return random.randrange(20, 500)

def HiringPeep(x):
    if str(x) == "Agency":
        return [1, 0, 0] # Agency,Direct, Employee Referral
    elif str(x) == "Direct":
        return [0, 1, 0]
    else:
        return [0, 0, 1]

def MStatus(x):
    if str(x) == "Marr.":
        return [1, 0, 0]
    elif str(x) == "Single":
        return [0, 1, 0]
    else:
        return [0, 0, 1]

def EmployeeGrp(x):
    if str(x) == "B1":
        return [1, 0, 0, 0]
    elif str(x) == "B2":
        return [0, 1, 0, 0]
    elif str(x) == 'B3':
        return [0, 0, 1, 0]
    else:
        return [0, 0, 0, 1]

def TenureGrp(x):
    if str(x) == "<=1":
        return [1, 0, 0]
    elif str(x) == "1-2":
        return [0, 1, 0]
    elif str(x) == "2-5":
        return [0, 0, 1]
    else:  # >5
        return [0, 0, 0]

def FunctionName(x):
    if str(x) == "Operation":
        return [1, 0, 0]
    elif str(x) == "Sales":
        return [0, 1, 0]
    else:
        return [0, 0, 1]

def Gender(x):
    if str(x) == "Female":
        return [1, 0, 0]
    elif str(x) == "Male":
        return [0, 1, 0]
    else:
        return [0, 0, 1]

def inspect_model():
    try:
        # Load the model from disk
        filename = os.path.join(os.path.dirname(__file__), 'finalized_model.pickle')
        loaded_model = pickle.load(open(filename, 'rb'))

        # Check if the model has feature_importances_ attribute
        if hasattr(loaded_model, 'feature_importances_'):
            print("Feature importances:", loaded_model.feature_importances_)
        else:
            print("Model does not have feature_importances_ attribute.")

        # Check if the model has classes_ attribute
        if hasattr(loaded_model, 'classes_'):
            print("Model classes:", loaded_model.classes_)
        else:
            print("Model does not have classes_ attribute.")

        # Check if the model has any other useful attributes
        print("Model parameters:", loaded_model.get_params())

    except Exception as e:
        print("Error inspecting model:", str(e))
        print("Traceback:", traceback.format_exc())

# Call the inspect_model function when the server starts
inspect_model()