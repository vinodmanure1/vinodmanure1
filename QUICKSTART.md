# Quick Start Guide

This guide will help you get the Career Guidance Platform up and running quickly.

## Prerequisites
- Docker and Docker Compose installed on your system
- Git

## Setup Instructions

### 1. Clone and Setup
```bash
git clone https://github.com/vinodmanure1/vinodmanure1.git
cd vinodmanure1
cp .env.example .env
```

### 2. Build and Start Services
```bash
docker compose up --build -d
```

This will:
- Build the Django application container
- Start PostgreSQL database
- Expose the application on port 8000

### 3. Initialize Database
```bash
# Run migrations
docker compose exec web python manage.py migrate

# Seed database with sample data (creates admin/student users and sample test)
docker compose exec web python manage.py seed_data
```

### 4. Access the Application

- **Student Dashboard**: http://localhost:8000/assessments/
- **Admin Interface**: http://localhost:8000/admin/

### Default Credentials

**Admin User:**
- Username: `admin`
- Password: `admin123`

**Student User:**
- Username: `student`
- Password: `student123`

## Testing the Application

### 1. Take a Test as Student
1. Login as student at http://localhost:8000/admin/login/
2. Navigate to http://localhost:8000/assessments/
3. Click "Take Test" on "Career Aptitude Assessment"
4. Answer questions (they autosave)
5. Submit the test
6. View your report and download PDF

### 2. Manage Tests as Admin
1. Login as admin at http://localhost:8000/admin/
2. Navigate to Assessments section
3. Add/edit Questions
4. Create new Tests
5. View student Attempts

## Running Tests

```bash
# Run all tests
docker compose exec web pytest

# Run with verbose output
docker compose exec web pytest -v
```

## Stopping the Application

```bash
# Stop containers
docker compose down

# Stop and remove volumes (deletes database)
docker compose down -v
```

## Importing Custom Questions

Create a CSV file with the following format:
```csv
text,dimension,weight,order,is_active
"Your question text",analytical,5,1,True
```

Then import:
```bash
docker compose exec web python manage.py import_questions /path/to/your/questions.csv
```

## Troubleshooting

### Database Connection Issues
```bash
# Check if containers are running
docker compose ps

# View logs
docker compose logs web
docker compose logs db
```

### Reset Database
```bash
docker compose down -v
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_data
```

## Next Steps

- Customize questions in `seed/question_bank_template.csv`
- Configure report paragraph mappings in admin
- Add more tests and questions
- Customize templates in `templates/assessments/`

For detailed documentation, see [README.md](README.md)
