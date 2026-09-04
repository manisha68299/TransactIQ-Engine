# TransactIQ Engine

Real-Time E-Commerce Analytics Engine — backend service that processes transactions, performs analytics and fraud detection, and supports CSV bulk imports.

Project artifacts
- FastAPI backend (app/)
- SQLAlchemy models, Pydantic schemas, CRUD layer
- Analytics pipeline using pandas / numpy
- Data cleaning & import scripts (data/)
- Deployment assets and diagrams (assets/)

Live deployment
- Render URL: <REPLACE_WITH_YOUR_RENDER_URL>

Architecture
- See assets/architecture-diagram.png for architecture and components.

Quickstart — run locally
1. Clone and create virtualenv

   git clone https://github.com/manisha68299/TransactIQ-Engine.git
   cd TransactIQ-Engine
   python -m venv .venv
   .venv\Scripts\activate     # Windows CMD: .venv\Scripts\activate

2. Install dependencies

   pip install -r requirements.txt

3. Set environment variables (example on Windows CMD)

   set DATABASE_URL=sqlite:///./ecommerce.db
   set SECRET_KEY=your-secret-key
   set LOG_LEVEL=INFO
   set REDIS_URL=redis://localhost:6379/0

4. Start the app (development)

   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

5. Start the background worker (for queued CSV processing)

   python worker.py

Useful endpoints
- GET / → health check
- GET /docs → Swagger UI
- POST /api/auth/token → get JWT token (body: username, password) (demo user exists)
- POST /api/upload/enqueue → enqueue CSV for background processing (protected)
- POST /api/upload/csv → synchronous CSV upload (public)
- Existing routes under /api/transactions and /api/analytics

Docker / Render
- A Dockerfile, Procfile and render.yaml exist. On Render set env vars: DATABASE_URL, SECRET_KEY, REDIS_URL and add a Redis service.
- Procfile/Dockerfile run the app with gunicorn + uvicorn workers.

Notes
- The demo authentication uses a fake_users_db in app/auth.py (for demo only). Replace with DB-backed users for production.
- Ensure SECRET_KEY and other secrets are set as environment variables in Render or your deployment environment.