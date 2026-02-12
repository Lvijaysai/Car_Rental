
# 🚗 Budget Car Rentals - Full Stack Application

A modern, full-stack car rental platform built with **Django REST Framework** and **React (Vite)**. This application allows users to browse a vehicle fleet, make hourly or daily bookings, and manage their rental history, while providing administrators with a dashboard to manage cars and reservations.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![React](https://img.shields.io/badge/React-18-blue)

## 🌟 Features

* **Fleet Management:** Browse cars with advanced filtering (availability, transmission, fuel type).
* **Flexible Booking System:** Support for both **12-Hour Shifts** and **Daily Rentals**.
* **Real-time Availability:** Smart filtering prevents booking cars that are already rented or under maintenance.
* **User Dashboard:** View active bookings and rental history.
* **Secure Authentication:** Session-based authentication with CSRF protection (HttpOnly cookies).
* **Admin Panel:** Full control over fleet inventory, booking approvals, and user management.

## 🛠️ Tech Stack

### Backend
* **Framework:** Django & Django REST Framework (DRF)
* **Security:** `python-decouple` for environment variable management.
* **Database:** SQLite (Development) / PostgreSQL (Production ready).
* **API:** RESTful API with Axios integration.

### Frontend
* **Framework:** React (via Vite).
* **Styling:** Tailwind CSS.
* **State Management:** React Context API (Auth).
* **Routing:** React Router v6.

---

## 🚀 Getting Started

Follow these instructions to set up the project locally.

### Prerequisites
* Python 3.10+
* Node.js & npm

### 1. Backend Setup (Django)

```bash
# Clone the repository
git clone <your-repo-url>
cd Car_Rental

# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt

# Create .env file (See Configuration section below)
# Run Migrations
python manage.py makemigrations
python manage.py migrate

# Create Admin User
python manage.py createsuperuser

# Start Server
python manage.py runserver

```

### 2. Frontend Setup (React)

Open a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Development Server
npm run dev

```

The frontend will run at `http://localhost:5173`.

---

## ⚙️ Configuration (.env)

**Security Note:** This project uses `python-decouple`. You must create a `.env` file in the `backend/` folder.

Copy the `backend/.env.example` file to `backend/.env` and update the values:

```ini
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://localhost:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173

```

---

## 📂 Project Structure

```
Car_Rental/
├── backend/            # Django API
│   ├── bookings/       # Booking logic & Math
│   ├── fleet/          # Car inventory management
│   ├── config/         # Settings & URLs
│   └── ...
├── frontend/           # React App
│   ├── src/
│   │   ├── api/        # Axios & Endpoints
│   │   ├── components/ # Reusable UI
│   │   ├── pages/      # Route views
│   └── ...
└── requirements.txt    # Python dependencies

```

## 🛡️ Security Measures

* **CSRF Protection:** The frontend implements the "Double Submit Cookie" pattern to securely handle CSRF tokens without storing sensitive data in LocalStorage.
* **Environment Variables:** Sensitive keys are strictly separated from the codebase using `.env`.
* **Input Validation:** Backend enforces strict date logic validation (e.g., preventing past dates or negative durations) to maintain data integrity.

---

### 3. `setup_instructions.txt`

This is for **YOU** (or a team member) to use right now to verify the project works before you commit. You can keep this in your root folder or delete it after you are done.

```text
=== CAR RENTAL PROJECT SETUP GUIDE ===

STEP 1: DATABASE INITIALIZATION
1. Open terminal in 'backend/' folder.
2. Ensure venv is active: `venv\Scripts\activate`
3. Delete old db.sqlite3 (if it exists and is corrupted).
4. Run: `python manage.py makemigrations`
5. Run: `python manage.py migrate`
6. Run: `python manage.py createsuperuser`
   - Username: admin
   - Email: admin@example.com
   - Password: admin (or whatever you choose)

STEP 2: ADDING DUMMY DATA
1. Run backend: `python manage.py runserver`
2. Go to: http://127.0.0.1:8000/admin/
3. Login with superuser.
4. Click "Categories" -> Add "SUV", "Sedan", "Luxury".
5. Click "Cars" -> Add 2-3 cars.
   - Make sure to upload images (even dummy ones) or the frontend might look empty.
   - Set Status to "Available".

STEP 3: FRONTEND VERIFICATION
1. Open new terminal in 'frontend/' folder.
2. Run: `npm run dev`
3. Go to: http://localhost:5173
4. Check: Do you see the cars you added?
5. Check: Click "Login" -> Login as the 'admin' user you created.
6. Check: Click a car -> Try to book it. 
   - If you get a "Success" screen, the API is working perfectly.

```

