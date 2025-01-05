from django.shortcuts import render, redirect
import pandas as pd
import pickle, os, random
import traceback
from django.http import HttpResponse

def home(request):
    return render(request, 'home.html')

# Finding attrition rate:
def Attrition_rate_finder(request):
    results = None  # Initialize results at the start of the function
    try:
        print("Method:", request.method)  # Debug print
        if request.method == 'POST':
            print("POST data:", request.POST)  # Debug print
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
                Promoted = '1' if Promoted == 'Yes' else '0'
                Job = '1' if Job == 'Yes' else '0'

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
                location = location_map.get(location, '1')  # Default to '1' if location not found

                prediction = Finder(name, location, emp_group, function, gender, tenure_group,
                                          experience, age, Maritial, Hiring, Promoted, Job)
                print("Prediction results:", prediction)  # Debug print
                
                if prediction is not None:
                    results = "Yes" if prediction[0] else "No"
                    print("Final results:", results)  # Debug print
                else:
                    print("Prediction returned None")  # Debug print
                    results = None
            else:
                print('Attrition button not found in POST data')  # Debug print

        return render(request, 'attrition_form.html', {'result': results})
    except Exception as e:
        print("Error in Attrition_rate_finder:", str(e))
        print("Traceback:", traceback.format_exc())
        return render(request, 'attrition_form.html', {'result': None, 'error': str(e)})

def Finder(name, location, emp_group, function, gender, tenure_group,
                                  experience, age, Maritial, Hiring, Promoted, Job):
    try:
        if name != "":
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
                'New Location': int(location),
                'New Promotion': int(Promoted),
                'New Job Role Match': int(Job),
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
    if str(x) == "< =1":
        return [1, 0]
    else:
        return [0, 1]

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