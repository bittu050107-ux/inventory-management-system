# API Gateway Microservice

The **API Gateway** serves as the unified reverse-proxy entry point for the Inventory Management System on **port 8000**.

All client applications (e.g. React Frontend on `:5173`) communicate exclusively with this Gateway. The Gateway transparently forwards requests to internal microservices while handling CORS, timeouts, and service availability errors.

---

## Architecture Flow

```
React Frontend (:5173)
       ↓
API Gateway (:8000)
       ↓  (forwards request & preserves Authorization header)
 ┌───────────────┐
 │ Auth Service  │ (:8001)
 └───────────────┘
```

---

## Active Proxy Routes

| Method | Gateway Endpoint | Forwarded Downstream Target | Header Forwarding | Purpose |
|---|---|---|---|---|
| `POST` | `/api/auth/login` | `http://localhost:8001/auth/login` | Content-Type | Client login & JWT issuance |
| `GET` | `/api/auth/me` | `http://localhost:8001/auth/me` | Bearer Authorization | Current user identity resolution |
| `GET` | `/api/auth/admin-test` | `http://localhost:8001/auth/admin-test` | Bearer Authorization | Admin privilege verification |
| `GET` | `/health` | (Handled directly by Gateway) | None | Gateway health check |

---

## Error Handling

- **503 Service Unavailable**: If Auth Service is unreachable or offline, the Gateway returns:
  ```json
  {
    "detail": "Auth service unavailable"
  }
  ```
- **504 Gateway Timeout**: If Auth Service takes longer than configured timeout to respond.
- **Client Status Preservation**: 400, 401, 403, and 422 responses from Auth Service are passed directly back to the client without alteration.

---

## Installation & Running

### 1. Install Dependencies
```bash
cd backend/api-gateway
pip install -r requirements.txt
```

### 2. Start API Gateway
```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Open Swagger UI
Visit: **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## Testing Through the Gateway

### 1. Health Check
```bash
curl -X GET http://localhost:8000/health
```
```json
{
  "service": "api-gateway",
  "status": "running"
}
```

### 2. Login via Gateway
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@inventory.com", "password": "admin123"}'
```
```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer",
  "role": "ADMIN"
}
```

### 3. Identity Check (`/api/auth/me`)
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <JWT_TOKEN>"
```
```json
{
  "user_id": "1",
  "role": "ADMIN"
}
```

### 4. Admin Privilege Check (`/api/auth/admin-test`)
```bash
curl -X GET http://localhost:8000/api/auth/admin-test \
  -H "Authorization: Bearer <JWT_TOKEN>"
```
```json
{
  "message": "Welcome Admin",
  "role": "ADMIN"
}
```
