# Inventory Management System

A professional, production-ready **Inventory Management System** built with a **Microservices Architecture** following **Clean Architecture** principles.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Services](#services)
- [Authentication and Roles](#authentication-and-roles)
- [Quick Start Local](#quick-start-local)
- [Docker Compose](#docker-compose)
- [API Reference](#api-reference)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [Order Lifecycle](#order-lifecycle)
- [Seeding Demo Data](#seeding-demo-data)

---

## Overview

This system manages products, stock levels, suppliers, and customer orders through a clean microservices backend, unified by an API Gateway, and served by a modern React frontend.

**Key capabilities:**
- JWT-based authentication with role-based access control (ADMIN / MANAGER / STAFF / USER)
- Products and categories management
- Inventory stock tracking with full audit log
- Order creation, lifecycle management, and automatic stock reservation/restoration
- Centralized API Gateway for routing and JWT verification
- SQLite (local dev) or PostgreSQL (Docker/production) support

---

## Architecture

```
                      +-------------------+
                      |  React Frontend   |  :5173
                      |   (Vite + JS)     |
                      +--------+----------+
                               | HTTP (Axios)
                      +--------v----------+
                      |    API Gateway    |  :8000
                      |  FastAPI + JWT    |
                      +--+--+--+--+-------+
                         |  |  |  |
          +--------------+  |  |  +--------------+
          |          +------+  +------+           |
  +-------v------+ +-v-----------+ +-v---------+ +-v----------+
  | Auth Service | |Product Svc  | |Inv. Svc   | |Order Svc   |
  |    :8001     | |   :8003     | |  :8004    | |  :8005     |
  +-------+------+ +------+------+ +-----+-----+ +------+-----+
          |               |              |               |
          +---------------+--------------+---------------+
                                  |
                     +------------v-----------+
                     | SQLite  (local dev)    |
                     | PostgreSQL  (Docker)   |
                     +------------------------+
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Axios, React Router v6 |
| API Gateway | FastAPI (Python 3.11+), httpx |
| Microservices | FastAPI, SQLAlchemy, Pydantic v2 |
| Auth | JWT (python-jose), bcrypt |
| Database (local) | SQLite (zero-config) |
| Database (Docker) | PostgreSQL 16 |
| Containerization | Docker, Docker Compose |
| Architecture | Clean Architecture + Layered Architecture |

---

## Services

| Service | Port | Status | Description |
|---|---|---|---|
| API Gateway | 8000 | Done | Routes all requests; verifies JWT |
| Auth Service | 8001 | Done | Login, register, JWT issue and verify |
| Product Service | 8003 | Done | Products, categories, suppliers CRUD |
| Inventory Service | 8004 | Done | Stock-in/out, adjustments, audit log |
| Order Service | 8005 | Done | Order creation, lifecycle, stock reservation |
| User Service | 8002 | Scaffold | Future: user profile management |
| React Frontend | 5173 | Done | Modern dashboard UI |

---

## Authentication and Roles

All protected endpoints require a `Bearer` JWT token in the `Authorization` header.

| Role | Permissions |
|---|---|
| `ADMIN` | Full access - all CRUD operations |
| `MANAGER` | View and update orders, manage inventory |
| `STAFF` | Stock movements, read products/inventory |
| `USER` | Place orders, view own orders |

Default seed admin: `admin@inventory.com` / `admin123`

---

## Quick Start Local

### Prerequisites
- Python 3.11+
- Node.js 18+
- No external database required (uses SQLite by default)

### Option A - Automated (PowerShell)

```powershell
# From project root - starts all services and frontend
.\start-all.ps1
```

### Option B - Manual

#### 1. Set up each Python service

```powershell
# Example: Auth Service
cd backend/services/auth-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
deactivate
cd ../../..

# Start from project root
$env:PYTHONPATH="backend/services/auth-service"
backend\services\auth-service\.venv\Scripts\uvicorn app.main:app --port 8001
```

Repeat for all services:

| Service | PYTHONPATH | Port |
|---|---|---|
| auth-service | `backend/services/auth-service` | 8001 |
| product-service | `backend/services/product-service` | 8003 |
| inventory-service | `backend/services/inventory-service` | 8004 |
| order-service | `backend/services/order-service` | 8005 |
| api-gateway | `backend/api-gateway` | 8000 |

#### 2. Start the Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend available at: `http://localhost:5173`

#### 3. Seed demo data (optional)

```powershell
python seed_demo_data.py
```

---

## Docker Compose

Runs all services + PostgreSQL + Frontend in containers.

**Prerequisites:** Docker Desktop installed and running.

```bash
# Start everything
docker-compose up --build

# Stop
docker-compose down

# Teardown including volumes
docker-compose down -v
```

After startup:
- Frontend: `http://localhost:5173`
- API Gateway: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

> Note: Docker Compose uses PostgreSQL. The root `.env` `DATABASE_URL` is overridden per-service in `docker-compose.yml` to point to the `postgres` container.

---

## API Reference

All frontend requests go through the **API Gateway** at `http://localhost:8000/api`.

### Auth - `/api/auth`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/login` | Public | Get JWT access token |
| POST | `/api/auth/register` | Public | Register new user |
| GET | `/api/auth/me` | Bearer | Get current user info |
| GET | `/api/auth/verify` | Bearer | Verify token validity |

### Products - `/api/products`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/products` | Bearer | List all products |
| POST | `/api/products` | Admin | Create product |
| GET | `/api/products/{id}` | Bearer | Get product by ID |
| PUT | `/api/products/{id}` | Admin | Update product |
| DELETE | `/api/products/{id}` | Admin | Delete product |
| GET | `/api/products/categories` | Bearer | List categories |
| POST | `/api/products/categories` | Admin | Create category |
| GET | `/api/products/suppliers` | Bearer | List suppliers |
| POST | `/api/products/suppliers` | Admin | Create supplier |

### Inventory - `/api/inventory`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/inventory` | Bearer | All inventory records |
| GET | `/api/inventory/low-stock` | Bearer | Low stock alerts |
| GET | `/api/inventory/product/{id}` | Bearer | Stock for product |
| POST | `/api/inventory/stock-in` | Staff+ | Add stock |
| POST | `/api/inventory/stock-out` | Staff+ | Deduct stock |
| POST | `/api/inventory/adjust` | Manager+ | Adjust stock |
| GET | `/api/inventory/transactions/{id}` | Bearer | Audit log for product |

### Orders - `/api/orders`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/orders` | Bearer | Create order |
| GET | `/api/orders` | Manager+ | All orders |
| GET | `/api/orders/my` | Bearer | My orders |
| GET | `/api/orders/{id}` | Bearer | Get order |
| PATCH | `/api/orders/{id}/status` | Manager+ | Update order status |
| POST | `/api/orders/{id}/cancel` | Bearer | Cancel order |
| DELETE | `/api/orders/{id}` | Admin | Delete order |

---

## Environment Variables

All services load from the single root `.env` file:

```env
APP_ENV=development

JWT_SECRET_KEY=change-this-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# SQLite for local dev (no install needed)
DATABASE_URL=sqlite:///./inventory.db
# PostgreSQL for Docker/production:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/inventory_db

ADMIN_SEED_EMAIL=admin@inventory.com
ADMIN_SEED_PASSWORD=admin123

API_GATEWAY_URL=http://localhost:8000
AUTH_SERVICE_URL=http://localhost:8001
USER_SERVICE_URL=http://localhost:8002
PRODUCT_SERVICE_URL=http://localhost:8003
INVENTORY_SERVICE_URL=http://localhost:8004
ORDER_SERVICE_URL=http://localhost:8005
FRONTEND_URL=http://localhost:5173
```

> Security: Never commit `.env` to version control. The `.gitignore` already excludes it.

---

## Project Structure

```
inventory-management-system/
|
+-- .env                        <- Single root env file (not committed)
+-- .gitignore
+-- docker-compose.yml          <- Orchestrates all containers
+-- start-all.ps1               <- PowerShell script to run locally
+-- seed_demo_data.py           <- Populates demo data
+-- README.md
|
+-- frontend/                   <- React + Vite SPA
|   +-- src/
|   |   +-- services/           <- Axios API clients
|   |   +-- components/         <- Reusable UI components
|   |   +-- pages/              <- Route-level page components
|   |   +-- context/            <- Auth context (JWT storage)
|   |   +-- main.jsx
|   +-- Dockerfile
|   +-- nginx.conf
|
+-- backend/
    +-- api-gateway/            <- FastAPI proxy + JWT verification :8000
    |   +-- app/
    |   |   +-- routes/         <- Per-service proxy routes
    |   |   +-- main.py
    |   +-- Dockerfile
    |
    +-- services/
        +-- auth-service/       <- :8001
        +-- user-service/       <- :8002 (scaffold)
        +-- product-service/    <- :8003
        +-- inventory-service/  <- :8004
        +-- order-service/      <- :8005

        Each service follows Clean Architecture:
        app/
        +-- core/           <- Config, exceptions, security
        +-- domain/         <- Pure entities + repository interfaces
        +-- application/    <- Business logic (services + DTOs)
        +-- infrastructure/ <- SQLAlchemy models, DB, HTTP clients
        +-- api/            <- FastAPI routes (thin layer only)
```

---

## Order Lifecycle

```
PENDING --> CONFIRMED --> SHIPPED --> DELIVERED
   |              |
   v              v
CANCELLED     CANCELLED
```

- **PENDING** - Order created, stock reserved immediately
- **CONFIRMED** - Admin/Manager confirmed
- **SHIPPED** - Dispatched to customer
- **DELIVERED** - Customer received
- **CANCELLED** - Stock automatically restored to inventory

---

## Seeding Demo Data

With all services running:

```powershell
python seed_demo_data.py
```

Creates:
- 3 product categories (Electronics, Furniture, Stationery)
- 2 suppliers
- 5 sample products with initial stock
- 2 sample orders

Login credentials after seeding:
- **Email:** `admin@inventory.com`
- **Password:** `admin123`
