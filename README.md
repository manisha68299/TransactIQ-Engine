# Real-Time E-Commerce Analytics Engine

> **A FastAPI-based backend for processing e-commerce transactions, generating business analytics, detecting suspicious transactions, and exposing the results through REST APIs.**

**Live API:** https://transactiq-engine-134r.onrender.com/  
**API Documentation:** https://transactiq-engine-134r.onrender.com/docs

---

## Problem Statement

E-commerce systems generate a large volume of transaction data, but raw transaction records alone do not provide useful business insight. Businesses need a backend system that can store transactions reliably, validate incoming data, identify potentially suspicious transactions, and turn transaction records into useful metrics such as revenue, city-wise performance, payment-method distribution, customer spending, and daily trends.

The goal of this project is to provide a single backend service that handles these tasks through a structured API.

---

## Solution

The **Real-Time E-Commerce Analytics Engine** provides a backend layer that:

- Accepts and validates transaction data.
- Stores transactions using SQLAlchemy.
- Provides CRUD operations and filtered transaction retrieval.
- Calculates revenue and statistical metrics.
- Analyzes revenue by city and payment method.
- Tracks daily transaction trends.
- Identifies top users by spending.
- Flags transactions above a configurable suspicious-amount threshold.
- Supports CSV-based bulk transaction processing.
- Provides JWT-based authentication.
- Adds request rate limiting, CORS, trusted-host handling, and global error handling.
- Maintains application and transaction logs.
- Provides Swagger and ReDoc API documentation.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core development language |
| **FastAPI** | REST API framework |
| **SQLAlchemy** | ORM and database operations |
| **SQLite / PostgreSQL-ready configuration** | Transaction data storage |
| **Pandas** | Data processing and analytics |
| **NumPy** | Numerical and statistical calculations |
| **Pydantic** | Request and response validation |
| **JWT** | API authentication |
| **Passlib** | Password hashing |
| **SlowAPI** | API rate limiting |
| **Cachetools** | TTL-based in-memory caching |
| **Gunicorn + Uvicorn** | Production server |
| **Render** | Cloud deployment |

---

## Key Features

### 1. Transaction Management

Transactions contain information such as:

- User ID
- Amount
- City
- Payment method
- Suspicious status
- Timestamp
- Unique reference ID

The database layer supports creating, retrieving, filtering, counting, and bulk-inserting transactions.

### 2. Business Analytics

The analytics engine generates:

- Total revenue
- Transaction count
- Average, minimum, and maximum transaction value
- Median
- Standard deviation and variance
- Percentiles and IQR
- City-wise revenue
- Payment-method analysis
- Daily revenue trends
- Top users by spending
- Executive summary

### 3. Suspicious Transaction Detection

A configurable amount threshold is used to flag suspicious transactions. The default threshold is **$10,000**, and it can be changed through environment configuration.

### 4. CSV Upload

The API supports CSV upload for bulk transaction processing. Required CSV fields are:

```text
user_id, amount, city, payment_method
```

The upload configuration also supports a configurable maximum file size and allowed upload formats.

### 5. Authentication

The backend uses OAuth2 bearer authentication with JWT tokens. Passwords are handled through Passlib hashing, and the JWT secret and token expiry can be configured through environment variables.

> The current authentication implementation contains a demo in-memory user (`admin`). It should be replaced with database-backed user management before production use.

### 6. Logging and Error Handling

The application logs:

- API requests
- Transactions
- Suspicious transactions
- Database operations
- CSV uploads
- Analytics generation
- Errors
- Cache operations

A global exception handler is also configured to return a controlled `500` response instead of exposing an unhandled application failure.

---

## Project Structure

```text
transactiq/
│
├── app/
│   ├── main.py              # FastAPI application and middleware
│   ├── auth.py              # JWT authentication and password handling
│   ├── config.py            # Environment and application configuration
│   ├── database.py          # Database engine and sessions
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── crud.py              # Database CRUD operations
│   ├── analytics.py         # Business analytics engine
│   ├── cache.py             # TTL cache helper
│   ├── logger.py            # Application logging
│   ├── tasks.py             # CSV/background-processing helpers
│   ├── utils.py             # Common validation and formatting utilities
│   └── routes/
│       ├── transaction_routes.py
│       ├── analytics_routes.py
│       ├── auth_routes.py
│       ├── upload_routes.py
│       └── bulk_routes.py
│
├── data/                    # Sample/input data
├── assets/                  # Project assets
├── logs/                    # Application logs
├── requirements.txt
├── Procfile
├── Dockerfile
├── render.yaml
├── worker.py
└── README.md
```

---

## API Overview

### Health & Documentation

```text
GET /
GET /docs
GET /redoc
GET /docs-summary
```

### Transactions

```text
POST /api/transactions
GET  /api/transactions
GET  /api/transactions/{transaction_id}
GET  /api/transactions/by-city/{city}
GET  /api/transactions/by-user/{user_id}
GET  /api/transactions/suspicious/all
```

### Analytics

```text
GET /api/analytics/revenue
GET /api/analytics/top-cities
GET /api/analytics/payment-analysis
GET /api/analytics/daily-trends
GET /api/analytics/top-users
GET /api/analytics/statistics
GET /api/analytics/summary
```

### CSV

```text
POST /api/upload/csv
```

For the complete request/response schemas, open the **Swagger UI** at `/docs`.

---

## Configuration

Create a `.env` file for local development:

```env
DATABASE_URL=sqlite:///./ecommerce.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

ENV=development
LOG_LEVEL=INFO
DATABASE_ECHO=False

SUSPICIOUS_TRANSACTION_THRESHOLD=10000
MAX_TRANSACTION_AMOUNT=50000
MIN_TRANSACTION_AMOUNT=1
```

For Render, set the environment variables in the service's **Environment** section instead of committing `.env`.

For production, `SECRET_KEY` must be provided through the environment.

---

## How to Run Locally

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd <your-project-folder>
```

### 2. Create a virtual environment

**Windows:**

```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create `.env` and add the required configuration shown above.

### 5. Start the application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### 6. Open API documentation

Go to:

```text
http://127.0.0.1:8000/docs
```

You can test the endpoints directly from Swagger.

---

## Deployment

The project is configured for deployment on **Render** using Gunicorn with Uvicorn workers.

Production start command:

```bash
gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT --workers 4
```

The deployed service is currently available at:

**https://transactiq-engine-134r.onrender.com/**

After deployment, verify:

1. `/` returns the healthy service response.
2. `/docs` opens Swagger UI.
3. Database environment variables are correctly configured.
4. `SECRET_KEY` is set in production.
5. If background processing is enabled, `REDIS_URL` is configured for the worker.

---

## Current Status

| Area | Status |
|---|---|
| FastAPI backend | Completed |
| Transaction CRUD | Completed |
| Database layer | Completed |
| Pydantic validation | Completed |
| Business analytics | Completed |
| Suspicious transaction detection | Completed |
| JWT authentication | Implemented |
| CSV upload | Implemented |
| Logging | Implemented |
| Rate limiting | Implemented |
| API documentation | Completed |
| Local configuration | Completed |
| Render deployment | Deployed |
| In-memory caching | Implemented |
| Background CSV processing | Basic scaffold / needs further integration |
| Production user database | Not yet implemented |

---

## Notes

The project is currently designed as a backend analytics engine rather than a complete customer-facing e-commerce application. The main focus is transaction processing, analytics, API design, validation, security, and deployment.

For a production-scale version, the next improvements would be database-backed user management, Redis-based shared caching, fully integrated background job processing, stronger production security configuration, and automated testing.

---

## Author

**Manisha Banerjee**  
B.Tech Information Technology  
Backend & Data Analytics Project

