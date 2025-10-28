# 🗳️ Polls API

A production-ready FastAPI-based polling application with comprehensive features, authentication, and extensive test coverage. Built with modern Python practices and designed for scalability.

## 🚀 Features

### 📊 Core Functionality

- **Poll Management**: Create, read, update, and delete polls with comprehensive validation
- **Poll Options**: Dynamic option management with duplicate detection and limits
- **Voting System**: Atomic voting with vote counting and duplicate prevention
- **Real-time Results**: Live vote counts with percentage calculations

### 🔐 Security & Authentication

- **JWT Authentication**: Secure token-based authentication with configurable expiration
- **Password Security**: bcrypt hashing with 12 rounds for maximum security
- **Access Control**: Owner-based permissions for poll management
- **Rate Limiting**: Configurable limits to prevent abuse and spam

### 🌐 Public/Private Polls

- **Flexible Visibility**: Choose between public polls (everyone can see) or private polls (owner-only)
- **Smart Access Control**: Anonymous users see public polls, authenticated users see public + own private polls
- **Privacy Filtering**: Database-level filtering ensures private data never leaks

### 📱 Frontend-Ready API

- **Complete Poll Data**: Single endpoint returns polls with options, vote counts, and user context
- **Calculated Percentages**: Server-side percentage calculations for immediate UI rendering
- **User Voting Status**: Built-in user context (has voted, which option) eliminates extra API calls
- **React Optimized**: Designed for optimal React/TypeScript integration

### 🔍 Advanced Querying

- **Pagination**: Efficient pagination with metadata for all list endpoints
- **Search**: Full-text search across poll titles and descriptions
- **Filtering**: Filter by active status, owner, creation date, and more
- **Sorting**: Multiple sorting options with enum validation

### 📚 Enterprise-Grade Documentation

- **OpenAPI 3.0**: Complete API documentation with examples for all endpoints
- **Error Handling**: Structured error responses with detailed context and error codes
- **Type Safety**: Full Pydantic schema validation with TypeScript-ready models

## 🛠️ Technology Stack

- **Framework**: FastAPI 0.119.0 with async support
- **Database**: SQLAlchemy 2.0.44 with SQLite (dev) / PostgreSQL (prod)
- **Authentication**: JWT with python-jose and bcrypt password hashing
- **Validation**: Pydantic v2 with comprehensive business rule validation
- **Testing**: pytest with 85%+ coverage (148 passing tests)
- **Code Quality**: Comprehensive linting, type hints, and documentation

## 📖 API Overview

### 🗳️ Poll Endpoints

```
GET    /api/v1/polls/              # List polls (paginated, filtered, searchable)
POST   /api/v1/polls/              # Create new poll
GET    /api/v1/polls/{poll_id}     # Get poll with options and vote data
PUT    /api/v1/polls/{poll_id}     # Update poll (owner only)
DELETE /api/v1/polls/{poll_id}     # Delete poll (owner only)
GET    /api/v1/polls/my-polls      # Get current user's polls
```

### 📋 Poll Options Endpoints

```
POST   /api/v1/polls/{poll_id}/options          # Add option to poll
```

### 🗳️ Voting Endpoints

```
POST   /api/v1/polls/{poll_id}/vote/{option_id} # Vote on poll option
```

### 👤 User Endpoints

```
POST   /api/v1/auth/register      # Register new user
POST   /api/v1/auth/token         # Login and get JWT token
GET    /api/v1/users/me           # Get current user profile
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip (Python package installer)

### Installation

1. **Clone the repository**:

```bash
git clone https://github.com/yourusername/polls-api.git
cd polls-api
```

2. **Create and activate virtual environment**:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize the database** (optional - includes sample data):

```bash
python migration.db.py
```

6. **Run the application**:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### 📚 Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 💾 Database Configuration

### Development (SQLite)

The application uses SQLite by default for development:

- Database file: `polls.db`
- Automatic creation on first run
- Perfect for local development and testing

### Production (PostgreSQL)

1. **Install PostgreSQL driver**:

```bash
pip install psycopg2-binary
```

2. **Update environment variables**:

```bash
DATABASE_URL=postgresql://username:password@localhost/polls_db
```

3. **Database will be created automatically** on first connection.

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_poll_endpoints.py -v
```

### Test Coverage

- **148 passing tests** with 85%+ coverage
- Comprehensive endpoint testing
- Business logic validation
- Error scenario coverage
- Authentication and authorization testing

## 📱 Frontend Integration

### React/TypeScript Example

```typescript
interface Poll {
  id: number;
  title: string;
  description?: string;
  is_active: boolean;
  is_public: boolean;
  owner_id: number;
  pub_date: string;
  options: PollOption[];
  total_votes: number;
  user_has_voted: boolean;
  user_vote_option_id?: number;
}

interface PollOption {
  id: number;
  text: string;
  vote_count: number;
  percentage: number;
  poll_id: number;
}

// Fetch poll with complete data
const poll = await fetch("/api/v1/polls/1").then((r) => r.json());
```

### API Client Examples

#### Authentication

```bash
# Register new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "securepass123"}'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=securepass123"
```

#### Create Poll

```bash
curl -X POST "http://localhost:8000/api/v1/polls/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Favorite Programming Language",
    "description": "Choose your preferred language",
    "is_public": true
  }'
```

#### Vote on Poll

```bash
curl -X POST "http://localhost:8000/api/v1/polls/1/vote/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🏗️ Project Structure

```
polls-api/
├── app/
│   ├── api/v1/               # API endpoints and utilities
│   │   ├── endpoints/        # Individual endpoint modules
│   │   ├── responses/        # Centralized response definitions
│   │   └── utils/           # Reusable utilities (pagination, etc.)
│   ├── core/                # Core functionality
│   │   ├── config.py        # Configuration settings
│   │   ├── security.py      # Authentication and security
│   │   └── constants.py     # Application constants
│   ├── db/                  # Database configuration
│   ├── models/              # SQLAlchemy database models
│   └── schemas/             # Pydantic validation schemas
├── tests/                   # Comprehensive test suite
├── migration.db.py          # Database migration and sample data
├── main.py                  # FastAPI application entry point
└── requirements.txt         # Python dependencies
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///./polls.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Development
DEBUG=true
```

### Business Rules Configuration

- **Max polls per user**: 50
- **Max options per poll**: 10
- **Rate limiting**: 5 polls/hour, 10 updates/hour
- **Vote limits**: 50 votes/user/day

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add comprehensive tests for new features
- Update documentation for API changes
- Ensure backward compatibility
- Use type hints throughout the codebase

## 📈 Performance

- **Optimized Queries**: Eager loading prevents N+1 query problems
- **Database Indexing**: Strategic indexes on frequently queried fields
- **Pagination**: Efficient offset-based pagination for large datasets
- **Caching Ready**: Structured for Redis caching implementation
- **Connection Pooling**: SQLAlchemy connection pooling for production

## 🔒 Security Features

- **Input Validation**: Comprehensive Pydantic validation
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **Password Security**: bcrypt hashing with configurable rounds
- **JWT Security**: Secure token generation with expiration
- **Rate Limiting**: Protection against abuse and spam
- **Error Handling**: No sensitive data in error responses

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Franco Nieva** - [GitHub Profile](https://github.com/franconieva)

## 🙏 Acknowledgments

- FastAPI team for the excellent framework
- SQLAlchemy for the powerful ORM
- Pydantic for data validation
- pytest for testing infrastructure

---

⭐ **Star this repo** if you find it helpful!

📫 **Questions?** Open an issue or reach out via GitHub.
