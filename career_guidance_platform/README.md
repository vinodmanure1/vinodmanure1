# Career Guidance Platform MVP

A Django-based Career Guidance Platform that provides students with comprehensive assessments to discover their career interests and strengths.

## Features

- 🎯 **Student Assessments**: Interactive questionnaire with timer and autosave
- 📊 **Scoring Engine**: Deterministic scoring across multiple career dimensions
- 📄 **PDF Reports**: Professional A4-formatted reports with WeasyPrint
- 👨‍💼 **Admin Interface**: Django admin for managing tests, questions, and viewing results
- 📥 **CSV Import**: Bulk import questions via management command or API
- 🧪 **Test Suite**: Comprehensive pytest-django tests
- 🐳 **Docker Support**: Complete Docker Compose setup for local development
- 🔄 **CI/CD**: GitHub Actions workflow for automated testing

## Technology Stack

- **Backend**: Django 4.2+, Django REST Framework
- **Database**: PostgreSQL 15
- **PDF Generation**: WeasyPrint
- **Testing**: pytest-django
- **Containerization**: Docker & Docker Compose
- **Deployment**: Gunicorn WSGI server

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd career_guidance_platform
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` if needed for your local environment.

3. **Build and start containers**
   ```bash
   docker-compose up --build
   ```
   
   This will:
   - Build the Django application container
   - Start PostgreSQL database
   - Expose the app on http://localhost:8000

4. **Run migrations** (in a new terminal)
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Import sample questions**
   ```bash
   docker-compose exec web python manage.py import_questions seed/question_bank_template.csv
   ```

6. **Seed initial data** (creates admin user and sample test)
   ```bash
   docker-compose exec web python manage.py seed_data
   ```
   
   Default credentials:
   - Admin: `admin` / `admin123`
   - Student: `student` / `student123`

7. **Access the application**
   - Main app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Manual Setup (Without Docker)

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database**
   Create a database named `career_platform_db` and update `.env` with credentials.

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Import questions**
   ```bash
   python manage.py import_questions seed/question_bank_template.csv
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Usage Guide

### For Students

1. **Login**: Navigate to http://localhost:8000 and login with student credentials
2. **Dashboard**: View available tests and past attempts
3. **Take Test**: 
   - Click "Start Test" on any available assessment
   - Answer questions on a scale of 0-10
   - Progress is auto-saved every 2 seconds
   - Submit when complete (or timer expires)
4. **View Results**: See your scores across different career dimensions
5. **Download Report**: Get a professional PDF report with recommendations

### For Administrators

1. **Login**: Access http://localhost:8000/admin with admin credentials
2. **Manage Questions**: 
   - Add/edit individual questions
   - Import bulk questions via CSV (use import_export feature)
3. **Create Tests**:
   - Create new test
   - Add questions using inline TestQuestion editor
   - Set duration and activate test
4. **View Attempts**: Monitor student attempts and scores
5. **API Upload**: Use the admin API endpoint at `/api/admin/upload-csv/` for programmatic CSV uploads

### CSV Import Format

Questions CSV should have the following format:

```csv
text,dimension,weight
How comfortable are you with programming?,Technical,1.0
Do you enjoy leading teams?,Leadership,1.5
Are you creative?,Creative,1.0
```

**Fields**:
- `text` (required): The question text
- `dimension` (required): Career dimension (e.g., Technical, Leadership, Creative)
- `weight` (optional): Question weight for scoring, defaults to 1.0

## API Endpoints

### Student Endpoints
- `GET /` - Home page
- `GET /dashboard/` - Student dashboard
- `GET /test/<id>/take/` - Take a test
- `POST /attempt/<id>/save/` - Autosave progress
- `POST /attempt/<id>/submit/` - Submit attempt
- `GET /attempt/<id>/report/` - View report (HTML)
- `GET /attempt/<id>/pdf/` - Download PDF report

### Admin API
- `POST /api/admin/upload-csv/` - Upload questions CSV (requires admin authentication)

## Running Tests

### With Docker
```bash
docker-compose exec web pytest
```

### Without Docker
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_scoring.py
```

### Run with coverage
```bash
pytest --cov=assessments --cov-report=html
```

## Project Structure

```
career_guidance_platform/
├── career_platform/           # Django project settings
│   ├── __init__.py
│   ├── settings.py           # Main settings
│   ├── urls.py               # URL routing
│   ├── wsgi.py               # WSGI config
│   └── asgi.py               # ASGI config
├── assessments/              # Main application
│   ├── models.py             # Data models
│   ├── views.py              # Views and API endpoints
│   ├── admin.py              # Admin configuration
│   ├── services.py           # Scoring engine
│   ├── utils.py              # CSV import utilities
│   ├── urls.py               # App URLs
│   └── management/
│       └── commands/
│           ├── import_questions.py
│           └── seed_data.py
├── templates/                # HTML templates
│   ├── base.html
│   └── assessments/
│       ├── home.html
│       ├── dashboard.html
│       ├── take_test.html
│       └── report.html
├── tests/                    # Test suite
│   ├── test_scoring.py
│   ├── test_csv_import.py
│   └── test_api.py
├── seed/                     # Seed data
│   └── question_bank_template.csv
├── static/                   # Static files
├── media/                    # User uploads (PDFs)
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose config
├── requirements.txt         # Python dependencies
├── pytest.ini              # Pytest configuration
├── manage.py               # Django management script
└── README.md               # This file
```

## Models

### Question
Stores individual assessment questions with dimension and weight.

### Test
Represents a complete assessment with title, description, and duration.

### TestQuestion
Links questions to tests with ordering.

### Profile
Extended user profile for students (OneToOne with User).

### Attempt
Records a student's test attempt with answers and computed scores.

### ReportParagraphMapping
Maps score ranges to report text for personalized feedback.

## Scoring Algorithm

The scoring engine (`assessments/services.py`) implements:

1. **Dimension Scoring**: 
   - Groups questions by career dimension
   - Calculates weighted average per dimension
   - Normalizes to 0-100 scale

2. **Total Score**: 
   - Average of all dimension scores

3. **Top Dimensions**: 
   - Sorts dimensions by score
   - Returns top 3 for recommendations

## Development

### Adding New Questions
```bash
# Via management command
python manage.py import_questions path/to/questions.csv

# Via Django admin
# Navigate to Questions → Import
```

### Creating a Test
1. Go to Django admin → Tests → Add test
2. Fill in title, description, duration
3. Add questions using the TestQuestion inline formset
4. Set "Is active" to True
5. Save

### Customizing Reports
Edit `templates/assessments/report.html` to modify the PDF report layout and content.

## Deployment Considerations

For production deployment:

1. **Security**:
   - Change `SECRET_KEY` to a strong random value
   - Set `DEBUG=False`
   - Configure `ALLOWED_HOSTS`
   - Use environment variables for sensitive data

2. **Database**:
   - Use managed PostgreSQL service
   - Enable SSL connections
   - Regular backups

3. **Static Files**:
   - Run `python manage.py collectstatic`
   - Serve via Nginx or CDN

4. **Media Files**:
   - Consider cloud storage (S3, etc.)
   - Implement proper access controls

5. **WSGI Server**:
   - Use Gunicorn (included) or uWSGI
   - Configure worker count based on CPU cores

6. **Reverse Proxy**:
   - Use Nginx or Apache
   - Configure SSL/TLS certificates

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running: `docker-compose ps`
- Check environment variables in `.env`
- Verify network connectivity

### WeasyPrint PDF Generation Fails
- Ensure system dependencies are installed (libcairo, libpango)
- Check template rendering without PDF generation first

### Tests Failing
- Run migrations: `python manage.py migrate`
- Clear test database: `pytest --create-db`

### Port Already in Use
- Stop existing services on port 8000/5432
- Or change ports in `docker-compose.yml`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Ensure tests pass: `pytest`
6. Submit a pull request

## License

This project is provided as-is for educational and development purposes.

## Support

For issues and questions, please open an issue in the GitHub repository.
