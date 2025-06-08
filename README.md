# Akteco School Attendance System

This is a Django-based backend system integrated with ZKTeco biometric devices for managing attendance in multiple schools. It features multi-level user roles and secure attendance tracking.

---

## Project Overview

The Akteco School Attendance System is designed to manage biometric attendance data collected from ZKTeco devices. The system supports a hierarchy of users:

- **SuperAdmin:** The main administrator who manages multiple schools and their admins.
- **School Admin:** Manages staff and students within a specific school.
- **Staff & Students:** Can log in to view their own attendance records.

---

## Features

- Multi-school support with separate school admins
- User roles with access control (SuperAdmin, School Admin, Staff, Student)
- Integration with ZKTeco biometric devices for face and fingerprint recognition
- Attendance record management (view, add, edit, delete)
- REST API endpoints for Flutter frontend integration
- Secure authentication and authorization
- Detailed user management and role assignments

---

## Technology Stack

- **Backend:** Python, Django, Django REST Framework
- **Frontend:** Flutter
- **Database:** SQLite
- **Biometric Devices:** ZKTeco face & fingerprint devices
- **Others:** JWT authentication

---

## Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd zkteco-school-attendance

2. **Create a virtual environment and activate it:**

   ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies:**

   ```bash
    pip install -r requirements.txt
   
4. **Run migrations:**

   ```bash
   python manage.py migrate

   

5. **Create superuser:**

   ```bash
   python manage.py createsuperuser

6. **Run the development server:**

   ```bash
   python manage.py runserver
