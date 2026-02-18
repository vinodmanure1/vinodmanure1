# Career Guidance Platform MVP

A Django-based Career Guidance Platform that provides comprehensive career assessments with deterministic scoring, PDF report generation, and admin management tools.

## Features

- **Student Assessment Portal**: Take career aptitude tests with timer and autosave
- **Deterministic Scoring Engine**: Normalized 0-100 scores per career dimension
- **PDF Report Generation**: HTML-to-PDF reports using WeasyPrint
- **Admin Dashboard**: Full Django admin with CSV import/export
- **REST API**: DRF endpoints for test submission and data management
- **Docker Support**: Containerized setup with Docker Compose
- **Automated Tests**: Pytest test suite with CI/CD via GitHub Actions

## Technology Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL 15
- **PDF Generation**: WeasyPrint
- **Testing**: pytest, pytest-django
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/vinodmanure1/vinodmanure1.git
   cd vinodmanure1
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` if needed (defaults work for local development)

3. **Build and start services**
   ```bash
   docker-compose up --build
   ```
   
   This will:
   - Build the Django application container
   - Start PostgreSQL database
   - Expose the application on http://localhost:8000

4. **In a new terminal, run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```
   
   Or use the seeded admin user:
   - Username: `admin`
   - Password: `admin123`

6. **Import sample questions**
   ```bash
   docker-compose exec web python manage.py import_questions seed/question_bank_template.csv
   ```

7. **Seed the database**
   ```bash
   docker-compose exec web python manage.py seed_data
   ```
   
   This creates:
   - Admin user (if not exists): `admin` / `admin123`
   - Sample test with all imported questions
   - Report paragraph mappings

8. **Access the application**
   - Student Dashboard: http://localhost:8000/
   - Admin Interface: http://localhost:8000/admin/
   - API Root: http://localhost:8000/assessments/api/

## Usage Guide

### For Students

1. **Login**: Navigate to http://localhost:8000/ and login
2. **Take Test**: Click "Take Test" on any available assessment
3. **Answer Questions**: Rate each statement on a 1-5 scale
4. **Submit**: Click "Submit Test" when complete
5. **View Report**: See your scores and download PDF report

### For Admins

1. **Login to Admin**: http://localhost:8000/admin/
2. **Manage Questions**: Add/edit questions via admin or CSV upload
3. **Create Tests**: Create tests and link questions
4. **View Attempts**: Monitor student submissions and scores
5. **CSV Import**: 
   - Via command: `docker-compose exec web python manage.py import_questions <csv_file>`
   - Via API: POST to `/assessments/api/upload-csv/` with file upload

### CSV Format for Questions

Create a CSV file with these columns:

```csv
text,dimension,weight
"I enjoy solving complex technical problems",technical,1.0
"I think outside the box to find solutions",creative,1.0
"I excel at analyzing data and patterns",analytical,1.0
"I am comfortable leading teams",leadership,1.0
"I communicate effectively",communication,1.0
```

**Valid dimensions**: `technical`, `creative`, `analytical`, `leadership`, `communication`

## API Endpoints

### Public Endpoints (require authentication)

- `GET /assessments/api/tests/` - List active tests
- `GET /assessments/api/tests/{id}/` - Get test details
- `POST /assessments/api/submit-attempt/` - Submit test answers
- `POST /assessments/api/autosave-attempt/{id}/` - Autosave answers
- `GET /assessments/api/attempts/` - List user's attempts

### Admin Endpoints (require admin privileges)

- `GET/POST /assessments/api/questions/` - Manage questions
- `POST /assessments/api/upload-csv/` - Upload CSV file
- `GET/POST /assessments/api/tests/` - Manage tests (admin only)

## Running Tests

### Run all tests
```bash
docker-compose exec web pytest assessments/tests.py -v
```

### Run specific test class
```bash
docker-compose exec web pytest assessments/tests.py::TestComputeScores -v
```

### Run with coverage
```bash
docker-compose exec web pytest assessments/tests.py --cov=assessments
```

## Development Workflow

### Making Changes

1. Make code changes
2. Test locally: `docker-compose exec web pytest`
3. Check migrations: `docker-compose exec web python manage.py makemigrations`
4. Run migrations: `docker-compose exec web python manage.py migrate`
5. Commit changes

### Accessing Django Shell

```bash
docker-compose exec web python manage.py shell
```

### Viewing Logs

```bash
docker-compose logs -f web
```

### Stopping Services

```bash
docker-compose down
```

### Rebuilding After Changes

```bash
docker-compose down
docker-compose up --build
```

## Project Structure

```
vinodmanure1/
├── career_platform/          # Django project settings
│   ├── settings.py          # Main settings
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py              # WSGI configuration
├── assessments/              # Main application
│   ├── models.py            # Database models
│   ├── views.py             # Views and API endpoints
│   ├── serializers.py       # DRF serializers
│   ├── services.py          # Business logic (scoring)
│   ├── admin.py             # Admin configuration
│   ├── urls.py              # App URL patterns
│   ├── tests.py             # Test suite
│   ├── management/          # Management commands
│   │   └── commands/
│   │       ├── import_questions.py
│   │       └── seed_data.py
│   └── templates/           # HTML templates
│       └── assessments/
│           ├── base.html
│           ├── student_dashboard.html
│           ├── take_test.html
│           └── report.html
├── seed/                     # Seed data
│   └── question_bank_template.csv
├── .github/                  # GitHub Actions
│   └── workflows/
│       └── ci.yml
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile               # Docker image definition
├── requirements.txt         # Python dependencies
├── pytest.ini              # Pytest configuration
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Models

### Question
- Stores assessment questions with dimension and weight
- Dimensions: technical, creative, analytical, leadership, communication

### Test
- Assessment test with name, description, and duration
- Links to questions via TestQuestion

### TestQuestion
- Many-to-many relationship between Test and Question
- Maintains question order in test

### Attempt
- User's test submission with answers and scores
- Stores dimension_scores, total_score, and top_dimensions
- Links to generated PDF report

### Profile
- OneToOne relationship with User
- Stores additional user information

### ReportParagraphMapping
- Maps dimension score ranges to report text
- Used for generating personalized reports

## Scoring Algorithm

The scoring engine (`assessments/services.py`) implements deterministic scoring:

1. **Normalization**: Answer values (1-5) normalized to 0-1 scale
2. **Weighting**: Applied per-question weights
3. **Dimension Scores**: Aggregated per dimension, normalized to 0-100
4. **Total Score**: Average of all dimension scores
5. **Top Dimensions**: Sorted list of top 3 scoring dimensions

Formula per dimension:
```
score = (sum of weighted_normalized_answers) / (sum of weights) * 100
```

Where:
```
weighted_normalized_answer = ((answer - 1) / 4) * weight
```

## Troubleshooting

### Database Connection Issues

If you get database connection errors:
```bash
docker-compose down
docker-compose up --build
```

### Port Already in Use

If port 8000 or 5432 is already in use:
1. Stop other services using those ports
2. Or modify ports in `docker-compose.yml`

### WeasyPrint PDF Generation Issues

WeasyPrint requires system libraries. These are included in the Dockerfile. If running locally without Docker:
```bash
# Ubuntu/Debian
sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0 libgdk-pixbuf2.0-0

# macOS
brew install pango gdk-pixbuf
```

### Migrations Not Applying

```bash
docker-compose exec web python manage.py migrate --run-syncdb
```

### Static Files Not Loading

```bash
docker-compose exec web python manage.py collectstatic --no-input
```

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) automatically:
- Runs on push to main/develop branches and PRs
- Sets up PostgreSQL service
- Installs dependencies
- Runs migrations
- Executes test suite

## Security Considerations

- Change `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Use strong passwords
- Enable HTTPS in production
- Review and restrict `ALLOWED_HOSTS`
- Keep dependencies updated

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Create an issue on GitHub
- Contact: admin@example.com

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

---

**Version**: 1.0.0  
**Last Updated**: 2024
