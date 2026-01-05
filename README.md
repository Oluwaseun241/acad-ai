# Acad AI - Mini Assessment Engine

A Django REST API for managing exams, questions, and student submissions with automated grading capabilities.

## Requirements

- Python 3.8+
- Django 5.2.2+
- Django REST Framework 3.15.0+
- scikit-learn 1.5.0+
- drf-spectacular 0.27.0+

## Database Setup

1. **Run migrations**:
```bash
python manage.py makemigrations
python manage.py migrate
```

2. **Create a superuser** (for admin access):
```bash
python manage.py createsuperuser
```

3. **Create test users** (optional):
```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_user(username='student1', password='password123')
User.objects.create_user(username='student2', password='password123')
```

## Running the Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

- **API Root**: `http://localhost:8000/api/`
- **Swagger UI**: `http://localhost:8000/api/schema/swagger-ui/`
- **ReDoc**: `http://localhost:8000/api/schema/redoc/`
- **Interactive Docs**: `http://localhost:8000/`

## API Documentation

### Authentication

All API endpoints (except login) require authentication using Token Authentication.

#### Login Endpoint

**POST** `/api/auth/login/`

Authenticate and receive an authentication token.

**Request Body**:
```json
{
    "username": "student1",
    "password": "password123"
}
```

**Response** (200 OK):
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user_id": 1,
    "username": "student1"
}
```

**Error Response** (400 Bad Request):
```json
{
    "detail": "Invalid credentials."
}
```

#### Using the Token

Include the token in the `Authorization` header for all subsequent requests:

```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Important**: Use the word `Token` (not `Bearer`) followed by a space and your token.

### Endpoints

#### Exams

##### List All Exams

**GET** `/api/exams/`

Retrieve a paginated list of all available exams.

**Headers**:
```
Authorization: Token <your_token>
```

**Response** (200 OK):
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
            "title": "Introduction to Python",
            "course": "CS101",
            "duration_minutes": 60,
            "metadata": {},
            "created_at": "2026-01-05T12:00:00Z",
            "question_count": 5
        },
        {
            "id": "01ARZ3NDEKTSV4RRFFQ69G5FAW",
            "title": "Database Systems",
            "course": "CS201",
            "duration_minutes": 90,
            "metadata": {},
            "created_at": "2026-01-05T11:00:00Z",
            "question_count": 10
        }
    ]
}
```

##### Get Exam Details

**GET** `/api/exams/{exam_id}/`

Retrieve detailed information about a specific exam including all questions.

**Headers**:
```
Authorization: Token <your_token>
```

**Response** (200 OK):
```json
{
    "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
    "title": "Introduction to Python",
    "course": "CS101",
    "duration_minutes": 60,
    "metadata": {},
    "created_at": "2026-01-05T12:00:00Z",
    "questions": [
        {
            "id": "01ARZ3NDEKTSV4RRFFQ69G5FAX",
            "question_text": "What is the output of print(2 + 3)?",
            "question_type": "MCQ",
            "marks": 1,
            "order": 0
        },
        {
            "id": "01ARZ3NDEKTSV4RRFFQ69G5FAY",
            "question_text": "Explain the concept of list comprehension in Python.",
            "question_type": "ESSAY",
            "marks": 10,
            "order": 1
        }
    ]
}
```

##### Submit Exam Answers

**POST** `/api/exams/{exam_id}/submit/`

Submit answers for an exam. All questions must be answered. Grading is performed automatically.

**Headers**:
```
Authorization: Token <your_token>
Content-Type: application/json
```

**Request Body**:
```json
{
    "answers": [
        {
            "question_id": "01ARZ3NDEKTSV4RRFFQ69G5FAX",
            "student_answer": "5"
        },
        {
            "question_id": "01ARZ3NDEKTSV4RRFFQ69G5FAY",
            "student_answer": "List comprehension is a concise way to create lists in Python. It allows you to generate a new list by applying an expression to each item in an iterable."
        }
    ]
}
```

**Response** (201 Created):
```json
{
    "id": "01ARZ3NDEKTSV4RRFFQ69G5FAZ",
    "student_username": "student1",
    "exam_title": "Introduction to Python",
    "exam_course": "CS101",
    "submitted_at": "2026-01-05T13:00:00Z",
    "graded_at": "2026-01-05T13:00:01Z",
    "score": 9.5,
    "max_score": 11.0,
    "percentage_score": 86.36,
    "is_graded": true,
    "answers": [
        {
            "question_id": "01ARZ3NDEKTSV4RRFFQ69G5FAX",
            "question_text": "What is the output of print(2 + 3)?",
            "question_type": "MCQ",
            "student_answer": "5",
            "awarded_marks": 1.0,
            "max_marks": 1
        },
        {
            "question_id": "01ARZ3NDEKTSV4RRFFQ69G5FAY",
            "question_text": "Explain the concept of list comprehension in Python.",
            "question_type": "ESSAY",
            "student_answer": "List comprehension is a concise way to create lists in Python...",
            "awarded_marks": 8.5,
            "max_marks": 10
        }
    ]
}
```

**Error Responses**:

- **400 Bad Request** - Missing or invalid answers:
```json
{
    "answers": ["At least one answer is required."]
}
```

- **400 Bad Request** - Duplicate question IDs:
```json
{
    "answers": ["Duplicate question IDs are not allowed."]
}
```

- **400 Bad Request** - Questions don't belong to exam:
```json
{
    "answers": ["Questions {'01ARZ3NDEKTSV4RRFFQ69G5FAW'} do not belong to this exam."]
}
```

- **400 Bad Request** - Not all questions answered:
```json
{
    "answers": ["All questions must be answered. Missing: {'01ARZ3NDEKTSV4RRFFQ69G5FAY'}"]
}
```

- **400 Bad Request** - Already submitted:
```json
{
    "detail": "You have already submitted this exam."
}
```

#### Submissions

##### List User's Submissions

**GET** `/api/submissions/`

Retrieve a paginated list of all submissions made by the authenticated user.

**Headers**:
```
Authorization: Token <your_token>
```

**Response** (200 OK):
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "01ARZ3NDEKTSV4RRFFQ69G5FAZ",
            "exam_title": "Introduction to Python",
            "exam_course": "CS101",
            "submitted_at": "2026-01-05T13:00:00Z",
            "graded_at": "2026-01-05T13:00:01Z",
            "score": 9.5,
            "max_score": 11.0,
            "percentage_score": 86.36,
            "is_graded": true
        },
        {
            "id": "01ARZ3NDEKTSV4RRFFQ69G5FA0",
            "exam_title": "Database Systems",
            "exam_course": "CS201",
            "submitted_at": "2026-01-05T14:00:00Z",
            "graded_at": "2026-01-05T14:00:02Z",
            "score": 18.0,
            "max_score": 20.0,
            "percentage_score": 90.0,
            "is_graded": true
        }
    ]
}
```

##### Get Submission Details

**GET** `/api/submissions/{submission_id}/`

Retrieve detailed information about a specific submission including all answers and grading results.

**Headers**:
```
Authorization: Token <your_token>
```

**Response** (200 OK):
```json
{
    "id": "01ARZ3NDEKTSV4RRFFQ69G5FAZ",
    "student_username": "student1",
    "exam_title": "Introduction to Python",
    "exam_course": "CS101",
    "submitted_at": "2026-01-05T13:00:00Z",
    "graded_at": "2026-01-05T13:00:01Z",
    "score": 9.5,
    "max_score": 11.0,
    "percentage_score": 86.36,
    "is_graded": true,
    "answers": [
        {
            "question_id": "01ARZ3NDEKTSV4RRFFQ69G5FAX",
            "question_text": "What is the output of print(2 + 3)?",
            "question_type": "MCQ",
            "student_answer": "5",
            "awarded_marks": 1.0,
            "max_marks": 1
        },
        {
            "question_id": "01ARZ3NDEKTSV4RRFFQ69G5FAY",
            "question_text": "Explain the concept of list comprehension in Python.",
            "question_type": "ESSAY",
            "student_answer": "List comprehension is a concise way...",
            "awarded_marks": 8.5,
            "max_marks": 10
        }
    ]
}
```

**Error Response** (403 Forbidden) - Accessing another user's submission:
```json
{
    "detail": "You do not have permission to view this submission."
}
```

## Request/Response Examples

### Complete Workflow Example

#### 1. Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "student1", "password": "password123"}'
```

#### 2. List Exams
```bash
curl -X GET http://localhost:8000/api/exams/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### 3. Get Exam Details
```bash
curl -X GET http://localhost:8000/api/exams/01ARZ3NDEKTSV4RRFFQ69G5FAV/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### 4. Submit Answers
```bash
curl -X POST http://localhost:8000/api/exams/01ARZ3NDEKTSV4RRFFQ69G5FAV/submit/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": [
      {
        "question_id": "01ARZ3NDEKTSV4RRFFQ69G5FAX",
        "student_answer": "5"
      },
      {
        "question_id": "01ARZ3NDEKTSV4RRFFQ69G5FAY",
        "student_answer": "List comprehension is a concise way to create lists."
      }
    ]
  }'
```

#### 5. View Submission
```bash
curl -X GET http://localhost:8000/api/submissions/01ARZ3NDEKTSV4RRFFQ69G5FAZ/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

## Error Handling

The API uses standard HTTP status codes:

- **200 OK**: Request succeeded
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data or validation error
- **401 Unauthorized**: Authentication required or invalid token
- **403 Forbidden**: Permission denied
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Common Error Responses

**401 Unauthorized** - Missing or invalid token:
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**400 Bad Request** - Validation errors:
```json
{
    "field_name": ["Error message describing the validation issue."]
}
```

## Grading System

The assessment engine uses an automated mock grading service that evaluates answers based on question type:

### Multiple Choice Questions (MCQ)
- Exact match: 100% score
- Expected answer contained in student answer: 90% score
- Student answer contained in expected answer: 70% score
- Keyword overlap: Up to 50% score

### Short Answer Questions
- Combines keyword matching (40% weight) and TF-IDF similarity (60% weight)
- Exact match: 100% score
- Partial matches scored based on keyword overlap and semantic similarity

### Essay Questions
- Uses TF-IDF vectorization with cosine similarity
- Focuses on semantic similarity rather than exact matches
- Falls back to keyword matching if TF-IDF fails


## Database Models

### Exam
- `id`: ULID primary key
- `title`: Exam title
- `course`: Course name or identifier
- `duration_minutes`: Exam duration in minutes
- `metadata`: JSON field for additional metadata
- `created_at`: Timestamp

### Question
- `id`: ULID primary key
- `exam`: Foreign key to Exam
- `question_text`: The question content
- `question_type`: MCQ, SHORT, or ESSAY
- `expected_answer`: The expected/correct answer
- `marks`: Maximum marks for the question
- `order`: Display order within the exam

### Submission
- `id`: ULID primary key
- `student`: Foreign key to User
- `exam`: Foreign key to Exam
- `submitted_at`: Submission timestamp
- `graded_at`: Grading completion timestamp
- `score`: Final score
- `max_score`: Maximum possible score
- Unique constraint: (student, exam) - one submission per student per exam

### Answer
- `submission`: Foreign key to Submission
- `question`: Foreign key to Question
- `student_answer`: The student's answer text
- `awarded_marks`: Marks awarded for this answer
- Unique constraint: (submission, question)

## Admin Interface

Access the Django admin interface at `http://localhost:8000/admin/` using your superuser credentials.

The admin interface allows you to:
- Create and manage exams
- Add questions to exams
- View all submissions
- View individual answers and grades
- Manage users

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/api/schema/swagger-ui/`
- **ReDoc**: `http://localhost:8000/api/schema/redoc/`
- **Root**: `http://localhost:8000/` (ReDoc)

The documentation includes:
- All available endpoints
- Request/response schemas
- Authentication requirements
- Example requests and responses
- Error response formats
