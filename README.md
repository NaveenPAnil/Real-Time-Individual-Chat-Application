# Premium Chat Application

A real-time, professional chat application built with Django, Channels, and a premium teal-themed UI.

## Features
- **Real-Time Messaging**: Instant message delivery using WebSockets (Django Channels).
- **User Presence**: Real-time "Online" status and "Last Seen" tracking.
- **File Sharing**: Capability to send and receive files within chat rooms.
- **Emoji Support**: Integrated emoji picker for expressive communication.
- **Identity & Auth**: Full registration and login system with email verification (via Allauth).
- **Premium Design System**: A cohesive, professional teal aesthetic with smooth animations and responsive layouts.

## Prerequisite
- Python 3.10+
- pip (Python package manager)

## Installation Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ZYBOTECH_TVM/src/chatapp
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**:
   Create a `.env` file in the `src/chatapp` directory (or use the existing one) with the following variables:
   ```env
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password
   EMAIL_USE_TLS=True
   ```

## Setup Steps

1. **Apply Migrations**:
   Prepare the database schema.
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Create a Superuser** (Optional):
   To access the Django admin panel.
   ```bash
   python manage.py createsuperuser
   ```

3. **Collect Static Files**:
   ```bash
   python manage.py collectstatic --noinput
   ```

## How to Run the Project

1. **Start the Development Server**:
   The project uses `daphne` as the ASGI server to handle both HTTP and WebSocket traffic.
   ```bash
   python manage.py runserver
   ```

2. **Access the Application**:
   Open your browser and navigate to:
   `http://127.0.0.1:8000/`

## Technology Stack
- **Backend**: Django, Django Channels (WebSockets)
- **Frontend**: HTML5, Vanilla CSS, Bootstrap 5, Font Awesome
- **Database**: SQLite (default)
- **Real-time**: ASGI (Daphne)
- **Auth**: Django Allauth