# Personal Finance Tracker

A full-stack Personal Finance Tracker Web Application using Django and Bootstrap.

## Features

- **🔐 User Authentication**: Secure Sign Up, Login, and Logout.
- **📊 Dashboard**: Monthly income/expense summary with Chart.js visualizations.
- **💳 Transaction Management**: Add, Edit, Delete, and Categorize transactions.
- **🌙 Dark/Light Mode**: Toggleable interface theme.
- **🔔 Budget Alerts**: Set monthly limits and get notified when you overspend.
- **📱 Payment Integration (Simulated)**: Import mock transactions from PhonePe/GPay.

## Tech Stack

- **Backend**: Python, Django 5.x
- **Frontend**: HTML5, Bootstrap 5.3, JavaScript, Chart.js
- **Database**: SQLite (default) / PostgreSQL compatible
- **Tools**: Git, FontAwesome

## Setup Instructions

1.  **Clone the Repository** (if applicable) or navigate to the project folder.

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Apply Database Migrations**:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

4.  **Seed Initial Categories** (Optional but recommended):
    ```bash
    python seed_data.py
    ```

5.  **Run the Server**:
    ```bash
    python manage.py runserver
    ```

6.  **Access the App**:
    Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## Usage

1.  **Register** a new account.
2.  **Add Transactions**: Go to the "Transactions" page or use "Add Transaction".
3.  **Set Budget**: Click "Set Budget" on the dashboard to define your monthly limit.
4.  **Simulate Import**: Use "Import Data" in the sidebar to add dummy transactions.
5.  **Toggle Theme**: Click the moon/sun icon in the navbar.
