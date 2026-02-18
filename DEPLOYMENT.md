# Deployment Guide

## Local Development Setup

### Using Docker Compose (Recommended)

1. **Start the application**
   ```bash
   docker-compose up --build
   ```

2. **In a new terminal, run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Seed initial data**
   ```bash
   docker-compose exec web python manage.py seed_data
   ```
   
   This creates:
   - Admin user: `admin` / `admin123`
   - Student user: `student` / `student123`
   - 25 sample questions
   - 1 Grade 9 test with 20 questions
   - Report paragraph mappings

4. **Access the application**
   - Student Portal: http://localhost:8000/
   - Admin Panel: http://localhost:8000/admin/
   - API Docs: http://localhost:8000/api/

### Without Docker

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Uses SQLite by default for local dev
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

7. **Run server**
   ```bash
   python manage.py runserver
   ```

## Running Tests

```bash
# Run all tests
pytest -v

# Run with coverage report
pytest --cov=assessments --cov-report=html

# Run specific test class
pytest assessments/tests.py::TestComputeScores -v
```

## Production Deployment

### Environment Variables

Set these in production:

```env
DEBUG=False
SECRET_KEY=<your-secret-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### Static Files

```bash
python manage.py collectstatic --no-input
```

### Security Checklist

- [ ] Change default admin password
- [ ] Set strong SECRET_KEY
- [ ] Configure ALLOWED_HOSTS
- [ ] Use PostgreSQL in production
- [ ] Enable HTTPS
- [ ] Configure CSRF_TRUSTED_ORIGINS
- [ ] Set up proper logging
- [ ] Configure email backend for password resets
- [ ] Review Django security checklist

### Docker Production

Update `docker-compose.yml` for production:

```yaml
services:
  web:
    command: gunicorn career_platform.wsgi:application --bind 0.0.0.0:8000 --workers 3
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
```

## Troubleshooting

### Database Connection Issues

If using Docker and can't connect to database:
```bash
docker-compose down -v
docker-compose up --build
```

### Migration Issues

```bash
# Reset migrations (development only!)
python manage.py migrate assessments zero
python manage.py migrate
```

### PDF Generation Issues

If WeasyPrint fails, ensure system dependencies are installed:
```bash
# Ubuntu/Debian
sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0 libgdk-pixbuf2.0-0

# macOS
brew install pango gdk-pixbuf
```

## Support

For issues, please check:
1. README.md for basic setup
2. GitHub issues
3. Django documentation
