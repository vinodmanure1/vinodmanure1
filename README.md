# Career Guidance Platform MVP

A Django-based career guidance platform for assessing student aptitudes and generating personalized reports.

## Features

- 🎯 Multi-dimensional aptitude assessments
- 📊 Automated scoring engine with normalized scores
- 📄 PDF report generation with WeasyPrint
- 👨‍💼 Admin interface for managing tests and questions
- 📁 CSV import for bulk question uploads
- ⏱️ Timed tests with autosave functionality
- 🔒 User authentication and authorization
- 🐳 Docker-based development environment

## Tech Stack

- **Backend**: Django 4.2+
- **Database**: PostgreSQL 15
- **API**: Django REST Framework
- **PDF Generation**: WeasyPrint
- **Testing**: pytest-django
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/vinodmanure1/vinodmanure1.git
cd vinodmanure1
```

2. **Copy environment variables**
```bash
cp .env.example .env
```

3. **Build and start containers**
```bash
docker-compose up --build
```

4. **In a new terminal, run migrations**
```bash
docker-compose exec web python manage.py migrate
```

5. **Seed the database with sample data**
```bash
docker-compose exec web python manage.py seed_data
```

This will create:
- Admin user (username: `admin`, password: `admin123`)
- Student user (username: `student`, password: `student123`)
- Sample questions from CSV
- A sample test with all questions
- Report paragraph mappings

6. **Access the application**
- Student Dashboard: http://localhost:8000/assessments/
- Admin Interface: http://localhost:8000/admin/

## Manual Setup (Alternative to seed_data)

If you prefer to set up manually:

1. **Create superuser**
```bash
docker-compose exec web python manage.py createsuperuser
```

2. **Import questions from CSV**
```bash
docker-compose exec web python manage.py import_questions seed/question_bank_template.csv
```

3. **Login to admin** (http://localhost:8000/admin/)
   - Create a Test
   - Add questions to the test
   - Create report paragraph mappings

## Usage

### Student Flow

1. Login with student credentials
2. View available tests on the dashboard
3. Click "Take Test" to start an assessment
4. Answer questions (autosaved automatically)
5. Submit the test to get scores
6. View the report and download PDF

### Admin Flow

1. Login to admin interface
2. Manage Questions, Tests, and Test configurations
3. Upload CSV files via admin or API endpoint
4. View student attempts and scores
5. Configure report paragraph mappings for different score ranges

## API Endpoints

### Submit Attempt
```
POST /assessments/api/submit/
Content-Type: application/json
Authorization: Session or Token

{
  "test_id": 1,
  "answers": {
    "1": 5,
    "2": 4,
    "3": 3
  }
}
```

### CSV Upload (Admin only)
```
POST /assessments/api/csv-upload/
Content-Type: multipart/form-data
Authorization: Admin credentials

file: questions.csv
```

### Generate PDF Report
```
GET /assessments/api/report/{attempt_id}/pdf/
Authorization: Session or Token
```

## CSV Format for Questions

The CSV file should have the following columns:

```csv
text,dimension,weight,order,is_active
"I enjoy solving complex problems",analytical,5,1,True
"I like creative activities",creative,4,2,True
```

**Columns:**
- `text`: Question text
- `dimension`: One of: analytical, creative, practical, social, leadership, technical
- `weight`: Question weight (1-10)
- `order`: Display order
- `is_active`: True or False

## Running Tests

```bash
# Run all tests
docker-compose exec web pytest

# Run with verbose output
docker-compose exec web pytest -v

# Run specific test file
docker-compose exec web pytest assessments/tests.py

# Run specific test class
docker-compose exec web pytest assessments/tests.py::TestComputeScores
```

## Development

### Project Structure

```
.
├── assessments/              # Main Django app
│   ├── management/          # Management commands
│   │   └── commands/
│   │       ├── import_questions.py
│   │       └── seed_data.py
│   ├── migrations/          # Database migrations
│   ├── admin.py            # Admin configuration
│   ├── models.py           # Data models
│   ├── serializers.py      # DRF serializers
│   ├── services.py         # Business logic (scoring)
│   ├── tests.py            # Test suite
│   ├── urls.py             # URL routing
│   └── views.py            # Views and API endpoints
├── career_platform/         # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/              # HTML templates
│   ├── base.html
│   └── assessments/
│       ├── student_dashboard.html
│       ├── take_test.html
│       └── report.html
├── seed/                   # Seed data
│   └── question_bank_template.csv
├── .github/workflows/      # CI/CD
│   └── ci.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### Models

- **Question**: Assessment questions with dimension and weight
- **Test**: Collection of questions
- **TestQuestion**: M2M through model for Test-Question relationship
- **Attempt**: User's test attempt with answers and scores
- **Profile**: Extended user profile
- **ReportParagraphMapping**: Score range to report text mapping

### Scoring Engine

The scoring engine (`assessments/services.py`) computes:
- **Dimension Scores**: Normalized 0-100 scores per dimension
- **Total Score**: Average of all dimension scores
- **Top Dimensions**: Top 3 performing dimensions
- **Raw Scores**: Pre-normalization scores for debugging

Formula:
```
dimension_score = (sum of weighted answers / sum of max possible scores) * 100
```

## Deployment Considerations

For production deployment:

1. **Update environment variables**
   - Set `DEBUG=False`
   - Use a strong `SECRET_KEY`
   - Configure proper database credentials
   - Set `ALLOWED_HOSTS`

2. **Use gunicorn**
```bash
gunicorn career_platform.wsgi:application --bind 0.0.0.0:8000
```

3. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

4. **Set up proper media file storage** (AWS S3, etc.)

5. **Configure HTTPS** and security headers

## CI/CD

The project includes GitHub Actions workflow that:
- Runs on push to main, develop, and copilot branches
- Sets up PostgreSQL service
- Installs dependencies
- Runs migrations
- Executes test suite

## Troubleshooting

### Database Connection Issues
```bash
# Check if postgres is running
docker-compose ps

# View logs
docker-compose logs db
```

### Migration Issues
```bash
# Reset migrations (development only!)
docker-compose exec web python manage.py migrate assessments zero
docker-compose exec web python manage.py migrate
```

### Permission Issues
```bash
# Fix media directory permissions
docker-compose exec web chmod -R 755 /app/media
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests for your changes
5. Run the test suite
6. Submit a pull request

## License

This project is provided as-is for educational purposes.

## Support

For issues and questions, please open an issue on GitHub.
