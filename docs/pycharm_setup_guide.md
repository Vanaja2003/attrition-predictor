# PyCharm Setup Guide for Attrition Predictor

This guide provides step-by-step instructions for setting up and running the Attrition Predictor project in PyCharm.

## Prerequisites

1. PyCharm Professional or Community Edition installed
2. Python 3.8 or higher installed
3. Git installed (optional, for version control)

## Setup Instructions

### Step 1: Opening the Project

1. Open PyCharm
2. Click on `File` → `Open`
3. Navigate to the `attrition-predictor` folder
4. Click `OK` to open the project

### Step 2: Setting up the Python Interpreter

1. Go to `File` → `Settings` (or `PyCharm` → `Preferences` on macOS)
2. Navigate to `Project: attrition-predictor` → `Python Interpreter`
3. Click the gear icon next to "Python Interpreter" and select "Add"
4. Choose "New Environment" using `virtualenv`
5. Select Python 3.8 or higher as the base interpreter
6. Click `OK` to create the virtual environment

### Step 3: Installing Dependencies

1. Open the terminal in PyCharm (`View` → `Tool Windows` → `Terminal`)
2. Ensure your virtual environment is activated (you should see `(venv)` in the terminal)
3. Run the following command:
   ```bash
   pip install -r requirements.txt
   ```

### Step 4: Database Setup

1. In the terminal, run the following commands:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Step 5: Running the Development Server

1. In the PyCharm terminal, run:
   ```bash
   python manage.py runserver
   ```
2. The server will start at `http://127.0.0.1:8000/`

### Step 6: Setting Up Run Configuration (Optional)

1. Click on `Add Configuration` in the top-right toolbar
2. Click the `+` button and select "Django Server"
3. Name your configuration (e.g., "Django Development Server")
4. Ensure the following settings:
   - Host: 127.0.0.1
   - Port: 8000
   - Python interpreter: Your project's virtual environment
5. Click `OK` to save the configuration

Now you can run/debug the server using the green play button in the toolbar.

## Common Issues and Solutions

### Issue 1: Missing Dependencies
If you see ImportError messages:
1. Ensure your virtual environment is activated
2. Run `pip install -r requirements.txt` again
3. Restart PyCharm

### Issue 2: Database Errors
If you encounter database errors:
1. Delete the `db.sqlite3` file
2. Run migrations again:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Issue 3: Port Already in Use
If port 8000 is already in use:
1. Kill the existing process using the port
2. Or use a different port:
   ```bash
   python manage.py runserver 8001
   ```

## Development Tips

1. Use PyCharm's integrated debugger by setting breakpoints (click left margin of code)
2. Use `Ctrl+Click` (or `Cmd+Click` on macOS) to navigate to definitions
3. Use `Alt+Enter` for quick fixes and suggestions
4. Use `Ctrl+Shift+A` (or `Cmd+Shift+A` on macOS) to search for actions

## Project Structure in PyCharm

- `apps/`: Contains the main application code
- `templates/`: Contains HTML templates
- `static/`: Contains static files (CSS, JS, images)
- `docs/`: Contains project documentation
- `manage.py`: Django management script
- `requirements.txt`: Project dependencies
