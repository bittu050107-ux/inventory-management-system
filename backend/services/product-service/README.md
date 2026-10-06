# Product Service

The **Product Microservice** handles products, categories, and suppliers in the Inventory Management System.

## Architecture
This service strictly adheres to **Clean Architecture / Layered Architecture**:
- **API Layer**: FastAPI routes (`/products`, `/categories`, `/suppliers`), HTTP Bearer JWT auth, dependencies
- **Application Layer**: DTOs and Application Services (`ProductService`, `CategoryService`, `SupplierService`) containing all business rules and validation
- **Domain Layer**: Pure Python entities and abstract repository interfaces (`ProductRepository`, `CategoryRepository`, `SupplierRepository`)
- **Infrastructure Layer**: PostgreSQL database configuration, SQLAlchemy ORM models (`ProductModel`, `CategoryModel`, `SupplierModel`), and concrete repository implementations

## Port & Endpoints
- **Port**: `8003`
- **Swagger Docs**: [http://localhost:8003/docs](http://localhost:8003/docs)
- **Health Checks**:
  - `GET /health` → `{"service": "product-service", "status": "running"}`
  - `GET /health/db` → `{"database": "postgresql", "status": "connected"}`

## Permissions
- **Admin**: Full CRUD on Categories, Suppliers, Products
- **Authenticated User / Staff**: Read-only (GET) access on all resources
- Unauthorized or insufficient role requests receive standard `401 Unauthorized` or `403 Forbidden`.
