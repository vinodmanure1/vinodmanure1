# Career Guidance Platform

A Django-based web application for career assessment and guidance. This platform helps students and professionals discover their ideal career paths through comprehensive assessments, scoring algorithms, and detailed career recommendations.

## Features

- **Career Assessment System**: Interactive questionnaires to evaluate interests, skills, and preferences
- **Intelligent Scoring**: Algorithm-based career matching system
- **Career Database**: Comprehensive information on various career paths including salary, growth rate, and education requirements
- **PDF Reports**: Downloadable assessment results (placeholder implementation)
- **REST API**: JSON API endpoints for integration with other systems
- **Admin Interface**: Django admin for managing careers, assessments, questions, and answers
- **Docker Support**: Containerized deployment for easy setup and scaling

## Tech Stack

- **Backend**: Django 4.2
- **Database**: PostgreSQL 15
- **Containerization**: Docker & Docker Compose
- **Web Server**: Gunicorn
- **Python**: 3.11

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

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration (optional for local development)
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Web Interface: http://localhost:8000
   - Admin Interface: http://localhost:8000/admin
   - Default admin credentials: `admin` / `admin123`

The application will automatically:
- Run database migrations
- Import seed data (careers and assessment)
- Create a superuser account

## Manual Setup (Without Docker)

1. **Install dependencies**
   ```bash
   cd career_platform
   pip install -r ../requirements.txt
   ```

2. **Configure database**
   - Install PostgreSQL
   - Create database: `career_platform`
   - Update `career_platform/settings.py` with your database credentials

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Import seed data**
   ```bash
   python manage.py import_seed_data
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
career_platform/
├── career_platform/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── assessments/              # Main application
│   ├── models.py            # Career, Assessment, Question, Answer, Result
│   ├── admin.py             # Admin configuration
│   ├── views.py             # Student views
│   ├── api_views.py         # REST API endpoints
│   ├── services.py          # Business logic (scoring)
│   ├── urls.py              # URL routing
│   ├── tests.py             # Unit tests
│   ├── templates/           # HTML templates
│   └── management/
│       └── commands/
│           └── import_seed_data.py  # Data import command
├── seed_data/
│   ├── careers.csv          # Career data
│   └── assessment.json      # Assessment questions and answers
└── manage.py
```

## API Endpoints

### List Assessments
```http
GET /api/assessments/
```

### Get Assessment Details
```http
GET /api/assessment/{id}/
```

### Submit Assessment
```http
POST /api/submit/
Content-Type: application/json

{
  "assessment_id": 1,
  "responses": {
    "1": 5,
    "2": 8
  },
  "student_name": "John Doe",
  "student_email": "john@example.com"
}
```

### List Results
```http
GET /api/results/
```

## Management Commands

### Import Seed Data
```bash
# Import default seed data
python manage.py import_seed_data

# Import specific files
python manage.py import_seed_data --careers path/to/careers.csv --assessment path/to/assessment.json
```

## Running Tests

```bash
cd career_platform
python manage.py test assessments
```

## Data Models

### Career
- Name, description, industry
- Average salary, growth rate
- Education requirements

### Assessment
- Title, description
- Duration
- Active status

### Question
- Assessment reference
- Question text
- Type (Multiple Choice, Rating, Text)
- Order

### Answer
- Question reference
- Answer text
- Career association
- Score value
- Order

### Result
- User/Student information
- Assessment reference
- Recommended career
- Score details (JSON)
- Responses (JSON)
- Completion timestamp

## Development

### Adding New Careers

1. Via Admin Interface: http://localhost:8000/admin/assessments/career/
2. Via CSV import: Update `seed_data/careers.csv` and run `import_seed_data` command
3. Via Django shell:
   ```python
   python manage.py shell
   from assessments.models import Career
   Career.objects.create(name='New Career', description='...', industry='...')
   ```

### Creating New Assessments

1. Via Admin Interface: http://localhost:8000/admin/assessments/assessment/
2. Via JSON import: Create JSON file and run `import_seed_data` command

## Security Notes

- **SECRET_KEY**: Change the default secret key in production
- **DEBUG**: Set to `False` in production
- **ALLOWED_HOSTS**: Configure appropriate hosts for production
- **Database Passwords**: Use strong passwords in production
- No secrets are committed to the repository

## CI/CD

GitHub Actions workflow is configured to:
- Run linting checks
- Execute unit tests
- Build Docker image
- Check for security vulnerabilities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

## Roadmap

- [ ] Enhanced PDF report generation with charts
- [ ] User authentication and profile management
- [ ] Email notifications for results
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Mobile application
- [ ] Integration with job boards
- [ ] Career counseling scheduling
