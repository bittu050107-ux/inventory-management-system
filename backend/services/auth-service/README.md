# Auth Service

The **Authentication Microservice** for the Inventory Management System.

Handles JWT-based login with role-based token payloads (ADMIN, MANAGER, STAFF, USER).

---

## Architecture (Clean Architecture)

```
HTTP Request
    ↓
FastAPI Route (app/api/routes/auth.py)
    ↓  [LoginRequest DTO]
Application Service (app/application/services/auth_service.py)
    ↓  [UserRepository interface]
Infrastructure Repository (app/infrastructure/repositories/user_repository_impl.py)
    ↓  [User domain entity]
Domain Entity (app/domain/entities/user.py)
```

**Key Rule**: Each layer only knows about the layer below it via an interface.

---

## Folder Structure

```
app/
├── api/
│   ├── routes/
│   │   └── auth.py          ← POST /auth/login (thin HTTP adapter)
│   └── dependencies.py      ← Dependency injection wiring
│
├── application/
│   ├── dto/
│   │   └── auth_dto.py      ← LoginRequest, LoginResponse (Pydantic)
│   └── services/
│       └── auth_service.py  ← Business logic: find user, verify, generate JWT
│
├── domain/
│   ├── entities/
│   │   └── user.py          ← Pure Python User class + UserRole enum
│   └── repositories/
│       └── user_repository.py ← Abstract interface (find_by_email)
│
├── infrastructure/
│   ├── database/
│   │   └── database.py      ← SQLAlchemy engine + session (ready for models)
│   └── repositories/
│       └── user_repository_impl.py ← In-memory implementation (temporary)
│
├── core/
│   ├── config.py            ← Loads root .env, exposes settings object
│   └── security.py          ← JWT create/decode functions
│
└── main.py                  ← FastAPI app entry point
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the service
uvicorn app.main:app --reload --port 8001

# 3. Open Swagger UI
http://localhost:8001/docs
```

---

## Endpoints

| Method | Path               | Protection  | Description                                      |
|--------|--------------------|-------------|--------------------------------------------------|
| POST   | `/auth/login`      | Public      | Authenticate credentials & receive JWT token     |
| GET    | `/auth/verify`     | Bearer JWT  | Verify token validity & extract identity claims  |
| GET    | `/auth/admin-only` | Role: ADMIN | Admin-only protected route (403 for other roles) |
| GET    | `/auth/user-only`  | Any User    | Protected route for any authenticated user       |
| GET    | `/health`          | Public      | Service health status check                      |

---

## Test Credentials

| Role  | Email                | Password |
|-------|----------------------|----------|
| ADMIN | admin@inventory.com  | admin123 |
| USER  | user@inventory.com   | user123  |

---

## Example Login

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@inventory.com", "password": "admin123"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "ADMIN"
}
```
