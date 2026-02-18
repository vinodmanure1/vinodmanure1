# Quick Start Guide

This guide will help you get the Career Guidance Platform up and running in under 5 minutes.

## Prerequisites
- Docker and Docker Compose installed OR
- Python 3.11+ and PostgreSQL 15+

## Option 1: Using Docker (Recommended)

1. **Navigate to the project directory**
   ```bash
   cd career_guidance_platform
   ```

2. **Start the application**
   ```bash
   docker-compose up --build
   ```
   
   Wait for the containers to start. You'll see messages indicating Django is running.

3. **In a new terminal, run setup commands**
   ```bash
   # Run database migrations
   docker-compose exec web python manage.py migrate
   
   # Import sample questions
   docker-compose exec web python manage.py import_questions seed/question_bank_template.csv
   
   # Create admin and student users + sample test
   docker-compose exec web python manage.py seed_data
   ```

4. **Access the application**
   - Main app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin
   
   **Login credentials:**
   - Admin: `admin` / `admin123`
   - Student: `student` / `student123`

## Option 2: Manual Setup

1. **Create and activate virtual environment**
   ```bash
   cd career_guidance_platform
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL**
   - Create database: `CREATE DATABASE career_platform_db;`
   - Copy `.env.example` to `.env` and update credentials

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Import data**
   ```bash
   python manage.py import_questions seed/question_bank_template.csv
   python manage.py seed_data
   ```

6. **Start server**
   ```bash
   python manage.py runserver
   ```

7. **Access at http://localhost:8000**

## Testing the Application

### As a Student
1. Login with `student` / `student123`
2. Go to Dashboard
3. Click "Start Test" on "Career Interest Assessment"
4. Answer questions (scale 0-10)
5. Submit assessment
6. View your report
7. Download PDF report

### As an Administrator
1. Login to admin panel with `admin` / `admin123`
2. Navigate to Questions, Tests, or Attempts
3. Create new tests, add questions
4. Upload questions via CSV import

## Running Tests

```bash
# With Docker
docker-compose exec web pytest

# Without Docker
pytest
```

## Common Issues

**Port already in use:**
- Change ports in `docker-compose.yml`

**Database connection error:**
- Ensure PostgreSQL is running
- Check `.env` credentials

**PDF generation fails:**
- System dependencies for WeasyPrint may be missing
- Docker includes these automatically

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize questions in `seed/question_bank_template.csv`
- Modify report template in `templates/assessments/report.html`
- Add custom dimensions and scoring logic in `assessments/services.py`
