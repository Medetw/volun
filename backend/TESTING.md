# Testing Configuration for Volunteer Platform Backend

## Test Structure

```
apps/
├── users/
│   └── tests/
│       ├── test_models.py      # User, VolunteerProfile, OrganizationProfile tests
│       ├── test_serializers.py # User-related serializer tests
│       ├── test_api.py         # User API endpoint tests
│       └── test_permissions.py # User permission tests
├── projects/
│   └── tests/
│       ├── test_models.py      # Project, Category, Region tests
│       ├── test_serializers.py # Project serializer tests
│       ├── test_api.py         # Project API tests
│       └── test_permissions.py # Project permission tests
├── applications/
│   └── tests/
│       ├── test_models.py      # Application model tests
│       ├── test_serializers.py # Application serializer tests
│       ├── test_api.py         # Application API tests
│       └── test_permissions.py # Application permission tests
└── reports/
    └── tests/
        ├── test_models.py      # ProjectReport, VolunteerContribution tests
        ├── test_serializers.py # Report serializer tests
        ├── test_api.py         # Report API tests
        └── test_permissions.py # Report permission tests
```

## Running Tests

### Quick Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=apps

# Run specific app tests
pytest apps/users/tests/

# Run specific test file
pytest apps/users/tests/test_models.py

# Run tests matching pattern
pytest -k "test_create_user"

# Run with coverage report
pytest --cov=apps --cov-report=html

# Run tests and show coverage in terminal
pytest --cov=apps --cov-report=term-missing
```

### Using the Test Runner Script

```bash
# Run all tests with coverage
./run_tests.sh

# Run specific test suites
./run_tests.sh --specific

# Run tests + linting
./run_tests.sh --lint

# Run tests + security checks
./run_tests.sh --security

# Run everything
./run_tests.sh --specific --lint --security
```

## Test Database Configuration

Tests use SQLite by default. To use PostgreSQL:

```bash
# Create test database
createdb test_volunteering_platform

# Set environment variable
export DATABASE_URL=postgres://username:password@localhost:5432/test_volunteering_platform

# Run tests
pytest
```

## Test Fixtures

Common test fixtures are defined in `conftest.py`:

- `api_client` - Unauthenticated API client
- `volunteer_user` - Volunteer user with profile
- `organization_user` - Organization user with profile
- `admin_user` - Admin user
- `auth_volunteer_client` - Authenticated volunteer client
- `auth_organization_client` - Authenticated organization client
- `auth_admin_client` - Authenticated admin client
- `category` - Test category
- `region` - Test region
- `project` - Test project
- `application` - Test application
- `approved_application` - Approved application

## Test Factories

Use factories for generating test data:

```python
from apps.tests.factories import UserFactory, ProjectFactory, ApplicationFactory

# Create test data
user = UserFactory(role='volunteer')
project = ProjectFactory(organization=user)
application = ApplicationFactory(volunteer=user, project=project)

# Create bulk test data
from apps.tests.factories import create_test_data
data = create_test_data()
```

## Writing Tests

### Model Tests

```python
class TestUserModel(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.username == 'testuser'
        assert user.check_password('testpass123')
```

### Serializer Tests

```python
class TestUserSerializer:
    def test_valid_serialization(self, db, volunteer_user):
        serializer = UserSerializer(volunteer_user)
        data = serializer.data
        assert data['username'] == volunteer_user.username
```

### API Tests

```python
class TestUserAPI:
    def test_register_volunteer(self, api_client):
        url = reverse('auth-register-volunteer')
        data = {
            'username': 'newvolunteer',
            'email': 'volunteer@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == 201
```

### Permission Tests

```python
class TestProjectPermissions:
    def test_volunteer_cannot_create_project(self, auth_volunteer_client):
        url = reverse('project-list')
        data = {'title': 'Test Project'}
        response = auth_volunteer_client.post(url, data)
        assert response.status_code == 403
```

## Coverage Requirements

- Target coverage: 80%
- Critical paths: 95%
- Model tests: 90%
- API tests: 85%
- Permission tests: 95%

## CI/CD Testing

GitHub Actions runs:

1. **Test Job**: All tests with coverage
2. **Security Job**: Dependency vulnerability scan + code security analysis

### CI Test Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Run tests with coverage
pytest --cov=apps --cov-report=xml

# Upload coverage to codecov
```

## Mocking

External services are mocked:

```python
@pytest.fixture
def mock_email_backend(mocker):
    return mocker.patch('django.core.mail.outlook.EmailBackend.send_messages')

@pytest.fixture
def mock_celery_task(mocker):
    return mocker.patch('apps.notifications.tasks.send_notification_email.delay')

@pytest.fixture
def mock_storage(mocker):
    return mocker.patch('django.core.files.storage.default_storage.save')
```

## Test Data Management

### Database Reuse

Tests use `--reuse-db` flag for performance:

```bash
pytest --reuse-db
```

### Cleanup

```bash
# Clean up test database
pytest --reuse-db --create-db

# Reset migrations
python manage.py migrate apps zero
python manage.py migrate
```

## Best Practices

1. **Use descriptive test names**
2. **Test one thing per test**
3. **Use fixtures for setup**
4. **Mock external dependencies**
5. **Test happy path and error cases**
6. **Test permissions thoroughly**
7. **Use factories for test data**
8. **Keep tests independent**
9. **Test API contracts**
10. **Verify database constraints**

## Debugging Tests

```bash
# Run with pdb
pytest --pdb

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Run specific test with debug
pytest apps/users/tests/test_models.py::TestUserModel::test_create_user -s -v --pdb
```

## Performance Testing

```bash
# Run tests with timing
pytest --durations=10

# Profile slow tests
pytest --profile
```

## Continuous Integration

Tests run on:
- Push to main/develop branches
- Pull requests
- Scheduled runs (daily)

Coverage is tracked and reported to Codecov.
