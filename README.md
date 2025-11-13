# File Share Project (development scaffold)

This is a minimal Django scaffold with:
- User registration, login with **email OTP** (console email backend by default)
- File upload, download, delete
- Shareable public link (UUID)
- Admin panel (create superuser to access)

## Setup (development)
1. Create virtualenv and install Django:
   ```bash
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   pip install django
   ```
2. Run migrations:
   ```bash
   python manage.py migrate
   ```
3. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```
4. Run server:
   ```bash
   python manage.py runserver
   ```
5. Register a user and test login. When logging in, an OTP is printed to the console (development).

## Important notes
- EMAIL_BACKEND uses the console backend for development. Configure SMTP in `file_sharing_project/settings.py` for real emails.
- This scaffold is intended as a starting point. Add stricter validation, file size limits, virus scanning, storage backends (S3) for production.
