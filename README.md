# HabotConnect — LSA Service Booking Backend

**Python Backend Developer Hiring Project**

**Candidate:** Kanishka Prabha  
**Email:** `your-email@example.com`  
**GitHub:** `https://github.com/your-username/your-repository`

---

## 1. Project Overview

HabotConnect is building a digital platform that connects parents with Learning Support Assistants (LSAs) for children with learning difficulties.

This project implements a backend prototype for the **LSA Service Booking module** using **Django REST Framework and PostgreSQL**.

The backend provides:

- LSA search based on skills and requested time.
- Availability calculation based on overlapping bookings.
- Booking creation with validation and concurrency protection.
- Prevention of overlapping/double bookings.
- Payment record management.
- Mock external payment integration.
- Payment webhook processing.
- Automated tests using Pytest.
- Continuous integration using GitHub Actions.

The implementation focuses on **data integrity, query efficiency, separation of responsibilities, and reliable state transitions**.

---

## 2. Objectives

The main objectives of the project are:

1. Design a relational database for parents, LSAs, bookings, and payments.
2. Provide RESTful APIs for LSA search and booking creation.
3. Optimize the LSA availability query and avoid N+1 database access.
4. Prevent concurrent booking requests from exceeding LSA capacity.
5. Integrate a mock external payment service.
6. Handle payment success/failure through a webhook.
7. Build automated tests covering success, edge, and failure cases.
8. Run the test suite automatically through GitHub Actions.

---

## 3. Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.13 |
| Framework | Django 6.1 |
| API | Django REST Framework |
| Database | PostgreSQL 16 |
| ORM | Django ORM |
| Array Search | PostgreSQL `ArrayField` |
| Skill Index | PostgreSQL GIN Index |
| Testing | Pytest + pytest-django |
| API Testing | Postman |
| External Integration | Python `requests` |
| CI/CD | GitHub Actions |
| Version Control | Git / GitHub |

---

## 4. Architecture

The application follows a layered architecture to keep HTTP handling, validation, business logic, and database operations separated.

```text
                    Client / Postman
                           |
                           v
                    Django REST API
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      LSA Search       Booking API     Payment Webhook
          |                |                |
          v                v                v
       Service          Service         Payment Service
          |                |                |
          +----------------+----------------+
                           |
                           v
                       PostgreSQL
```

### Application flow

```text
Request
   ↓
View
   ↓
Serializer
   ↓
Service
   ↓
Repository / Django ORM
   ↓
PostgreSQL
```

### Responsibilities

| Layer | Responsibility |
|---|---|
| Views | HTTP request/response handling |
| Serializers | Request validation and response serialization |
| Services | Business rules and workflow orchestration |
| Repositories | Database access/query abstraction |
| Models | Database schema and relationships |
| Payment Service | External/mock payment communication |

This separation follows **Separation of Concerns** and keeps business logic independent from HTTP-specific implementation details.

---

## 5. Project Structure

```text
habot-booking/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
└── haboot-booking/
    │
    ├── manage.py
    ├── pytest.ini
    ├── requirements.txt
    │
    ├── config/
    │   ├── settings.py
    │   ├── urls.py
    │   ├── asgi.py
    │   └── wsgi.py
    │
    └── bookings/
        ├── models.py
        ├── serializers.py
        ├── views.py
        ├── services.py
        ├── repositories.py
        ├── payment_services.py
        ├── payment_mock_views.py
        ├── exceptions.py
        ├── urls.py
        │
        ├── migrations/
        │
        └── tests/
            ├── test_booking.py
            ├── test_lsa_search.py
            └── test_payment.py
```

---

## 6. Database Design

The application uses PostgreSQL as the primary relational database.

### Entity Relationship

```text
Parent
  |
  | 1:N
  |
  v
BookingRequest
  |
  | N:1
  |
  v
LSAProfile


BookingRequest
  |
  | 1:1
  |
  v
Payment
```

### Parent

Stores parent information.

Important fields:

- `id`
- `name`
- `email`
- `created_at`
- `updated_at`

The email field is unique.

### LSAProfile

Stores Learning Support Assistant information.

Important fields:

- `id`
- `name`
- `skills`
- `qualification`
- `experience_years`
- `max_concurrent_students`
- `is_active`
- `created_at`
- `updated_at`

#### Skills

Skills are stored using PostgreSQL's `ArrayField`.

Example:

```json
[
    "dyslexia",
    "adhd"
]
```

This allows the search API to perform skill-containment queries.

### BookingRequest

Represents a parent's requested session.

Important fields:

- `parent`
- `lsa`
- `child_name`
- `start_time`
- `end_time`
- `status`
- `expires_at`
- timestamps

Booking statuses:

```text
PENDING
CONFIRMED
EXPIRED
```

### Payment

Payment is modeled separately from the booking.

Important fields:

- `booking`
- `payment_status`
- `external_payment_id`
- timestamps

Payment statuses:

```text
PENDING
SUCCESS
FAILED
EXPIRED
```

A booking has a one-to-one relationship with its payment record.

---

## 7. API Endpoints

### 7.1 Search Available LSAs

#### Endpoint

```http
GET /api/v1/lsas/search/
```

#### Query Parameters

```text
skill
start_time
end_time
```

#### Example

```http
GET /api/v1/lsas/search/?skill=dyslexia&start_time=2026-08-20T10:00:00Z&end_time=2026-08-20T11:00:00Z
```

#### Example Response

```json
[
    {
        "id": 1,
        "name": "Alice",
        "skills": [
            "dyslexia",
            "adhd"
        ],
        "qualification": "Special Education",
        "experience_years": 5,
        "max_concurrent_students": 4,
        "overlapping_bookings": 0
    }
]
```

#### Availability Rules

An LSA is returned only when:

1. The LSA is active.
2. The requested skill is present.
3. Existing bookings overlap the requested time.
4. The number of overlapping active bookings is below the LSA's maximum capacity.

---

## 8. LSA Availability Query Optimization

The availability query is one of the key performance considerations in this project.

A booking overlaps a requested interval when:

```text
existing.start_time < requested.end_time

AND

existing.end_time > requested.start_time
```

The application counts only relevant bookings whose status can consume capacity:

```text
PENDING
CONFIRMED
```

The query uses database-side aggregation:

```python
.annotate(
    overlapping_bookings=Count(
        "bookings",
        filter=overlapping_filter
    )
)
```

and then compares:

```text
overlapping_bookings
        <
max_concurrent_students
```

### Why database-side aggregation?

A naive implementation could retrieve LSAs and then perform a separate booking query for every LSA:

```text
Get LSAs
   ↓
LSA 1 → query bookings
LSA 2 → query bookings
LSA 3 → query bookings
...
```

This can lead to an **N+1 query pattern**.

Instead, the application lets PostgreSQL perform the filtering, joining, and aggregation.

```text
Application
     |
     | one optimized ORM query
     v
PostgreSQL
     |
     +-- filter active LSAs
     +-- filter skill
     +-- identify overlapping bookings
     +-- count bookings
     +-- compare capacity
     |
     v
Available LSAs
```

This keeps the computation close to the data and avoids unnecessary Python-side loops and database round trips.

---

## 9. Database Indexing

Two important indexes are used.

### GIN Index — LSA Skills

```python
GinIndex(fields=["skills"])
```

The GIN index is used because `skills` is a PostgreSQL array and the application performs containment-style queries against the array.

Example:

```python
skills__contains=["dyslexia"]
```

### Composite Booking Index

```python
models.Index(
    fields=[
        "lsa",
        "status",
        "start_time",
        "end_time",
    ]
)
```

This index is aligned with the dimensions frequently used by the availability query:

```text
LSA
+
Booking status
+
Time range
```

The goal is to reduce unnecessary database scanning when locating relevant booking records.

---

## 10. Booking API

### Endpoint

```http
POST /api/v1/bookings/
```

### Example Request

```json
{
    "parent_id": 1,
    "lsa_id": 1,
    "child_name": "Test Child",
    "skill": "dyslexia",
    "start_time": "2026-08-20T10:00:00Z",
    "end_time": "2026-08-20T11:00:00Z"
}
```

### Booking Flow

```text
Request
   ↓
Validate input
   ↓
Validate Parent
   ↓
Validate LSA
   ↓
Validate skill
   ↓
Validate time range
   ↓
Start transaction
   ↓
Lock relevant LSA row
   ↓
Re-check availability
   ↓
Create Booking
   ↓
Create Payment(PENDING)
   ↓
Initiate mock payment
   ↓
Return response
```

---

## 11. Concurrency & Double-Booking Protection

LSA search provides an **availability snapshot**, but that result can become outdated immediately.

For example:

```text
Request A                  Request B

Search LSA
Available

                           Search LSA
                           Available

Book LSA
                           Book LSA
```

If the booking API trusted the earlier search result, both requests could potentially consume the same capacity.

Therefore, the booking operation performs an authoritative availability check inside a database transaction.

### Transaction

The critical booking operation uses:

```python
transaction.atomic()
```

This ensures that related database changes are handled as a single transaction.

### Row-level locking

The booking flow also uses:

```python
select_for_update()
```

This locks the relevant LSA row while the critical section executes.

Conceptually:

```text
Request A
   ↓
Lock LSA
   ↓
Check availability
   ↓
Create booking
   ↓
Commit
   ↓
Unlock
           Request B
              ↓
           Gets lock
              ↓
        Re-check availability
              ↓
        Accept / Reject
```

This prevents concurrent requests from making decisions based on the same stale availability state.

---

## 12. Payment Architecture

Payment is intentionally separated from booking state.

### Booking Status

```text
PENDING
CONFIRMED
EXPIRED
```

### Payment Status

```text
PENDING
SUCCESS
FAILED
EXPIRED
```

### Why separate them?

Booking and payment represent different business concepts and have independent state transitions.

A booking can therefore have a payment record without coupling the two state machines into a single field.

---

## 13. Mock Payment Integration

The application uses a mock external payment service to simulate a third-party payment provider.

The integration is isolated inside a payment service.

```text
Booking
   ↓
Payment(PENDING)
   ↓
Mock Payment Service
   ↓
External Payment ID
   ↓
Webhook
```

The external interaction is performed through Python's `requests` library.

The external call is separated from the core booking logic so that the payment provider can be replaced later without rewriting the booking domain.

---

## 14. Payment Webhook

### Endpoint

```http
POST /api/v1/payments/webhook/
```

The webhook processes payment events and updates the corresponding payment and booking states.

### Successful payment

```text
Webhook
   ↓
Payment SUCCESS
   ↓
Booking CONFIRMED
```

### Failed payment

```text
Webhook
   ↓
Payment FAILED
   ↓
Booking remains / transitions to appropriate non-confirmed state
```

The webhook also validates the current payment state to avoid incorrectly processing repeated state transitions.

---

## 15. Testing Strategy

The project uses:

- `pytest`
- `pytest-django`
- Django REST Framework `APIClient`
- `monkeypatch` for external-service mocking

Tests cover:

### Booking

- Successful booking.
- Booking/payment creation.
- Invalid time range.
- Capacity exceeded.
- Invalid/inactive LSA.
- Skill mismatch.

### LSA Search

- Skill-based filtering.
- Availability filtering.
- Concurrent capacity calculation.

### Payment

- Successful payment webhook.
- Failed payment webhook.
- Duplicate/repeated webhook handling.

External payment requests are mocked during tests so the test suite does not depend on a real external service.

This makes the tests:

- deterministic,
- faster,
- independent of network availability,
- safe to run in CI.

---

## 16. Continuous Integration

GitHub Actions is configured to run the test suite automatically on:

```yaml
push:
pull_request:
```

### CI Pipeline

```text
Git Push / Pull Request
        ↓
GitHub Actions
        ↓
Ubuntu Runner
        ↓
PostgreSQL 16
        ↓
Python 3.13
        ↓
Install Dependencies
        ↓
pytest
        ↓
PASS / FAIL
```

The workflow uses a PostgreSQL service container so that CI tests run against PostgreSQL rather than a different local database engine.

---

## 17. Local Setup

### Prerequisites

Install:

- Python 3.13
- PostgreSQL
- Git

### Clone the repository

```bash
git clone <repository-url>
cd habot-booking
```

Then enter the Django project:

```bash
cd haboot-booking
```

### Create virtual environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## 18. Environment Variables

The application expects PostgreSQL configuration through environment variables.

Example:

```env
DB_NAME=habot
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```



---

## 19. Database Setup

Create the required PostgreSQL database and configure the environment variables.

Then run:

```bash
python manage.py migrate
```

To create an administrative user:

```bash
python manage.py createsuperuser
```

---

## 20. Run the Development Server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

---

## 21. Run Tests

From the Django project directory:

```bash
pytest
```

The test suite creates a separate test database and executes the automated tests against the configured Django database backend.

---

## 22. API Testing

The APIs can be tested using Postman or another REST client.

### LSA Search

```http
GET /api/v1/lsas/search/
```

### Booking

```http
POST /api/v1/bookings/
```

### Payment Webhook

```http
POST /api/v1/payments/webhook/
```

Use ISO 8601 datetime values, for example:

```text
2026-08-20T10:00:00Z
```

---

## 23. Design Principles

The implementation follows several backend engineering principles.

### Separation of Concerns

HTTP handling, validation, business logic and persistence are separated.

### Single Responsibility

Individual components focus on specific responsibilities.

### Loose Coupling

The payment integration is isolated from the booking domain.

### Database-side Processing

Filtering and aggregation are performed by PostgreSQL rather than unnecessary Python-side processing.

### Defense in Depth

Input validation, business validation, transactions and database behavior collectively protect data integrity.

### Testability

External dependencies are isolated and mocked during tests.

### Reliable State Transitions

Booking and payment states are explicitly modeled instead of being represented by a single combined state.

---

## 24. Key Engineering Decisions

| Decision | Reason |
|---|---|
| PostgreSQL | Relational integrity, indexing and transaction/locking support |
| Django REST Framework | Structured REST API implementation |
| `ArrayField` | Straightforward representation of LSA skills |
| GIN index | Efficient array containment queries |
| Composite booking index | Supports common booking availability filters |
| Database-side `Count()` | Avoids per-LSA Python/database loops |
| `transaction.atomic()` | Maintains transactional integrity |
| `select_for_update()` | Protects critical booking concurrency |
| Separate Payment model | Independent payment lifecycle |
| Mock payment service | Isolates external integration |
| Pytest | Automated backend testing |
| GitHub Actions | Automated test execution on code changes |

---

## 25. API / Data Flow Summary

```text
                ┌─────────────────┐
                │     Client      │
                └────────┬────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
       LSA Search API          Booking API
              │                     │
              ▼                     ▼
       Availability          Transaction +
          Query               Row Lock
              │                     │
              │                     ▼
              │                 Booking
              │                     │
              │                     ▼
              │                  Payment
              │                     │
              │                     ▼
              │               Mock Payment
              │                     │
              │                     ▼
              │                  Webhook
              │                     │
              └─────────────┬───────┘
                            ▼
                       PostgreSQL
```

---

## 26. Verification

The project has been verified through:

- API testing using Postman.
- Django/Pytest automated tests.
- PostgreSQL-backed test execution.
- GitHub Actions CI.
- Booking edge-case testing.
- Payment webhook testing.
- LSA availability and capacity testing.

The GitHub Actions workflow successfully executes the automated test suite against PostgreSQL.

---

## 27. Future Improvements

The current implementation is intentionally focused on the hiring-project requirements.

Potential production extensions could include:

- Authentication and authorization.
- API rate limiting.
- Structured application logging and monitoring.
- Real payment-provider integration.
- Webhook signature verification.
- Idempotency keys for payment/booking requests.
- Pagination for LSA search.
- API schema generation with OpenAPI/Swagger.
- More granular permission controls.
- Additional database/query performance analysis using `EXPLAIN ANALYZE`.

---

## 28. Conclusion

This project demonstrates a backend implementation focused on:

```text
Reliable APIs
     +
Efficient database queries
     +
Concurrency-safe booking
     +
Separated payment lifecycle
     +
Automated testing
     +
Continuous integration
```

The primary design goal was not only to make the API functional, but to ensure that **availability, booking, payment and data integrity remain reliable under realistic backend conditions**.

---

## Author

**Kanishka Prabha**  
Python Backend Developer

**Email:** `your-email@example.com`  
**GitHub:** `https://github.com/your-username/your-repository`
