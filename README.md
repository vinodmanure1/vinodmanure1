# Career Guidance Platform MVP

A Django-based Career Guidance Platform that provides assessment tests, deterministic scoring, and personalized PDF reports for students.

## Features

- **Question Bank Management**: Import questions via CSV or create them through admin interface
- **Test Creation**: Admin can create tests by selecting questions from the question bank
- **Student Assessment**: Students can take tests through a clean, user-friendly interface
- **Deterministic Scoring**: Automatic scoring with category-wise breakdown (Math, Verbal, Logical, etc.)
- **PDF Report Generation**: Generate detailed PDF reports with personalized feedback using WeasyPrint
- **Report Paragraph Mapping**: Configurable feedback paragraphs based on score ranges
- **Admin Dashboard**: Full Django admin interface for managing questions, tests, and viewing attempts
- **RESTful API**: API endpoints for CSV import, test submission, and PDF generation
- **Docker Support**: Complete Docker Compose setup with PostgreSQL database
- **Automated Testing**: pytest-django test suite with CI/CD via GitHub Actions

## Tech Stack

- **Backend**: Django 4.2.9
- **Database**: PostgreSQL 15
- **PDF Generation**: WeasyPrint 60.2
- **API**: Django REST Framework 3.14.0
- **Testing**: pytest-django 4.7.0
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions

## Local Development Setup

### Prerequisites

- Docker and Docker Compose installed
- Git

### Quick Start

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

4. **Run migrations** (in a new terminal)
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Seed the database** (optional but recommended)
   ```bash
   docker-compose exec web python manage.py seed_data
   ```

   This will:
   - Import sample questions from `assessments/seed/question_bank_template.csv`
   - Create report paragraph mappings from `assessments/seed/report_paragraph_mappings.json`
   - Create a sample test with questions

7. **Access the application**
   - Admin Interface: http://localhost:8000/admin
   - Student Interface: http://localhost:8000/student/
   - API Endpoints: http://localhost:8000/api/

### Alternative: Import Questions from Custom CSV

If you have your own CSV file with questions:

```bash
docker-compose exec web python manage.py import_questions /path/to/your/questions.csv
```

**CSV Format:**
```csv
question_text,option_a,option_b,option_c,option_d,correct_answer,category,difficulty
"What is 2+2?",3,4,5,6,B,Math,Easy
```

## Running Tests

### Run all tests
```bash
docker-compose exec web pytest
```

### Run with verbose output
```bash
docker-compose exec web pytest -v
```

### Run specific test file
```bash
docker-compose exec web pytest assessments/tests.py
```

## Project Structure

```
.
├── career_platform/          # Django project configuration
│   ├── settings.py          # Project settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
├── assessments/             # Main application
│   ├── models.py            # Data models (Question, Test, Attempt, etc.)
│   ├── admin.py             # Admin interface configuration
│   ├── views.py             # API views
│   ├── student_views.py     # Student-facing views
│   ├── services.py          # Business logic (compute_scores)
│   ├── urls.py              # API URL routes
│   ├── student_urls.py      # Student URL routes
│   ├── tests.py             # Test suite
│   ├── management/
│   │   └── commands/
│   │       ├── import_questions.py  # CSV import command
│   │       └── seed_data.py         # Database seeding
│   ├── templates/           # HTML templates
│   │   └── assessments/
│   │       ├── test_list.html
│   │       ├── take_test.html
│   │       ├── test_result.html
│   │       └── report_template.html
│   └── seed/                # Seed data files
│       ├── question_bank_template.csv
│       └── report_paragraph_mappings.json
├── static/                  # Static files (CSS, JS, images)
├── media/                   # User-uploaded files and generated PDFs
├── Dockerfile               # Docker configuration for web service
├── docker-compose.yml       # Docker Compose configuration
├── requirements.txt         # Python dependencies
├── pytest.ini               # pytest configuration
├── .env.example             # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Usage Guide

### For Administrators

1. **Login to Admin**: Navigate to http://localhost:8000/admin and login with superuser credentials

2. **Import Questions**: 
   - Use management command: `docker-compose exec web python manage.py import_questions <csv_file>`
   - Or use the API: POST to `/api/import-questions/` with CSV file

3. **Create Tests**:
   - Go to Admin → Tests → Add Test
   - Fill in title and description
   - Add questions by selecting from TestQuestions inline

4. **View Attempts**:
   - Go to Admin → Attempts
   - View student submissions, scores, and download PDFs

5. **Manage Report Feedback**:
   - Go to Admin → Report Paragraph Mappings
   - Configure feedback text for different score ranges and categories

### For Students

1. **View Available Tests**: Navigate to http://localhost:8000/student/

2. **Take a Test**:
   - Click on "Take Test" button
   - Enter your name and email (optional)
   - Answer all questions
   - Submit the test

3. **View Results**:
   - After submission, you'll see your scores by category
   - Download detailed PDF report with personalized feedback

### API Endpoints

#### Import Questions (Admin Only)
```
POST /api/import-questions/
Content-Type: multipart/form-data
Body: file=<csv_file>
```

#### Submit Test Attempt
```
POST /api/submit-attempt/
Content-Type: application/json
Body:
{
  "test_id": 1,
  "student_name": "John Doe",
  "student_email": "john@example.com",
  "answers": {
    "1": "A",
    "2": "B",
    "3": "C"
  }
}
```

#### Generate PDF Report
```
GET /api/report/<attempt_id>/pdf/
```

## Development

### Running Without Docker

1. Install Python 3.11+
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up PostgreSQL database
5. Copy `.env.example` to `.env` and configure database settings
6. Run migrations:
   ```bash
   python manage.py migrate
   ```
7. Run development server:
   ```bash
   python manage.py runserver
   ```

### Adding New Tests

Add test functions to `assessments/tests.py`:

```python
@pytest.mark.django_db
def test_my_feature():
    # Your test code
    assert True
```

Run tests:
```bash
docker-compose exec web pytest
```

## CI/CD

The project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that:
- Runs on push to `main` branch and pull requests
- Sets up PostgreSQL service
- Installs dependencies
- Runs migrations
- Executes the test suite

## Data Models

### Question
- Stores individual assessment questions with multiple choice options
- Categories: Math, Verbal, Logical, etc.
- Difficulty levels: Easy, Medium, Hard

### Test
- Container for groups of questions
- Can be activated/deactivated

### TestQuestion
- Links questions to tests with ordering

### Attempt
- Records student's test submission
- Stores answers (JSON), computed scores (JSON)
- Links to generated PDF report

### Profile
- Extended user information for students

### ReportParagraphMapping
- Maps score ranges to personalized feedback text
- Configured per category (Math, Verbal, etc.)

## Scoring Logic

The `compute_scores` function in `assessments/services.py`:
1. Retrieves all questions for the test
2. Compares student answers with correct answers
3. Calculates category-wise scores (correct/total/percentage)
4. Calculates overall score
5. Returns deterministic JSON structure

## PDF Report Generation

Reports are generated using WeasyPrint:
1. HTML template rendered with Django template engine
2. Student scores and personalized feedback included
3. PDF generated from HTML
4. Stored in `media/reports/` directory
5. Linked to Attempt model

## Environment Variables

Key environment variables (see `.env.example`):
- `DEBUG`: Enable debug mode (True/False)
- `SECRET_KEY`: Django secret key
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_HOST`: Database host
- `POSTGRES_PORT`: Database port

## Security Notes

- No secrets are committed to the repository
- `.env` file is gitignored
- Use strong `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Configure `ALLOWED_HOSTS` appropriately
- No AI/LLM integrations included

## License

This is an MVP scaffold for development purposes.

## Support

For issues or questions, please open an issue on GitHub.
