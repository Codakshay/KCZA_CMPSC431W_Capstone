# Nittany Business User Authentication

This project is a simple Flask application that provides a single-page interface for user registration and login. Users' passwords are securely hashed using SHA256 and stored in an SQLite database. The application uses flash messages (styled in blue) to give feedback and uses a responsive, modern design with a gradient background and a clean card layout.

## Features

- **User Registration:** New users can register with an email and password.
- **User Login:** Existing users can authenticate with their credentials.
- **Password Hashing:** Passwords are hashed with SHA256 before storage.
- **Flash Messages:** Users receive flash messages styled in blue for registration/login feedback.
- **Single-Page Interface:** Both registration and login forms are available on one page.
- **SQLite Database:** All user data is stored in an `SQLite` database (`nittanybusiness.db`).

## Prerequisites

- Python 3.9
- [Flask](https://flask.palletsprojects.com/)
- SQLite 
## Installation

1. **Clone the Repository or Download the Files:**

   ```bash
   git clone https://github.com/Codakshay/KCZA_CMPSC431W_Capstone.git
   cd NittanyBusinessTest
   
2. **Set up virtual environment and install dependencies**
    ```bash
   python -m venv .venv
    source .venv/bin/activate
   pip install flask
   
3. **Run the application and navigate to browser**
    ```bash
   python app.py
   
## File Structure

    ├── app.py              # Main Flask application
    ├── import_users.py     # Script to import CSV data into the database
    ├── Users.csv           # CSV file with initial user data (plain-text passwords)
    ├── nittanybusiness.db  # SQLite database (auto-created or updated on first run)
    ├── templates           # Folder for HTML templates
    │   └── index.html      # HTML template for the main interface
    └── README.md           # Project documentation

