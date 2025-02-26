
# EventTracker and Reporting System with Supervised Learning model

EventTracker is a Django-based application designed to manage events, employee assignments, and reporting within an organization. This system escapulates the essence of what it does through integrating a supervised machine learning model to recommend employees for events based on their skills and performance and standardize reporting to enhances transparency, accountability, and provides valuable insights through comprehensive reporting and real time analytics.In addition, the system incorporate Celery with RabbitMQ for asynchronous email notifications, ensuring that account credentials and assignment details are sent reliably even under intermittent connectivity.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Database Migrations](#database-migrations)
- [Running the Django Server](#running-the-django-server)
- [Celery & RabbitMQ Integration](#celery--rabbitmq-integration)
- [ML Model Training & Integration](#ml-model-training--integration)
- [Email Sending](#email-sending)
- [Usage Flow](#usage-flow)
- [License](#license)

## Features

- **User Authentication:** Secure login system.
- **Event Assignment Management:** Create, assign, and manage events.
- - **ML-Based Recommendations:**  A machine learning model recommends employees for an event based on their skill match and performance.
- **Asynchronous Email Notifications:**  
  Uses Celery with RabbitMQ to send HTML-formatted emails (e.g., account credentials) asynchronously.
- **Event Reporting Interface:** Intuitive interface for reporting activities.
- **Multimedia Support:** Employee writting reports can Upload any relevant file partaining the event. 
- **Report Submission:** Through the employee interface the can write and submit their event reports Online.
- **Review Workflow:** Supervisor/administrator can review the submitted event reports
- **Notification System:** Automated notifications for key actions.
  - Login credentials :- when user is created in the system, automated email is sent carrying user password and email.
  - Password reset request :- when user request a password reset ,automate email is sent with instruction.
  - Assignment and changes if any:- whenever a user is assigned an event to attend, user get notified automatically through email.
- **Search and Filtering:** Admin and users can search  and filter options in the tables in the system.
- **Data Security and Privacy:** User data is encrypted not even the admin can know the user personal information such as password.
- **Analytics and Insights:** System offer a graphical interface for various domains for analytics.
- **Mobile Compatibility:** The system is Mobile responsive making accessible on mobile devices.

## Tech Stack

- **Backend:** Python 3.11, Django 5.1.4  
- **Database:** MySQL  
- **Asynchronous Tasks:** Celery, RabbitMQ  
- **Machine Learning:** scikit-learn, imbalanced-learn (SMOTE) and GradientBoosting Classier 
- **Email Rendering:** Django templating for emails
- 
  ## Project Structure
  EventTracker/ ├── account/ │ ├── models.py │ ├── tasks.py # Celery tasks (e.g., send_credentials_email) │ ├── signals.py # Post-save signals to trigger email tasks │ ├── apps.py # App configuration for auto-discovering signals/tasks │ └── ... ├── employee/ │ ├── models.py # Employee, Department, Skills models │ ├── utils.py # ML recommendation integration │ ├── tasks.py # (Optional) Additional tasks │ └── ... ├── EventRecord/ │ ├── models.py # Event, Assignment, etc. │ └── ... ├── administrator/ │ └── views.py # Admin-related logic ├── templates/ │ ├── account/ │ │ └── password_email.html # HTML email template for credentials │ ├── EventRecord/ │ │ └── assign_event_employee.html # Assignment form modal template │ └── ... ├── ml_models/ # Directory for storing model and preprocessor files │ ├── optimized_recommender.pkl │ └── feature_preprocessor.pkl ├── trainmodel.py # Synthetic data generation script ├── feature_engineering.py # Feature engineering script ├── train_model.py # Model training script ├── celery.py # Celery application configuration ├── manage.py ├── requirements.txt # Python dependencies └── EventTracker/ ├── settings.py # Django settings ├── urls.py ├── wsgi.py └── init.py

## Installation

### Step- by- Step

1. **Clone the repository:**

    ```bash
    git clone https://github.com/JOSEPH-MUGO/
    cd EventTracker
    ```

3. **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    Windows: .event\Scripts\activate
    ```
   

4. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Configure the database settings:**
   Update the `DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'EventTracker',
        'USER': 'root',
        'PASSWORD': 'YourPassword',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}`
 
6. **Configure Email and Celery Settings:**
   ```bash
from decouple import config

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

   ```
7.  **Create `.env` file in the project directory:**
```bash
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
CELERY_BROKER_URL=amqp://guest:guest@localhost//
CELERY_RESULT_BACKEND=rpc://
```
 **Database Migration**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

8. **Create a superuser:**
 Admin
    ```bash
    python3 manage.py createsuperuser
    ```

9. **Start the development server:**

    ```bash
    python3 manage.py runserver
    
    ```Visit http://127.0.0.1:8000/ to see your project a web browser.
## Celery & RabbitMQ Integration
-**Start RabbitMQ**
Download and ensure RabbitMQ is installed and running on your machine.
-**Start Celery Worker**
```bash
celery -A EventTracker worker --pool=solo --loglevel=info
```
-*This starts the worker that processes asynchronous tasks (like sending emails).*

## Usage Flow

### Employee Creation and Authentication:
-Admin creates a new employee through the form.
- The system generates a password and attaches it to the user.
- A post-save signal fires, triggering a Celery task to send a credentials email using password_email.html.
- The email is queued in RabbitMQ and sent by a Celery worker.
- Users can log in using their credentials.
### Event Assignment Management

- A manager opens the "Add new assignment" modal.
- The manager selects an event and department.
- An AJAX call filters the employee dropdown to show only Supervised learning-recommended employees for that event and department.
- The manager selects a recommended employee and completes the assignment.
### Model Training
- The model was trained using a supervised learning approach on synthetic data that we generated to mimic real-world scenarios of employee assignments to events.
### Event Reporting Interface
- Employees report their events activities through a standardized form.
- Reports can include text and multimedia files partaining the event.
- Integrates [Django Summernote](https://github.com/summernote/django-summernote) to allow rich text editing for reports, enabling users to create and edit reports with a user-friendly, WYSIWYG interface.

### Multimedia Support

- Users can upload files as part of their reports.

### Report Submission

- Employees submit their reports online.
- Submitted reports are stored in the system for review and download.

### Review and Download Workflow

- Supervisors review submitted reports and rate the report as performance of the employee.
- Feedback can be provided, and reports can be downloaded.

### Search and Filtering

- Users can search and filter events and reports by their preffered fields data.

### Data Security and Privacy

- The system adheres to data security standards to protect sensitive information of the employees.

### Analytics and Insights

- Graphical tabulation of data in some of system domains, for faster analysis and insight.

### Mobile Compatibility

- The system is responsive and accessible on mobile devices.

## Visuals

### Login Page
![Login Page](EventTracker/static/images/login.png)
### Admin Dashboard
![Event Reporting](EventTracker/static/images/dash.png)
### Graphical interface
![Event Reporting](EventTracker/static/images/dash1.png)
### Event Assignment
![Event Assignment](EventTracker/static/images/event.png)
### Employees
![Event Reporting](EventTracker/static/images/employee.png)
### Employee Reporting Interface
![Event Reporting](EventTracker/static/images/wr.png)
### Event Report
![Event Reporting](EventTracker/static/images/report.png)
### Assigning Event
![Event Reporting](EventTracker/static/images/assign.png)

### Workflow Demonstration
![Workflow video](EventTracker/static/images/system.gif)

## Contributing

Thank you for considering contributing to my project! Contributions are welcomed and encouraged.

### How to Contribute

1. **Fork** the repository and clone it locally.
2. **Set Up** your development environment.
3. **Create** a new branch for your feature or bug fix.
4. **Commit** your changes with descriptive messages.
5. **Push** your branch to your fork.
6. **Open** a pull request (PR) to our main repository.
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the Django community for their excellent framework.
- Special thanks to the team for their dedication and hard work.
### support
- if you need any assistance concerning the project do not hesitate to call me.
```email
josephithanwa@gmail.com
```
