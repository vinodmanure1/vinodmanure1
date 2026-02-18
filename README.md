# Career Guidance Platform MVP

A Django-based career guidance platform that provides assessments, scoring, and PDF report generation for students.

## Features

- 🎯 Multi-dimensional career assessments (Aptitude, Logical Reasoning, Interest, Motivation)
- 📊 Deterministic scoring engine with weighted questions
- 📄 PDF report generation with personalized feedback
- 💾 CSV import for question banks
- 🔄 Auto-save functionality during tests
- ⏱️ Timed assessments with countdown timer
- 👥 Admin panel for managing tests, questions, and viewing results
- 🐳 Docker support for easy deployment

## Technology Stack

- **Backend**: Django 4.2.7, Django REST Framework
- **Database**: PostgreSQL (production), SQLite (development)
- **PDF Generation**: WeasyPrint
- **Testing**: pytest, pytest-django, pytest-cov
- **Containerization**: Docker, Docker Compose

## Local Development Setup

### Prerequisites

- Docker and Docker Compose
- Git

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vinodmanure1
   ```

2. **Build and start the containers**
   ```bash
   docker-compose up --build
   ```

3. **In a new terminal, run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Create a superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Seed initial data (optional)**
   ```bash
   docker-compose exec web python manage.py seed_data
   ```
   
   This creates:
   - Admin user (username: `admin`, password: `admin123`)
   - Student user (username: `student`, password: `student123`)
   - Sample questions from CSV
   - A Grade 9 test
   - Report paragraph mappings

6. **Access the application**
   - **Student Dashboard**: http://localhost:8000/
   - **Admin Panel**: http://localhost:8000/admin/
   - **API**: http://localhost:8000/api/

### Local Development without Docker

1. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env if needed (defaults work for local development)
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Seed data**
   ```bash
   python manage.py seed_data
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
vinodmanure1/
├── career_platform/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── assessments/              # Main application
│   ├── models.py            # Database models
│   ├── views.py             # Views and API endpoints
│   ├── serializers.py       # DRF serializers
│   ├── services.py          # Business logic (scoring, CSV import)
│   ├── admin.py             # Admin configuration
│   ├── urls.py              # URL routing
│   ├── tests.py             # Test suite
│   └── management/
│       └── commands/
│           ├── import_questions.py
│           └── seed_data.py
├── templates/               # HTML templates
│   ├── base.html
│   └── assessments/
│       ├── dashboard.html
│       ├── take_test.html
│       └── report.html
├── seed/                    # Seed data files
│   ├── question_bank_template.csv
│   └── report_paragraph_mappings.json
├── static/                  # Static files (CSS, JS)
├── media/                   # User-uploaded files and reports
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
└── README.md
```

## Database Models

### Question
Stores assessment questions with metadata
- Fields: external_id, grade, topic, question_type, question_text, options, correct_answer, weight, dimension

### Test
Assessment configuration
- Fields: name, grade, duration_minutes
- Related: questions (through TestQuestion)

### TestQuestion
Junction table for test-question relationship with ordering

### Attempt
Student test attempt with results
- Fields: test, user, started_at, completed_at, raw_answers, scores, total_score, pdf_report_file

### Profile
Extended user profile
- Fields: user (OneToOne), grade, role

### ReportParagraphMapping
Maps score ranges to report paragraphs
- Fields: dimension, score_range, student_paragraph, parent_paragraph

## API Endpoints

### DRF API

- `GET /api/tests/` - List all tests
- `GET /api/tests/{id}/` - Get test details with questions
- `POST /api/attempts/submit/` - Submit test answers and get scores
- `POST /api/attempts/autosave/` - Auto-save partial answers
- `GET /api/attempts/` - List user's attempts

### Student Views

- `GET /` - Student dashboard
- `GET /take-test/{test_id}/` - Take test page
- `GET /report/{attempt_id}/pdf/` - Generate and download PDF report

### Admin

- `GET /admin/` - Django admin panel
- CSV import available in Question admin

## Management Commands

### Import Questions from CSV
```bash
python manage.py import_questions seed/question_bank_template.csv
```

CSV format:
```csv
external_id,grade,topic,question_type,question_text,options,correct_answer,weight,dimension
Q001,9,Math,mcq,What is 2+2?,"[""2"",""3"",""4"",""5""]",4,1.0,aptitude
```

### Seed Data
```bash
python manage.py seed_data
```

Loads sample data including questions, tests, and report mappings.

## Scoring Engine

The scoring engine (`assessments/services.py`) implements deterministic scoring:

1. **Question Scoring**
   - MCQ/True-False: Correct answer = full weight, wrong = 0
   - Rating Scale: Normalized to weight (rating/5 * weight)

2. **Dimension Scores**
   - Questions grouped by dimension (aptitude, logical, interest, motivation)
   - Score per dimension = (sum of question scores / max possible) * 100

3. **Total Score**
   - Average of all dimension scores

4. **Top Dimensions**
   - Returns top 3 dimensions by score

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=assessments --cov-report=html

# Run specific test class
pytest assessments/tests.py::TestComputeScores -v
```

## Deployment

### Docker Production

1. Update `docker-compose.yml` for production settings
2. Set proper environment variables in `.env`:
   ```
   DEBUG=False
   SECRET_KEY=<your-secret-key>
   ALLOWED_HOSTS=yourdomain.com
   DATABASE_URL=postgresql://user:pass@db:5432/dbname
   ```
3. Run migrations and collect static files:
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py collectstatic --no-input
   ```

## Configuration

### Environment Variables

- `DEBUG` - Debug mode (default: True)
- `SECRET_KEY` - Django secret key
- `DATABASE_URL` - PostgreSQL connection string
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts

### Admin Configuration

Default admin credentials (from seed_data):
- **Username**: admin
- **Password**: admin123

**⚠️ Change these credentials in production!**

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## License

This project is for educational purposes.

## Support

For issues and questions, please open an issue on GitHub.

---

**Note**: This is an MVP (Minimum Viable Product) for local development. Additional security hardening and optimizations are needed for production deployment.
