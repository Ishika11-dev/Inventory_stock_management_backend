# Inventory Stock Management Backend

A backend REST API for managing inventory, products, categories, and suppliers.

The project is built using **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **Alembic**. It follows a modular architecture with separate models, schemas, services, routes, utilities, and database configuration.It also includes **JWT-based authentication**, **Role-Based Access Control (RBAC)**, pagination, search, filtering, and stock management.

---

## 🚀 Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python** | Programming language |
| **FastAPI** | Backend web framework |
| **PostgreSQL** | Relational database |
| **SQLAlchemy** | ORM |
| **Alembic** | Database migrations |
| **Pydantic** | Data validation |
| **JWT** | Authentication |
| **Passlib / Password Hashing** | Secure password storage |
| **Uvicorn** | ASGI server |
| **Git & GitHub** | Version control |



---
# ⚙️ Installation

## 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd backend
```

## 2. Create a virtual environment

```bash
python -m venv .venv
```

## 3. Activate the virtual environment

### Windows PowerShell

```bash
.venv\Scripts\activate
```

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:54323/inventory_db
```

Replace `YOUR_PASSWORD` with your PostgreSQL password.

> Do not upload `.env` to GitHub.

## 6. Run database migrations

```bash
alembic upgrade head
```

## 7. Start the FastAPI server

```bash
uvicorn app.main:app --reload
```

---



# 📖 API Documentation

Once the server is running, open:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

---

## 🌐 Frontend Integration

The Angular frontend communicates with the FastAPI backend through HTTP APIs.

### 1. Clone the Frontend Repository

Clone the frontend project:

```bash
git clone <frontend-github-repository-url>
cd <frontend-project-folder>
```

Install the frontend dependencies:

```bash
npm install
```

Start the Angular application:

```bash
ng serve
```

The frontend will normally run at:

```text
http://localhost:4200
```

---

### 2. Backend URL

Start the FastAPI backend:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

For a frontend running on the same computer, use:

```text
http://127.0.0.1:8000
```


---

### 3. API Base URL

The Angular frontend should use the backend URL as its API base URL.

Example:

```typescript
private apiUrl = 'http://xyz:8000';
```

---

### 4. API Modules & Endpoints Overview

The backend exposes 9 active modular API routes under `/api/v1`:

1. **Authentication** (`/api/v1/auth`): Register, Login, Refresh, Logout (with RevokedToken blacklist).
2. **Users & Teams** (`/api/v1/users`): Super admin user list, team retrieval by managers, role updates.
3. **Categories** (`/api/v1/categories`): Category CRUD with soft deletion.
4. **Suppliers** (`/api/v1/suppliers`): Supplier CRUD with soft deletion.
5. **Products** (`/api/v1/products`): Full product management, SKU validation, stock adjustments (IN/OUT), pagination, and inventory summary metrics.
6. **Customers** (`/api/v1/customers`): Customer contact and profile CRUD.
7. **Orders** (`/api/v1/orders`): Order placement, item calculation, inventory availability check, and status state machine.
8. **Tasks** (`/api/v1/tasks`): Manager-to-staff duty delegation and task-based access control (ABAC).
9. **Delivery Predictions** (`/api/v1/predictions`): Machine Learning (XGBoost) delivery fulfillment forecasting.

> 📖 **Full API Reference**: For exhaustive details, payloads, request bodies, and responses for every endpoint, see [API_DOCUMENTATION.md](file:///c:/Users/Ishika/Desktop/inv-mgmt/backend/API_DOCUMENTATION.md).


---

### 5. Frontend → Backend Flow

```text
Angular Frontend
       ↓
   HttpClient
       ↓
   FastAPI API
       ↓
  Service Layer
       ↓
   SQLAlchemy
       ↓
  PostgreSQL
       ↓
   FastAPI Response
       ↓
 Angular Frontend
```

---


## 📁 Project Structure

```text
backend/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── categories.py
│   │       ├── products.py
│   │       └── suppliers.py
│   │
│   ├── controllers/
│   │   ├── auth_controller.py
│   │   ├── category_controller.py
│   │   ├── product_controller.py
│   │   └── supplier_controller.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   └── security.py
│   │
│   ├── models/
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── supplier.py
│   │   └── user.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── category.py
│   │   ├── product.py
│   │   └── supplier.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── category_service.py
│   │   ├── product_service.py
│   │   └── supplier_service.py
│   │
│   ├── utils/
│   │   ├── constraints.py
│   │   └── exceptions.py
│   │
│   └── main.py
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── .env
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```
## 👩‍💻 Author

Ishika

Inventory Stock Management Backend developed using FastAPI, PostgreSQL, SQLAlchemy, and Alembic.
