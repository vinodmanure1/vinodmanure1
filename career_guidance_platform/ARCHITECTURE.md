# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Web Browser                              │
│  (Student Dashboard, Test Taking Interface, Admin Panel)         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ HTTP/HTTPS
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                    Django Application                            │
│                                                                   │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │   Views     │  │     API      │  │   Admin Interface      │ │
│  │  (Student   │◄─┤   Endpoints  │◄─┤   (Question/Test      │ │
│  │   flows)    │  │   (DRF)      │  │    Management)         │ │
│  └──────┬──────┘  └──────┬───────┘  └───────────┬────────────┘ │
│         │                │                       │               │
│  ┌──────▼────────────────▼───────────────────────▼────────────┐ │
│  │              Business Logic Layer                           │ │
│  │  ┌─────────────────┐  ┌──────────────────┐                 │ │
│  │  │ Scoring Engine  │  │  CSV Import      │                 │ │
│  │  │ (services.py)   │  │  (utils.py)      │                 │ │
│  │  └────────┬────────┘  └──────────┬───────┘                 │ │
│  └───────────┼────────────────────────┼─────────────────────────┘ │
│              │                        │                           │
│  ┌───────────▼────────────────────────▼─────────────────────────┐ │
│  │                     Django ORM                                │ │
│  │  Models: Question, Test, TestQuestion, Attempt, Profile      │ │
│  └───────────────────────────┬───────────────────────────────────┘ │
└────────────────────────────────┼─────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   PostgreSQL Database   │
                    │  (Persistent Storage)   │
                    └─────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                     Additional Services                         │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │   WeasyPrint     │  │   Media Storage  │                   │
│  │  (PDF Reports)   │  │  (Generated PDFs)│                   │
│  └──────────────────┘  └──────────────────┘                   │
└────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Student Assessment Flow
1. **Student logs in** → Redirected to Dashboard
2. **Selects test** → Creates new Attempt record
3. **Answers questions** → Auto-saves to Attempt.answers (JSON)
4. **Submits test** → Triggers scoring engine
5. **Scoring engine** → Computes dimension scores, total score
6. **Results saved** → Updates Attempt with scores, completion time
7. **View report** → Renders HTML report
8. **Download PDF** → WeasyPrint generates PDF from HTML template

### Admin Question Management Flow
1. **Admin uploads CSV** → API endpoint receives file
2. **CSV parsed** → utils.py processes rows
3. **Questions created** → Bulk insert to database
4. **Test creation** → Admin links questions to test via TestQuestion
5. **Test activation** → Makes test available to students

## Component Details

### Models Layer
- **Question**: Individual assessment questions with dimension and weight
- **Test**: Collection of questions with metadata (title, duration, etc.)
- **TestQuestion**: M2M relationship with ordering
- **Attempt**: Records student's test attempt and results
- **Profile**: Extended user information
- **ReportParagraphMapping**: Maps score ranges to report text

### Services Layer
- **compute_scores()**: 
  - Groups answers by dimension
  - Applies weighted averaging
  - Normalizes to 0-100 scale
  - Returns dimension scores, total score, top dimensions

### Views Layer
- **Student Views**: Dashboard, take test, view results
- **Report Views**: HTML rendering, PDF generation with caching
- **API Views**: Submit attempt, save progress, CSV upload

### Admin Layer
- **Django Admin**: CRUD for all models
- **Import/Export**: CSV bulk operations
- **Inline Editors**: TestQuestion management within Test admin

## Technology Stack Details

### Backend
- **Django 4.2+**: Web framework
- **Django REST Framework**: API endpoints
- **PostgreSQL**: Primary database
- **WeasyPrint**: PDF generation from HTML/CSS

### Frontend
- **Server-side rendering**: Django templates
- **JavaScript**: Timer, autosave, form handling
- **CSS**: Responsive design, A4 print styles

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Gunicorn**: WSGI server for production
- **pytest**: Testing framework
- **GitHub Actions**: CI/CD pipeline

## Security Considerations

1. **Authentication**: Django's built-in auth system
2. **CSRF Protection**: Django middleware enabled
3. **SQL Injection**: ORM prevents direct SQL
4. **XSS Protection**: Template auto-escaping
5. **Admin Access**: Permission-based access control

## Scalability Considerations

### Current Architecture
- Single server deployment
- File-based media storage
- Synchronous request processing

### Future Enhancements
- **Horizontal Scaling**: Load balancer + multiple app servers
- **Cloud Storage**: S3/GCS for PDFs and media
- **Caching**: Redis for session and query caching
- **Async Tasks**: Celery for PDF generation
- **CDN**: Static file delivery
- **Database Replication**: Read replicas for reporting

## Performance Optimization

1. **Database Indexing**: Automatic on foreign keys
2. **Query Optimization**: select_related() for joins
3. **Static Files**: Collected and served efficiently
4. **PDF Caching**: Generated PDFs cached in model
5. **Autosave Throttling**: 2-second delay prevents spam

## Deployment Architecture (Docker)

```
┌──────────────────────────────────────────────────────────┐
│                    Docker Host                            │
│                                                            │
│  ┌──────────────────┐         ┌──────────────────┐      │
│  │  Web Container   │         │  DB Container    │      │
│  │  (Django App)    │◄───────►│  (PostgreSQL)    │      │
│  │  Port: 8000      │         │  Port: 5432      │      │
│  └──────────────────┘         └──────────────────┘      │
│           │                            │                  │
│           │                            │                  │
│  ┌────────▼────────┐         ┌────────▼────────┐        │
│  │  Volume:        │         │  Volume:        │        │
│  │  media_files    │         │  postgres_data  │        │
│  └─────────────────┘         └─────────────────┘        │
└──────────────────────────────────────────────────────────┘
```

## API Endpoints

### Public Endpoints
- `GET /` - Home page
- `POST /admin/login/` - Admin login

### Authenticated Student Endpoints
- `GET /dashboard/` - Student dashboard
- `GET /test/<id>/take/` - Take test interface
- `POST /attempt/<id>/save/` - Autosave progress
- `POST /attempt/<id>/submit/` - Submit final answers
- `GET /attempt/<id>/report/` - View HTML report
- `GET /attempt/<id>/pdf/` - Download PDF report

### Admin API Endpoints
- `POST /api/admin/upload-csv/` - Bulk import questions (requires staff permission)

## Testing Strategy

### Unit Tests
- **test_scoring.py**: Scoring algorithm validation
- **test_csv_import.py**: CSV parsing and validation
- **test_api.py**: API endpoint functionality

### Integration Tests
- Database migrations
- End-to-end student flow (in manual testing)
- Admin workflows (in manual testing)

### CI/CD Pipeline
1. Checkout code
2. Install dependencies
3. Run migrations
4. Execute pytest
5. Run Django system check
