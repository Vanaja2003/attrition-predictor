# Attrition Rate Prediction Django Application

## Project Overview
This Django web application is designed to predict employee attrition based on various employee attributes. It uses a machine learning model to make predictions and provides a user-friendly interface for data input.

## Key Features
- **Form Styling**: Modern, clean layout with responsive design and interactive elements.
- **Test Data Population**: Buttons to populate the form with test data for both false and true scenarios.
- **Error Handling**: Robust error handling and debug logging to capture form data and prediction results.

## Dependencies and APIs
- **Django**: Web framework for building the application.
- **Pandas**: For data manipulation.
- **Scikit-learn**: For loading and running the prediction model.

## Setup Instructions
1. **Clone the Repository**: Clone this repository to your local machine.
2. **Install Dependencies**: Run `pip install -r requirements.txt` to install the necessary packages.
3. **Run the Server**: Use `python manage.py runserver` to start the Django server.
4. **Access the Application**: Open `http://127.0.0.1:8000/` in your web browser to access the form.

## Usage Guidelines
- Use the "Fill with Test Data" buttons to populate the form with predefined scenarios.
- Submit the form to receive a prediction on employee attrition.
- Monitor the terminal for any errors or logs.

## Troubleshooting
- Ensure all dependencies are installed and compatible, particularly `scikit-learn`.
- Check console logs for any error messages or warnings.

## Next Steps
- Test the application thoroughly.
- Address any issues that arise during testing.

## License
This project is licensed under the MIT License.
