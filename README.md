# Attrition Predictor

A Django-based application for predicting employee attrition using machine learning.

## Project Structure
```
attrition_project/
├── core/                   # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   └── attrition_predictor/  # Attrition prediction app
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       └── ml/            # Machine learning components
│           └── model/     # Trained model and data
├── static/                # Static files (CSS, JS, Images)
├── templates/            # Project-wide templates
├── data/                # Data files
│   ├── Table_1.csv
│   └── test_data.csv
├── manage.py
└── requirements.txt
```

## Setup and Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Run the development server:
```bash
python manage.py runserver
```

## Features
- Employee attrition prediction using machine learning
- Historical prediction tracking
- Insights and analytics dashboard
- User-friendly interface for data input and analysis

## Data Files
- Table_1.csv: Training data for the model
- test_data.csv: Test data for verification

## Dependencies
See requirements.txt for the full list of dependencies.
