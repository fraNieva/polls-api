# Polls API

A FastAPI-based polls application with SQLite database.

## Setup

1. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy environment variables:

```bash
cp .env.example .env
```

4. Run the application:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Database

- **Development**: SQLite (`polls.db` file)
- **Production**: PostgreSQL (requires setup)

### PostgreSQL Setup (for production)

1. Install PostgreSQL driver:

```bash
pip install psycopg2-binary
```

2. Update your `.env` file:

```bash
DATABASE_URL=postgresql://username:password@localhost/polls_db
```

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.
