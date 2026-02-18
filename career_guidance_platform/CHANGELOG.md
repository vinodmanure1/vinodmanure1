# Changelog

All notable changes to the Career Guidance Platform project will be documented in this file.

## [1.0.0] - 2026-02-18

### Added - Initial MVP Release

#### Core Infrastructure
- Django 4.2+ project structure with `career_platform` project and `assessments` app
- Docker and Docker Compose configuration for local development
- PostgreSQL 15 database integration
- Comprehensive requirements.txt with all dependencies
- Environment configuration via .env files
- GitHub Actions CI/CD workflow for automated testing

#### Data Models
- **Question**: Individual assessment questions with dimension and weight
- **Test**: Assessment tests with title, description, and duration
- **TestQuestion**: Many-to-many relationship linking questions to tests with ordering
- **Attempt**: Student test attempts with answers and computed scores
- **Profile**: Extended user profile (OneToOne with Django User)
- **ReportParagraphMapping**: Score-to-text mapping for personalized reports

#### Admin Interface
- Full Django admin configuration for all models
- List display views with filtering and search
- Inline TestQuestion editor within Test admin
- CSV import/export functionality via django-import-export
- Admin API endpoint for programmatic CSV uploads

#### Scoring Engine
- **compute_scores()** function in services.py
- Dimension-based scoring with weighted averaging
- Normalization to 0-100 scale
- Automatic calculation of total score and top dimensions
- Deterministic and reproducible results

#### Student Features
- Server-rendered dashboard showing available tests and past attempts
- Interactive test-taking interface with:
  - Countdown timer (configurable duration)
  - Slider-based question input (0-10 scale)
  - Auto-save functionality (saves every 2 seconds)
  - Real-time progress indication
- Results viewing with detailed dimension breakdown
- Professional HTML report generation
- PDF report generation using WeasyPrint with A4 formatting
- PDF caching to avoid regeneration

#### Data Management
- CSV import via management command: `import_questions`
- Seed data management command: `seed_data`
  - Creates admin user (username: admin, password: admin123)
  - Creates student user (username: student, password: student123)
  - Creates sample test with imported questions
- Sample question bank template in `seed/question_bank_template.csv`
- Admin API for bulk question uploads

#### Testing
- Comprehensive pytest-django test suite (15 tests)
- **test_scoring.py**: Tests for scoring algorithm including:
  - Perfect scores
  - Zero scores
  - Mixed scores
  - Empty answers
  - Weighted questions
- **test_csv_import.py**: Tests for CSV import including:
  - Valid CSV parsing
  - Missing fields handling
  - Default values
  - Whitespace trimming
  - Invalid data handling
- **test_api.py**: Tests for API endpoints including:
  - Attempt submission
  - Progress saving
  - Authentication
  - Admin CSV upload
- All tests pass with 100% success rate

#### Documentation
- **README.md**: Comprehensive project documentation
  - Technology stack overview
  - Quick start guide
  - Manual setup instructions
  - Usage guide for students and administrators
  - API endpoint documentation
  - Project structure
  - Model descriptions
  - Scoring algorithm explanation
  - Troubleshooting guide
- **QUICKSTART.md**: 5-minute setup guide
  - Docker setup steps
  - Manual setup steps
  - Testing instructions
  - Common issues and solutions
- **ARCHITECTURE.md**: Technical architecture documentation
  - System architecture diagram
  - Data flow diagrams
  - Component details
  - Technology stack details
  - Security considerations
  - Scalability considerations
  - Deployment architecture
- **CHANGELOG.md**: This file

#### CI/CD
- GitHub Actions workflow (`.github/workflows/ci.yml`)
- Automated testing on push and pull request
- PostgreSQL service container for integration tests
- System dependency installation for WeasyPrint
- Migration verification
- Django system checks

#### Templates
- **base.html**: Base template with navigation
- **home.html**: Landing page
- **dashboard.html**: Student dashboard
- **take_test.html**: Test-taking interface with JavaScript
- **report.html**: A4-formatted PDF-ready report template

#### API Endpoints
- `GET /` - Home page
- `GET /dashboard/` - Student dashboard
- `GET /test/<id>/take/` - Take test interface
- `POST /attempt/<id>/save/` - Autosave progress
- `POST /attempt/<id>/submit/` - Submit attempt
- `GET /attempt/<id>/report/` - View report
- `GET /attempt/<id>/pdf/` - Download PDF
- `POST /api/admin/upload-csv/` - Admin CSV upload

#### Security Features
- CSRF protection enabled
- Session-based authentication
- Permission-based admin access
- SQL injection prevention via ORM
- XSS protection via template auto-escaping
- Configurable secret key
- Debug mode control
- Allowed hosts configuration

### Technical Specifications

#### Dependencies
- Django 4.2+
- Django REST Framework 3.14+
- PostgreSQL driver (psycopg2-binary)
- WeasyPrint for PDF generation
- django-import-export for CSV handling
- python-dotenv for environment management
- pytest-django for testing
- pandas for data processing
- gunicorn for production WSGI
- Pillow for image handling

#### Database Schema
- 6 models with proper relationships
- Automatic migrations included
- JSON fields for flexible data storage (answers, scores)
- Timestamps on all models
- Foreign key constraints with CASCADE

#### Performance Features
- Query optimization with select_related()
- PDF caching in database
- Autosave throttling (2-second delay)
- Static file collection and serving
- Database indexing on foreign keys

### Notes
- All code is well-documented with docstrings
- No paid services or AI/LLM integrations
- Pure Python/Django implementation
- Production-ready with proper security defaults
- Fully containerized with Docker
- Complete test coverage of core functionality

### Breaking Changes
None - Initial release

### Deprecated
None - Initial release

### Known Issues
- pytest collection warnings for Test and TestQuestion model classes (cosmetic only)
- Security warnings in Django check for production deployment (expected for development)

### Future Enhancements
See ARCHITECTURE.md for scalability considerations including:
- Horizontal scaling with load balancers
- Cloud storage integration (S3/GCS)
- Redis caching
- Celery for async tasks
- CDN for static files
- Database replication
