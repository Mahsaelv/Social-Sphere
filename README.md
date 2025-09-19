# SocialSphere

A modern social media platform built with **Django**, providing features such as user authentication, posting, commenting, following, and media management. The project is designed with a focus on **security**, **scalability**, and **clean architecture**.

---

## 🚀 Features

- User authentication (register, login, logout, password reset/change)
- Email verification for account activation
- Create, edit, and delete posts with images and tags
- Search users, tags
- send private message
- Like, save, and comment on posts
- Follow/unfollow users
- Rate-limiting login attempts with **django-axes**


---

## 🛠️ Tech Stack

- **Backend:** Django 5, Django REST Framework
- **Database:** MySQL
- **Frontend:** Django Templates
- **Other Tools:** django-taggit, django-axes, debug-toolbar (dev only)

---

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Mahsaelv/Social-Sphere.git
   cd socialsphere
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate 
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following variables:
   ```env
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   DB_NAME=socialmedia
   DB_USER=root
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_email_password
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```
