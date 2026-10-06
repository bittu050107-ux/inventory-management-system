# Inventory Service

The **Inventory Microservice** manages warehouse stock levels, stock-in, stock-out, and stock adjustment transaction history in the Inventory Management System.

## Architecture
Strictly implements **Clean Layered Architecture**:
- **API Layer**: FastAPI routes (`/inventory`), HTTP Bearer JWT auth, dependencies
- **Application Layer**: DTOs (`inventory_dto.py`) and Application Service (`inventory_service.py`)
- **Domain Layer**: Pure entities (`inventory.py`, `stock_transaction.py`) and abstract repository interface (`inventory_repository.py`)
- **Infrastructure Layer**: PostgreSQL database config, SQLAlchemy models (`InventoryModel`, `StockTransactionModel`), repository implementation (`inventory_repository_impl.py`), internal HTTP client to Product Service (`http://localhost:8003`)

## Port & Endpoints
- **Port**: `8004`
- **Swagger Docs**: [http://localhost:8004/docs](http://localhost:8004/docs)
- **Health Checks**:
  - `GET /health` → `{"status": "ok", "service": "inventory-service"}`
  - `GET /health/db` → `{"database": "postgresql", "status": "connected"}`

## Roles & Permissions
- **READ** (`/inventory`, `/inventory/{product_id}`, `/inventory/low-stock`, `/inventory/{product_id}/transactions`): `ADMIN`, `MANAGER`, `STAFF`, `USER`
- **STOCK-IN** (`/inventory/stock-in`): `ADMIN`, `MANAGER`, `STAFF`
- **STOCK-OUT** (`/inventory/stock-out`): `ADMIN`, `MANAGER`, `STAFF`
- **ADJUSTMENT** (`/inventory/adjust`): `ADMIN`, `MANAGER`
