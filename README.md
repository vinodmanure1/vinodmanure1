# Career Guidance Platform MVP

A Django-based Career Guidance Platform that provides assessments, deterministic scoring, and personalized career guidance reports with PDF generation.

## Features

- 🎯 **Career Assessment Tests**: Multi-category skill assessments (Technical, Creative, Analytical, Interpersonal, Leadership)
- 📊 **Deterministic Scoring**: Consistent and transparent scoring system
- 📄 **PDF Report Generation**: Professional PDF reports using WeasyPrint
- 📥 **CSV Import**: Bulk import questions from CSV files
- 🎨 **Admin Interface**: Django admin for managing tests, questions, and users
- 🐳 **Docker Support**: Complete Docker Compose setup with PostgreSQL
- 🧪 **Test Coverage**: Unit tests for core services

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL 15
- **PDF Generation**: WeasyPrint
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/vinodmanure1/vinodmanure1.git
   cd vinodmanure1
   ```

2. **Copy environment file**
   ```bash
   cp .env.example .env
   ```

3. **Build and start containers**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Web Application: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin (username: `admin`, password: `admin123`)
   - Demo User: Auto-login as `demo_student` on first visit

### Without Docker

1. **Install PostgreSQL**
   ```bash
   # Install PostgreSQL 15 and create database
   createdb career_guidance_db
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Run migrations and seed data**
   ```bash
   python manage.py migrate
   python manage.py seed_data
   ```

5. **Start development server**
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
.
├── career_platform/          # Django project settings
│   ├── settings.py          # Main settings
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI configuration
├── assessments/             # Main application
│   ├── models.py            # Data models
│   ├── admin.py             # Admin interface
│   ├── services.py          # Business logic (scoring)
│   ├── api_views.py         # REST API views
│   ├── student_views.py     # Student interface views
│   ├── management/          # Management commands
│   │   └── commands/
│   │       ├── import_questions.py
│   │       └── seed_data.py
│   └── tests/               # Test suite
│       └── test_services.py
├── templates/               # HTML templates
│   ├── base.html
│   └── assessments/
│       ├── student_dashboard.html
│       ├── take_test.html
│       ├── view_report.html
│       └── report.html      # PDF template
├── seed/                    # Seed data
│   ├── question_bank_template.csv
│   └── report_paragraph_mappings.json
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Usage

### For Students

1. Visit http://localhost:8000
2. Auto-login as demo user (or create an account)
3. Select an available test from the dashboard
4. Complete the assessment
5. View your personalized report
6. Download PDF report for offline access

### For Administrators

1. Access admin panel at http://localhost:8000/admin
2. Login with admin credentials
3. Manage:
   - Questions (add, edit, delete)
   - Tests (create new tests, add questions)
   - User profiles
   - Test attempts and results
   - Report paragraph mappings

### Importing Questions

```bash
# Using management command
python manage.py import_questions seed/question_bank_template.csv

# CSV format:
# text,category,option_a,option_b,option_c,option_d,correct_answer
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test assessments.tests.test_services

# With coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## API Endpoints

### REST API

- `GET /api/tests/` - List all active tests
- `GET /api/tests/{id}/` - Get test details with questions
- `POST /api/attempts/start_test/` - Start a new test attempt
- `POST /api/attempts/{id}/submit_answer/` - Submit answer for a question
- `POST /api/attempts/{id}/complete_test/` - Complete test and compute scores

### Student Interface

- `GET /` - Landing page (auto-login)
- `GET /dashboard/` - Student dashboard
- `GET /test/{id}/` - Take a test
- `GET /report/{attempt_id}/` - View report
- `GET /report/{attempt_id}/pdf/` - Download PDF report

## Scoring System

The platform uses a **deterministic scoring system**:

1. Each question belongs to a skill category
2. Answers are evaluated against correct answers
3. Category-wise scores are computed as percentages
4. Overall score is the total correct answers
5. Report paragraphs are matched based on score ranges

## Customization

### Adding New Question Categories

1. Update `CATEGORY_CHOICES` in `assessments/models.py`
2. Add corresponding report mappings in `seed/report_paragraph_mappings.json`
3. Run migrations: `python manage.py migrate`

### Customizing Report Templates

- Edit `templates/assessments/report.html` for PDF layout
- Edit `templates/assessments/view_report.html` for web view
- Modify CSS styles inline for WeasyPrint compatibility

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `True` |
| `SECRET_KEY` | Django secret key | (required) |
| `POSTGRES_DB` | Database name | `career_guidance_db` |
| `POSTGRES_USER` | Database user | `career_user` |
| `POSTGRES_PASSWORD` | Database password | `career_password` |
| `POSTGRES_HOST` | Database host | `db` (Docker) / `localhost` |
| `POSTGRES_PORT` | Database port | `5432` |

## CI/CD

GitHub Actions workflow runs on push/PR to main:
- Sets up PostgreSQL service
- Installs dependencies
- Runs migrations
- Executes test suite
- Security scan with Bandit

## Acceptance Criteria

✅ Complete Django project structure with all required files  
✅ Docker Compose setup with PostgreSQL  
✅ Runnable local development environment  
✅ CSV import for questions  
✅ Deterministic scoring system  
✅ Admin UI for management  
✅ HTML to PDF report generation  
✅ Seed data and sample questions  
✅ Unit tests for services  
✅ CI/CD workflow  
✅ Comprehensive README with quickstart  

## Troubleshooting

### Docker Issues

```bash
# Reset containers
docker-compose down -v
docker-compose up --build

# View logs
docker-compose logs -f web
```

### Database Connection Errors

- Ensure PostgreSQL is running
- Check environment variables in `.env`
- Verify database credentials

### PDF Generation Issues

- WeasyPrint requires system libraries (libpango, etc.)
- Ensure Dockerfile includes required dependencies
- Use inline CSS in templates (external CSS may not load)

## Security Notes

⚠️ **For Development Only**
- Change `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Use strong database passwords
- Configure `ALLOWED_HOSTS` appropriately
- Enable HTTPS in production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run test suite
5. Submit pull request

## License

This is an MVP scaffold for demonstration purposes.

## Support

For issues or questions, please open an issue on GitHub.
