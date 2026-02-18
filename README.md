# Career Guidance Platform MVP

A Django-based web application for career assessment and guidance. Students can take an assessment to discover their career aptitudes and receive personalized career recommendations with PDF reports.

## Features

- 📝 **Career Assessment**: Interactive questionnaire covering 5 aptitude categories
  - Technical
  - Creative
  - Analytical
  - Social
  - Practical

- 📊 **Score Analysis**: Weighted scoring system that evaluates responses across all categories

- 🎯 **Career Recommendations**: AI-driven career suggestions based on assessment results

- 📄 **PDF Reports**: Professional career guidance reports generated using WeasyPrint

- 🔐 **Admin Interface**: Django admin for managing questions, responses, and recommendations

- ✅ **Automated Testing**: Comprehensive test suite with CI/CD via GitHub Actions

## Tech Stack

- **Backend**: Django 4.2.28
- **Database**: PostgreSQL 15
- **PDF Generation**: WeasyPrint 68.0
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions

## Prerequisites

- Docker Desktop or Docker Engine + Docker Compose
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/vinodmanure1/vinodmanure1.git
cd vinodmanure1
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` if needed (the defaults work for local development).

### 3. Run with Docker Compose

```bash
docker-compose up --build
```

This command will:
- Build the Docker images
- Start PostgreSQL database
- Run Django migrations
- Import seed questions from CSV
- Start the Django development server on `http://localhost:8000`

### 4. Access the Application

- **Main Application**: http://localhost:8000
- **Admin Interface**: http://localhost:8000/admin
  - Create a superuser first (see below)

## Creating a Superuser

To access the admin interface, create a superuser account:

```bash
docker-compose exec web python manage.py createsuperuser
```

Follow the prompts to set username, email, and password.

## Running Without Docker

### 1. Install System Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3-pip postgresql \
  libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0
```

#### macOS
```bash
brew install python@3.11 postgresql cairo pango gdk-pixbuf
```

### 2. Set Up Python Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Database

Start PostgreSQL and create database:

```bash
sudo service postgresql start
sudo -u postgres psql -c "CREATE DATABASE career_guidance;"
sudo -u postgres psql -c "CREATE USER postgres WITH PASSWORD 'postgres';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE career_guidance TO postgres;"
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env to set DB_HOST=localhost
```

### 5. Run Migrations and Import Data

```bash
python manage.py migrate
python manage.py import_questions seed/questions.csv
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit http://localhost:8000

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI workflow
├── assessments/                # Main Django app
│   ├── management/
│   │   └── commands/
│   │       └── import_questions.py  # CSV import command
│   ├── templates/
│   │   └── assessments/
│   │       ├── base.html       # Base template
│   │       ├── home.html       # Landing page
│   │       ├── assessment.html # Assessment form
│   │       ├── results.html    # Results page
│   │       └── report_pdf.html # PDF template
│   ├── admin.py                # Admin configuration
│   ├── apps.py                 # App configuration
│   ├── models.py               # Data models
│   ├── services.py             # Scoring service
│   ├── tests.py                # Unit tests
│   ├── urls.py                 # URL routing
│   └── views.py                # View controllers
├── career_platform/            # Django project settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Root URL configuration
│   └── wsgi.py
├── seed/
│   └── questions.csv           # Seed data for questions
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── manage.py                   # Django management script
├── README.md                   # This file
└── requirements.txt            # Python dependencies
```

## Database Models

### Question
- `text`: Question text
- `category`: One of (technical, creative, analytical, social, practical)
- `weight`: Scoring weight (default: 1)

### StudentResponse
- `student_name`: Student's name
- `student_email`: Student's email (unique per question)
- `question`: Foreign key to Question
- `rating`: 1-5 scale rating
- `created_at`: Timestamp

### CareerRecommendation
- `student_email`: Unique student identifier
- `student_name`: Student's name
- `technical_score`: Score (0-100)
- `creative_score`: Score (0-100)
- `analytical_score`: Score (0-100)
- `social_score`: Score (0-100)
- `practical_score`: Score (0-100)
- `recommended_career`: Primary career recommendation
- `alternative_careers`: List of alternative careers (JSON)

## Management Commands

### Import Questions from CSV

```bash
python manage.py import_questions <path_to_csv>
```

CSV format:
```csv
text,category,weight
"Question text here",technical,1
```

## Running Tests

### With Docker

```bash
docker-compose exec web python manage.py test
```

### Without Docker

```bash
python manage.py test
```

## CI/CD

The project includes a GitHub Actions workflow that:
1. Sets up Python 3.11
2. Installs system and Python dependencies
3. Runs PostgreSQL in a service container
4. Runs database migrations
5. Imports seed data
6. Executes the test suite
7. Checks Django deployment settings

## API Endpoints

- `GET /` - Home page
- `GET /assessment/` - Assessment form
- `POST /assessment/` - Submit assessment
- `GET /results/<email>/` - View results
- `GET /report/<email>/pdf/` - Download PDF report
- `GET /admin/` - Django admin interface

## Customization

### Adding New Questions

1. Edit `seed/questions.csv` or add via admin interface
2. Reimport: `python manage.py import_questions seed/questions.csv`

### Adding New Career Categories

1. Update `CATEGORY_CHOICES` in `assessments/models.py`
2. Update `CAREER_RECOMMENDATIONS` in `assessments/services.py`
3. Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Customizing Scoring Algorithm

Edit the `CareerScoringService` class in `assessments/services.py`

## Troubleshooting

### Docker Issues

**Container won't start:**
```bash
docker-compose down -v
docker-compose up --build
```

**Database connection error:**
- Ensure PostgreSQL container is healthy
- Check environment variables in `.env`

### Permission Errors

```bash
chmod +x manage.py
```

### PDF Generation Issues

Ensure WeasyPrint system dependencies are installed:
```bash
# Ubuntu/Debian
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0
```

## Security Notes

- ⚠️ **Change `SECRET_KEY` in production**
- ⚠️ **Set `DEBUG=False` in production**
- ⚠️ **Use strong database passwords**
- ⚠️ **Enable HTTPS in production**
- ⚠️ **Configure `ALLOWED_HOSTS` properly**

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python manage.py test`
5. Submit a pull request

## License

This project is open source and available for educational purposes.

## Support

For issues or questions, please open a GitHub issue.

## Acceptance Criteria

✅ Complete Django project structure with all required files  
✅ Docker Compose setup with PostgreSQL database  
✅ Models for Questions, StudentResponses, and CareerRecommendations  
✅ Admin interface for managing data  
✅ CSV import management command  
✅ Scoring service with weighted calculations  
✅ Student-facing views (home, assessment, results)  
✅ PDF report generation with WeasyPrint  
✅ Professional HTML templates with styling  
✅ Seed CSV with sample questions  
✅ Comprehensive test suite  
✅ GitHub Actions CI workflow  
✅ Detailed README with setup instructions  
✅ No secrets in code (using environment variables)  
✅ Runnable local setup with single command  
