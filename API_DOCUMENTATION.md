# Inventory & Stock Management System - Backend Documentation

Comprehensive architecture, end-to-end workflows, role-based access control (RBAC), and complete API endpoint reference with sample payloads for the **Inventory & Stock Management** backend.

---

## 📑 Table of Contents
1. [System Overview & Architecture](#system-overview--architecture)
2. [Database Schema & Data Models](#database-schema--data-models)
3. [Authentication & Authorization (RBAC + ABAC)](#authentication--authorization-rbac--abac)
4. [End-to-End Business Workflows](#end-to-end-business-workflows)
   - [Authentication & Session Flow](#1-authentication--session-lifecycle)
   - [Product & Inventory Management Flow](#2-product--inventory-management-flow)
   - [Order Lifecycle & State Transitions](#3-order-processing--status-state-machine)
   - [Manager-Staff Task Delegation Flow](#4-manager-staff-task-delegation--abac-flow)
   - [Machine Learning Delivery Prediction Flow](#5-machine-learning-delivery-prediction-flow)
5. [Complete API Endpoints Reference & Sample Payloads](#complete-api-endpoints-reference)
   - [Authentication Endpoints (`/api/v1/auth`)](#1-authentication-endpoints-apiv1auth)
   - [Users & Team Endpoints (`/api/v1/users`)](#2-users--team-management-apiv1users)
   - [Category Endpoints (`/api/v1/categories`)](#3-categories-apiv1categories)
   - [Supplier Endpoints (`/api/v1/suppliers`)](#4-suppliers-apiv1suppliers)
   - [Product Endpoints (`/api/v1/products`)](#5-products-apiv1products)
   - [Customer Endpoints (`/api/v1/customers`)](#6-customers-apiv1customers)
   - [Order Endpoints (`/api/v1/orders`)](#7-orders-apiv1orders)
   - [Task Delegation Endpoints (`/api/v1/tasks`)](#8-task-management-apiv1tasks)
   - [ML Delivery Prediction Endpoints (`/api/v1/predictions`)](#9-delivery-prediction-apiv1predictions)
6. [Setup, Execution & Database Migrations](#setup-execution--database-migrations)

---

## System Overview & Architecture

The backend is built with **FastAPI** following a multi-tier layered architecture:

```
FastAPI Router (app/api/v1)
        ↓
Controller Layer (app/controllers) -> Translates HTTP & maps custom exceptions
        ↓
Service Layer (app/services)       -> Encapsulates business logic, state machines & rules
        ↓
ORM & Data Access (SQLAlchemy)     -> Maps models, relations, transactions & constraints
        ↓
PostgreSQL Database                -> Relational storage with UUID primary keys & foreign keys
```

### Key Technical Characteristics
- **Framework**: FastAPI (Python 3.10+) with Uvicorn ASGI server.
- **Database & ORM**: PostgreSQL via SQLAlchemy 2.0 with Alembic database migrations.
- **Identity & Keys**: All entity IDs use standard `UUIDv4`.
- **Validation**: Strict typing and request/response serialisation with Pydantic v2.
- **Security**: JWT dual-token mechanism (short-lived access tokens + HttpOnly cookie refresh tokens) with instant database token revocation (`RevokedToken`).
- **Machine Learning**: Integrated XGBoost regressor (`xgboost-v2`) predicting order delivery fulfillment days based on stock, shortage, and supplier lead times.

---

## Database Schema & Data Models

| Entity | Table Name | Key Attributes | Notes & Relations |
|---|---|---|---|
| **User** | `users` | `id` (UUID), `username`, `email`, `password_hash`, `role`, `manager_id` | Self-referencing FK `manager_id -> users.id` for hierarchical reporting. |
| **RevokedToken**| `revoked_tokens` | `id`, `jti` (UUID), `expires_at`, `token_type` | Revocation blacklist for access & refresh tokens on logout. |
| **Category** | `categories` | `id`, `name`, `description`, `is_deleted`, `created_at` | Soft delete via `is_deleted = True`. 1-to-N with `products`. |
| **Supplier** | `suppliers` | `id`, `name`, `contact_email`, `phone`, `address`, `is_deleted` | Soft delete via `is_deleted = True`. 1-to-N with `products`. |
| **Product** | `products` | `id`, `name`, `sku`, `category_id`, `supplier_id`, `unit_price`, `quantity_in_stock`, `reorder_level`, `is_active` | FK to `categories` and `suppliers`. Unique SKU. Computed `stock_status`. |
| **Customer** | `customers` | `id`, `name`, `email`, `phone`, `address`, `created_at`, `updated_at` | 1-to-N with `orders`. |
| **Order** | `orders` | `id`, `customer_id`, `order_date`, `status`, `total_amount`, `predicted_delivery_date`, `actual_delivery_date` | FK to `customers`. Cascades to `order_items` and `order_tracking`. |
| **OrderItem** | `order_items` | `id`, `order_id`, `product_id`, `quantity`, `unit_price`, `subtotal` | FK to `orders` and `products`. |
| **OrderTracking**| `order_tracking` | `id`, `order_id`, `status`, `timestamp`, `notes` | Audit trail of order status transitions. |
| **Task** | `tasks` | `id`, `title`, `description`, `priority`, `status`, `due_date`, `assigned_to_id`, `assigned_by_id`, `target_type`, `target_id` | FK to `users` for creator & assignee. Polymorphic link to `PRODUCT`, `CATEGORY`, `SUPPLIER`. |
| **PurchaseOrder**| `purchase_orders` | `id`, `supplier_id`, `status`, `order_date`, `expected_date`, `received_date` | B2B supplier procurement tracking. |
| **StockMovement**| `stock_movements` | `id`, `product_id`, `quantity`, `movement_type`, `reference_id` | Audit log of inventory adjustments. |

---

## Authentication & Authorization (RBAC + ABAC)

### 1. User Roles
The application defines 5 distinct user roles:
1. `SUPER_ADMIN`: Root privileges. Can view/manage all users, roles, tasks, categories, suppliers, and products.
2. `INVENTORY_MANAGER`: Manages inventory staff, creates inventory tasks, and has unrestricted write access to products, categories, and suppliers.
3. `ORDER_MANAGER`: Manages order staff, creates order tasks, and tracks customer orders.
4. `INVENTORY_STAFF`: Field operator. Can only create or edit products, categories, and suppliers if assigned an active task for that item.
5. `ORDER_STAFF`: Handles fulfillment tasks assigned by the order manager.

### 2. Safeguards & Access Control Rules
- **Bootstrap Rule**: The first user ever registered automatically receives the `SUPER_ADMIN` role. All subsequent registrations default to `INVENTORY_STAFF`.
- **Last Super Admin Protection**: The system prevents demoting or deleting the last active `SUPER_ADMIN`.
- **Staff-Manager Relationship**:
  - `INVENTORY_MANAGER` can only assign tasks to `INVENTORY_STAFF`.
  - `ORDER_MANAGER` can only assign tasks to `ORDER_STAFF`.
  - Once a staff member is assigned to a manager, other managers cannot reassign or hijack that staff member.
- **Attribute-Based Access Control (Task-Gated Mutations)**:
  - **Read Access**: All authenticated users can view/list products, categories, suppliers, orders, and customer records.
  - **Write Access (Create)**:
    - Super admins & managers: Allowed unconditionally.
    - Staff members: Must have an active (`status != 'COMPLETED'`) task matching `target_type` (e.g. `PRODUCT`).
  - **Write Access (Update / Delete / Stock Adjust)**:
    - Super admins & managers: Allowed unconditionally.
    - Staff members: Must have an active task where `target_type == entity` AND `target_id == record.id`.

---

## End-to-End Business Workflows

### 1. Authentication & Session Lifecycle
```text
Client                          FastAPI Backend                 Database
  |                                   |                            |
  |--- POST /auth/register ---------->|-- Verify email & count --->|
  |                                   |-- Hash password (bcrypt) ->|
  |<-- 201 Created (User details) ----|-- Save user --------------->|
  |                                   |                            |
  |--- POST /auth/login ------------->|-- Verify password --------->|
  |                                   |-- Generate Access Token    |
  |                                   |-- Generate Refresh Token   |
  |<-- 200 OK ------------------------|                            |
  |    (Body: access_token, role)     |                            |
  |    (Set-Cookie: HttpOnly refresh) |                            |
  |                                   |                            |
  |--- GET /products (Bearer token) ->|-- Decode JWT & check jti ->|
  |<-- 200 OK (Products list) --------|                            |
  |                                   |                            |
  |--- POST /auth/logout ------------>|-- Store JTIs in RevokedToken
  |<-- 200 OK (Cookie deleted) -------|-- Blacklisted tokens ----->|
```

### 2. Product & Inventory Management Flow
1. **Creation**: `POST /api/v1/products` validates category and supplier exist and ensures the SKU is unique.
2. **Stock Status Calculation**: Automatically evaluated on every query:
   - `quantity_in_stock == 0` → `"out of stock"`
   - `0 < quantity_in_stock <= reorder_level` → `"low stock"`
   - `quantity_in_stock > reorder_level` → `"in stock"`
3. **Stock Adjustments**: `PATCH /api/v1/products/{id}/stock` accepts operation `"IN"` (increases stock) or `"OUT"` (decreases stock). Prevents negative inventory and records operational reason.
4. **Summary & Metrics**: `GET /api/v1/products/summary` provides instant aggregated dashboard counts (total items, total inventory value in currency, low-stock count, and out-of-stock count).

### 3. Order Processing & Status State Machine
When a customer order is placed, the backend calculates totals and dynamically evaluates stock availability:
- If any requested product has `product.quantity_in_stock < requested_quantity`, initial status is `AWAITING_STOCK`.
- Otherwise, initial status is `CONFIRMED`.

#### State Machine Flowchart:
```text
           [ ORDER_PLACED ]
               /      \
              /        \
             ↓          ↓
       [ CONFIRMED ]  [ CANCELLED ]
          /     \
         ↓       ↓
 [ PROCESSING ] [ AWAITING_STOCK ]
       |     \          |
       |      \         ↓
       |       --> [ SUPPLIER_ORDER_PLACED ]
       |                |
       |                ↓
       |         [ STOCK_RECEIVED ]
       |                |
       |                ↓
       +---------> [ PACKED ]
                        |
                        ↓
                   [ SHIPPED ]
                        |
                        ↓
              [ OUT_FOR_DELIVERY ]
                        |
                        ↓
                  [ DELIVERED ]
```

### 4. Manager-Staff Task Delegation & ABAC Flow
1. Manager creates a task via `POST /api/v1/tasks/` specifying:
   - Title, description, priority (`LOW`, `MEDIUM`, `HIGH`), due date.
   - Assigned staff (`assigned_to_id`).
   - Scope: `target_type` (`PRODUCT`, `CATEGORY`, `SUPPLIER`, or `NONE`) and optional `target_id`.
2. The staff member logs in and queries `GET /api/v1/tasks/my` to retrieve assigned duties.
3. The staff member performs the operation (e.g., updating a product). The FastAPI dependency `ensure_record_access` validates that the staff member holds an active task targeting that specific product ID.
4. Once finished, the staff member updates the task status to `COMPLETED` via `PATCH /api/v1/tasks/{id}/status`.
5. Write access for that record automatically revokes.

### 5. Machine Learning Delivery Prediction Flow
1. An order is created or assessed for fulfillment.
2. The backend calls `POST /api/v1/predictions/delivery` supplying:
   - `order_quantity`, `number_of_items`, `current_stock`, `reorder_level`
   - `supplier_lead_time`, `processing_time`, `shipping_time`
3. The feature engineer computes `shortage_quantity = max(order_quantity - current_stock, 0)`.
4. The trained XGBoost model (`app/ml/models/delivery_model.pkl`) evaluates non-linear interactions to forecast total fulfillment days.
5. The predicted delivery timestamp is calculated: `order_date + timedelta(days=predicted_days)`.

---

## Complete API Endpoints Reference

### Base URL
- Local: `http://127.0.0.1:8000/api/v1`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

---

### 1. Authentication Endpoints (`/api/v1/auth`)

#### 1.1 Register User
- **Method**: `POST`
- **Path**: `/auth/register`
- **Auth Required**: None (Public)
- **Status Code**: `201 Created`
- **Request Body**:
```json
{
  "username": "ishika_dev",
  "email": "ishika@example.com",
  "password": "SecurePassword123!",
  "confirm_password": "SecurePassword123!"
}
```
- **Response (`201 Created`)**:
```json
{
  "id": "e0b5fa21-5a04-4c47-8a6f-31b32d2012a4",
  "username": "ishika_dev",
  "email": "ishika@example.com",
  "role": "SUPER_ADMIN"
}
```

#### 1.2 Login
- **Method**: `POST`
- **Path**: `/auth/login`
- **Auth Required**: None (Public)
- **Status Code**: `200 OK`
- **Sets Cookie**: `refresh_token=<token>; HttpOnly; Path=/api/v1/auth; Max-Age=604800`
- **Request Body**:
```json
{
  "email": "ishika@example.com",
  "password": "SecurePassword123!"
}
```
- **Response (`200 OK`)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "SUPER_ADMIN",
  "username": "ishika_dev"
}
```

#### 1.3 Refresh Access Token
- **Method**: `POST`
- **Path**: `/auth/refresh`
- **Auth Required**: Refresh token cookie
- **Request Headers / Cookies**:
```text
Cookie: refresh_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
- **Response (`200 OK`)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 1.4 Logout
- **Method**: `POST`
- **Path**: `/auth/logout`
- **Auth Required**: Bearer Access Token + Refresh Token Cookie
- **Request Headers**:
```text
Authorization: Bearer <access_token>
Cookie: refresh_token=<refresh_token>
```
- **Response (`200 OK`)**:
```json
{
  "message": "Logout successful"
}
```

---

### 2. Users & Team Management (`/api/v1/users`)

#### 2.1 List All Users (Paginated)
- **Method**: `GET`
- **Path**: `/users/?page=1&page_size=10`
- **Auth Required**: Bearer Token (`SUPER_ADMIN` only)
- **Query Parameters**:
  - `page` (int, default: 1, ge: 1)
  - `page_size` (int, default: 10, ge: 1, le: 100)
- **Response (`200 OK`)**:
```json
{
  "items": [
    {
      "id": "e0b5fa21-5a04-4c47-8a6f-31b32d2012a4",
      "username": "ishika_dev",
      "email": "ishika@example.com",
      "role": "SUPER_ADMIN"
    },
    {
      "id": "c328e63a-9c64-4cab-a9a1-100d9e07c0b0",
      "username": "john_inv_mgr",
      "email": "john@example.com",
      "role": "INVENTORY_MANAGER"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 2,
  "total_pages": 1
}
```

#### 2.2 List Managed Team Members (Paginated)
- **Method**: `GET`
- **Path**: `/users/team?page=1&page_size=10`
- **Auth Required**: Bearer Token (`INVENTORY_MANAGER` or `ORDER_MANAGER`)
- **Query Parameters**:
  - `page` (int, default: 1, ge: 1)
  - `page_size` (int, default: 10, ge: 1, le: 100)
- **Response (`200 OK`)**:
```json
{
  "items": [
    {
      "id": "f81f263a-76f8-44bf-a08c-be87f930fcd7",
      "username": "staff_member_1",
      "email": "staff1@example.com",
      "role": "INVENTORY_STAFF"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 1,
  "total_pages": 1
}
```

#### 2.3 Update User Role
- **Method**: `PATCH`
- **Path**: `/users/{user_id}/role`
- **Auth Required**: Bearer Token (`SUPER_ADMIN` only)
- **Request Body**:
```json
{
  "role": "INVENTORY_MANAGER"
}
```
- **Response (`200 OK`)**:
```json
{
  "id": "f81f263a-76f8-44bf-a08c-be87f930fcd7",
  "username": "staff_member_1",
  "email": "staff1@example.com",
  "role": "INVENTORY_MANAGER"
}
```

---

### 3. Categories (`/api/v1/categories`)

#### 3.1 Create Category
- **Method**: `POST`
- **Path**: `/categories/`
- **Auth Required**: Bearer Token (Unrestricted or Staff with `CATEGORY` creation task)
- **Request Body**:
```json
{
  "name": "Electronics",
  "description": "Smartphones, laptops, monitors and home appliances"
}
```
- **Response (`201 Created`)**:
```json
{
  "id": "533a15dd-5c2d-4037-81f4-de00b87e68a2",
  "name": "Electronics",
  "description": "Smartphones, laptops, monitors and home appliances",
  "created_at": "2026-09-23T14:30:00Z"
}
```

#### 3.2 List Categories (Paginated)
- **Method**: `GET`
- **Path**: `/categories/?page=1&page_size=10`
- **Auth Required**: Bearer Token
- **Query Parameters**:
  - `page` (int, default: 1, ge: 1)
  - `page_size` (int, default: 10, ge: 1, le: 100)
- **Response (`200 OK`)**:
```json
{
  "items": [
    {
      "id": "533a15dd-5c2d-4037-81f4-de00b87e68a2",
      "name": "Electronics",
      "description": "Smartphones, laptops, monitors and home appliances",
      "created_at": "2026-09-23T14:30:00Z"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 1,
  "total_pages": 1
}
```

#### 3.3 Get Category by ID
- **Method**: `GET`
- **Path**: `/categories/{category_id}`
- **Auth Required**: Bearer Token
- **Response (`200 OK`)**:
```json
{
  "id": "533a15dd-5c2d-4037-81f4-de00b87e68a2",
  "name": "Electronics",
  "description": "Smartphones, laptops, monitors and home appliances",
  "created_at": "2026-09-23T14:30:00Z"
}
```

#### 3.4 Update Category
- **Method**: `PUT`
- **Path**: `/categories/{category_id}`
- **Auth Required**: Bearer Token (Unrestricted or Staff with assigned task for this ID)
- **Request Body**:
```json
{
  "name": "Consumer Electronics",
  "description": "Updated category description"
}
```
- **Response (`200 OK`)**:
```json
{
  "id": "533a15dd-5c2d-4037-81f4-de00b87e68a2",
  "name": "Consumer Electronics",
  "description": "Updated category description",
  "created_at": "2026-09-23T14:30:00Z"
}
```

#### 3.5 Soft Delete Category
- **Method**: `DELETE`
- **Path**: `/categories/{category_id}`
- **Auth Required**: Bearer Token (Unrestricted or Staff with assigned task for this ID)
- **Response**: `204 No Content`

---

### 4. Suppliers (`/api/v1/suppliers`)

#### 4.1 Create Supplier
- **Method**: `POST`
- **Path**: `/suppliers/`
- **Auth Required**: Bearer Token (Unrestricted or Staff with `SUPPLIER` creation task)
- **Request Body**:
```json
{
  "name": "Samsung Logistics Corp",
  "contact_email": "orders@samsung-logistics.com",
  "phone": "9876543210",
  "address": "Building 5, Tech Innovation Park, Seoul"
}
```
- **Response (`201 Created`)**:
```json
{
  "id": "8ff19537-9752-4646-8a4f-bc947fed6ce0",
  "name": "Samsung Logistics Corp",
  "contact_email": "orders@samsung-logistics.com",
  "phone": "9876543210",
  "address": "Building 5, Tech Innovation Park, Seoul",
  "created_at": "2026-09-23T14:32:00Z"
}
```

#### 4.2 List Suppliers (Paginated)
- **Method**: `GET`
- **Path**: `/suppliers/?page=1&page_size=10`
- **Auth Required**: Bearer Token
- **Query Parameters**:
  - `page` (int, default: 1, ge: 1)
  - `page_size` (int, default: 10, ge: 1, le: 100)
- **Response (`200 OK`)**:
```json
{
  "items": [
    {
      "id": "8ff19537-9752-4646-8a4f-bc947fed6ce0",
      "name": "Samsung Logistics Corp",
      "contact_email": "orders@samsung-logistics.com",
      "phone": "9876543210",
      "address": "Building 5, Tech Innovation Park, Seoul",
      "created_at": "2026-09-23T14:32:00Z"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 1,
  "total_pages": 1
}
```

#### 4.3 Get Supplier by ID
- **Method**: `GET`
- **Path**: `/suppliers/{supplier_id}`
- **Auth Required**: Bearer Token
- **Response (`200 OK`)**: Same as single supplier representation.

#### 4.4 Update Supplier
- **Method**: `PUT`
- **Path**: `/suppliers/{supplier_id}`
- **Auth Required**: Bearer Token (Unrestricted or Staff with task for this ID)
- **Request Body**:
```json
{
  "name": "Samsung Global Suppliers",
  "contact_email": "b2b@samsung.com",
  "phone": "9876543210",
  "address": "Global HQ, Seoul"
}
```
- **Response (`200 OK`)**: Updated supplier object.

#### 4.5 Soft Delete Supplier
- **Method**: `DELETE`
- **Path**: `/suppliers/{supplier_id}`
- **Auth Required**: Bearer Token (Unrestricted or Staff with task for this ID)
- **Response**: `204 No Content`

---

### 5. Products (`/api/v1/products`)

#### 5.1 Create Product
- **Method**: `POST`
- **Path**: `/products/`
- **Auth Required**: Bearer Token (Unrestricted or Staff with `PRODUCT` creation task)
- **Request Body**:
```json
{
  "name": "Galaxy Ultra Book 4",
  "sku": "SAM-GUB4-001",
  "category_id": "533a15dd-5c2d-4037-81f4-de00b87e68a2",
  "supplier_id": "8ff19537-9752-4646-8a4f-bc947fed6ce0",
  "unit_price": 1299.99,
  "quantity_in_stock": 25,
  "reorder_level": 5
}
```
- **Response (`201 Created`)**:
```json
{
  "id": "733784bb-7a4b-45fa-a9c8-f23677d3a141",
  "name": "Galaxy Ultra Book 4",
  "sku": "SAM-GUB4-001",
  "category_id": "533a15dd-5c2d-4037-81f4-de00b87e68a2",
  "supplier_id": "8ff19537-9752-4646-8a4f-bc947fed6ce0",
  "unit_price": "1299.99",
  "quantity_in_stock": 25,
  "reorder_level": 5,
  "is_active": true,
  "stock_status": "in stock",
  "created_at": "2026-09-23T14:35:00Z",
  "updated_at": "2026-09-23T14:35:00Z"
}
```

#### 5.2 List Products (Paginated with Filters)
- **Method**: `GET`
- **Path**: `/products/?page=1&page_size=10&search=Galaxy&stock_status=in%20stock`
- **Auth Required**: Bearer Token
- **Query Parameters**:
  - `page` (int, default: 1, ge: 1)
  - `page_size` (int, default: 10, ge: 1, le: 100)
  - `search` (string, optional: matches name or sku via ILIKE)
  - `category_id` (UUID, optional)
  - `stock_status` (string, optional: `"in stock"` | `"low stock"` | `"out of stock"`)
- **Response (`200 OK`)**:
```json
{
  "items": [
    {
      "id": "733784bb-7a4b-45fa-a9c8-f23677d3a141",
      "name": "Galaxy Ultra Book 4",
      "sku": "SAM-GUB4-001",
      "category_id": "533a15dd-5c2d-4037-81f4-de00b87e68a2",
      "supplier_id": "8ff19537-9752-4646-8a4f-bc947fed6ce0",
      "unit_price": "1299.99",
      "quantity_in_stock": 25,
      "reorder_level": 5,
      "is_active": true,
      "stock_status": "in stock",
      "created_at": "2026-09-23T14:35:00Z",
      "updated_at": "2026-09-23T14:35:00Z"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 1,
  "total_pages": 1
}
```

#### 5.3 Product Inventory Summary Dashboard
- **Method**: `GET`
- **Path**: `/products/summary`
- **Auth Required**: Bearer Token
- **Response (`200 OK`)**:
```json
{
  "total_products": 42,
  "total_stock_value": "158420.50",
  "low_stock_count": 4,
  "out_of_stock_count": 2
}
```

#### 5.4 Get Product by ID
- **Method**: `GET`
- **Path**: `/products/{product_id}`
- **Auth Required**: Bearer Token
- **Response (`200 OK`)**: Product details with current `stock_status`.

#### 5.5 Update Product
- **Method**: `PUT`
- **Path**: `/products/{product_id}`
- **Auth Required**: Bearer Token (Unrestricted or Staff with task for this product)
- **Request Body**:
```json
{
  "name": "Galaxy Ultra Book 4 Pro",
  "unit_price": 1399.99,
  "reorder_level": 8
}
```
- **Response (`200 OK`)**: Updated product response.

#### 5.6 Adjust Stock (Stock In / Stock Out)
- **Method**: `PATCH`
- **Path**: `/products/{product_id}/stock`
- **Auth Required**: Bearer Token (Unrestricted or Staff with task for this product)
- **Request Body**:
```json
{
  "quantity": 10,
  "operation": "IN",
  "reason": "Restocked from purchase order PO-2026-09-001"
}
```
*(Use `"operation": "OUT"` to deduct items; checks that remaining stock does not drop below 0).*
- **Response (`200 OK`)**: Updated product response with refreshed `quantity_in_stock` and `stock_status`.

#### 5.7 Soft Delete Product
- **Method**: `DELETE`
- **Path**: `/products/{product_id}`
- **Auth Required**: Bearer Token (Unrestricted or Staff with task for this product)
- **Response**: `204 No Content` (Sets `is_active = False`).

---

### 6. Customers (`/api/v1/customers`)

#### 6.1 Create Customer
- **Method**: `POST`
- **Path**: `/customers/`
- **Auth Required**: None (or authenticated per frontend flow)
- **Request Body**:
```json
{
  "name": "Sarah Connor",
  "email": "sarah.connor@example.com",
  "phone": "+1-555-0199",
  "address": "42 Cyberdyne Way, Los Angeles, CA"
}
```
- **Response (`201 Created`)**:
```json
{
  "id": "18c8e11a-0db5-48b2-8419-f521b44d2162",
  "name": "Sarah Connor",
  "email": "sarah.connor@example.com",
  "phone": "+1-555-0199",
  "address": "42 Cyberdyne Way, Los Angeles, CA",
  "created_at": "2026-09-23T14:40:00Z",
  "updated_at": "2026-09-23T14:40:00Z"
}
```

#### 6.2 List Customers (Paginated)
- **Method**: `GET`
- **Path**: `/customers/?page=1&page_size=10`
- **Query Parameters**:
  - `page` (int, default: 1, ge: 1)
  - `page_size` (int, default: 10, ge: 1, le: 100)
- **Response (`200 OK`)**:
```json
{
  "items": [
    {
      "id": "18c8e11a-0db5-48b2-8419-f521b44d2162",
      "name": "Sarah Connor",
      "email": "sarah.connor@example.com",
      "phone": "+1-555-0199",
      "address": "42 Cyberdyne Way, Los Angeles, CA",
      "created_at": "2026-09-23T14:40:00Z",
      "updated_at": "2026-09-23T14:40:00Z"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 1,
  "total_pages": 1
}
```

#### 6.3 Get Customer by ID
- **Method**: `GET`
- **Path**: `/customers/{customer_id}`
- **Response (`200 OK`)**: Single customer details.

#### 6.4 Update Customer
- **Method**: `PUT`
- **Path**: `/customers/{customer_id}`
- **Request Body**:
```json
{
  "phone": "+1-555-9988",
  "address": "742 Evergreen Terrace, Springfield"
}
```
- **Response (`200 OK`)**: Updated customer object.

---

### 7. Orders (`/api/v1/orders`)

#### 7.1 Create Order
- **Method**: `POST`
- **Path**: `/orders/`
- **Auth Required**: Open / Authenticated
- **Request Body**:
```json
{
  "customer_id": "18c8e11a-0db5-48b2-8419-f521b44d2162",
  "items": [
    {
      "product_id": "733784bb-7a4b-45fa-a9c8-f23677d3a141",
      "quantity": 2
    }
  ]
}
```
- **Response (`201 Created`)**:
```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "customer_id": "18c8e11a-0db5-48b2-8419-f521b44d2162",
  "order_date": "2026-09-23T14:45:00Z",
  "status": "CONFIRMED",
  "total_amount": "2599.98",
  "predicted_delivery_date": null,
  "actual_delivery_date": null,
  "items": [
    {
      "id": "3146d6b8-20cf-46d9-813f-14f762294101",
      "product_id": "733784bb-7a4b-45fa-a9c8-f23677d3a141",
      "quantity": 2,
      "unit_price": "1299.99",
      "subtotal": "2599.98"
    }
  ],
  "created_at": "2026-09-23T14:45:00Z",
  "updated_at": "2026-09-23T14:45:00Z"
}
```
*(If warehouse stock for any ordered item is lower than requested quantity, order status is automatically set to `"AWAITING_STOCK"`, and the system instantly dispatches a high-priority `"Restock Required: <Product Name> (Shortage: <Qty>)"` task assigned directly to the `INVENTORY_MANAGER` with product scope).*


#### 7.2 List Orders (Paginated)
- **Method**: `GET`
- **Path**: `/orders/?page=1&page_size=10`
- **Query Parameters**:
  - `page` (int, default: 1, ge: 1)
  - `page_size` (int, default: 10, ge: 1, le: 100)
- **Response (`200 OK`)**:
```json
{
  "items": [
    {
      "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "customer_id": "18c8e11a-0db5-48b2-8419-f521b44d2162",
      "order_date": "2026-09-23T14:45:00Z",
      "status": "CONFIRMED",
      "total_amount": "2599.98",
      "predicted_delivery_date": null,
      "actual_delivery_date": null,
      "items": [
        {
          "id": "3146d6b8-20cf-46d9-813f-14f762294101",
          "product_id": "733784bb-7a4b-45fa-a9c8-f23677d3a141",
          "quantity": 2,
          "unit_price": "1299.99",
          "subtotal": "2599.98"
        }
      ],
      "created_at": "2026-09-23T14:45:00Z",
      "updated_at": "2026-09-23T14:45:00Z"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 1,
  "total_pages": 1
}
```

#### 7.3 Get Order by ID
- **Method**: `GET`
- **Path**: `/orders/{order_id}`
- **Response (`200 OK`)**: Single order details with items and subtotal breakdown.

#### 7.4 Update Order Status
- **Method**: `PATCH`
- **Path**: `/orders/{order_id}/status`
- **Request Body**:
```json
{
  "status": "PROCESSING"
}
```
- **Response (`200 OK`)**: Updated order object.
- **Enforced Transitions**: Attempting invalid state transitions (e.g. `ORDER_PLACED` directly to `DELIVERED`) throws `400 Bad Request`.

---

### 8. Task Management (`/api/v1/tasks`)

#### 8.1 Create Task
- **Method**: `POST`
- **Path**: `/tasks/`
- **Auth Required**: Bearer Token (`SUPER_ADMIN`, `INVENTORY_MANAGER`, `ORDER_MANAGER`)
- **Request Body**:
```json
{
  "title": "Audit Laptop Inventory & Reorder",
  "description": "Verify physical count of Galaxy laptops and update the database accordingly.",
  "priority": "HIGH",
  "due_date": "2026-09-26T18:00:00Z",
  "assigned_to_id": "f81f263a-76f8-44bf-a08c-be87f930fcd7",
  "target_type": "PRODUCT",
  "target_id": "733784bb-7a4b-45fa-a9c8-f23677d3a141"
}
```
- **Response (`201 Created`)**:
```json
{
  "id": "c1a2e3f4-5678-90ab-cdef-1234567890ab",
  "title": "Audit Laptop Inventory & Reorder",
  "description": "Verify physical count of Galaxy laptops and update the database accordingly.",
  "priority": "HIGH",
  "status": "PENDING",
  "due_date": "2026-09-26T18:00:00Z",
  "assigned_to_id": "f81f263a-76f8-44bf-a08c-be87f930fcd7",
  "assigned_by_id": "c328e63a-9c64-4cab-a9a1-100d9e07c0b0",
  "target_type": "PRODUCT",
  "target_id": "733784bb-7a4b-45fa-a9c8-f23677d3a141",
  "created_at": "2026-09-23T14:50:00Z",
  "updated_at": "2026-09-23T14:50:00Z"
}
```

#### 8.2 List Tasks (Manager / Super Admin - Paginated)
- **Method**: `GET`
- **Path**: `/tasks/?page=1&page_size=10`
- **Auth Required**: Bearer Token (`SUPER_ADMIN` sees all; managers see tasks they initiated).
- **Query Parameters**:
  - `page` (int, default: 1, ge: 1)
  - `page_size` (int, default: 10, ge: 1, le: 100)
- **Response (`200 OK`)**:
```json
{
  "items": [
    {
      "id": "c1a2e3f4-5678-90ab-cdef-1234567890ab",
      "title": "Audit Laptop Inventory & Reorder",
      "priority": "HIGH",
      "status": "PENDING",
      "assigned_to_id": "f81f263a-76f8-44bf-a08c-be87f930fcd7",
      "assigned_by_id": "c328e63a-9c64-4cab-a9a1-100d9e07c0b0",
      "target_type": "PRODUCT",
      "target_id": "733784bb-7a4b-45fa-a9c8-f23677d3a141",
      "created_at": "2026-09-23T14:50:00Z",
      "updated_at": "2026-09-23T14:50:00Z"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 1,
  "total_pages": 1
}
```

#### 8.3 Get Current User's Tasks (Paginated)
- **Method**: `GET`
- **Path**: `/tasks/my?page=1&page_size=10`
- **Auth Required**: Bearer Token (Any authenticated role; returns tasks where `assigned_to_id == current_user.id`).
- **Query Parameters**:
  - `page` (int, default: 1, ge: 1)
  - `page_size` (int, default: 10, ge: 1, le: 100)
- **Response (`200 OK`)**: Same paginated structure as list tasks.

#### 8.4 Get Task Details
- **Method**: `GET`
- **Path**: `/tasks/{task_id}`
- **Auth Required**: Bearer Token (Creator, Assignee, or Super Admin).
- **Response (`200 OK`)**: Task details.

#### 8.5 Update Task Status (Staff / Assignee)
- **Method**: `PATCH`
- **Path**: `/tasks/{task_id}/status`
- **Auth Required**: Bearer Token (Assignee, Creator, or Super Admin).
- **Request Body**:
```json
{
  "status": "COMPLETED"
}
```
*(Allowed statuses: `"PENDING"`, `"IN_PROGRESS"`, `"COMPLETED"`).*
- **Response (`200 OK`)**: Updated task response.

#### 8.6 Full Task Update (Manager Only)
- **Method**: `PUT`
- **Path**: `/tasks/{task_id}`
- **Auth Required**: Bearer Token (Task Creator or Super Admin).
- **Request Body**:
```json
{
  "title": "Updated Title",
  "priority": "MEDIUM",
  "due_date": "2026-09-30T12:00:00Z"
}
```
- **Response (`200 OK`)**: Updated task object.

#### 8.7 Delete Task
- **Method**: `DELETE`
- **Path**: `/tasks/{task_id}`
- **Auth Required**: Bearer Token (Task Creator or Super Admin).
- **Response**: `204 No Content`

---

### 9. Delivery Prediction (`/api/v1/predictions`)

#### 9.1 Predict Delivery by Order ID (Automated Database Feature Extraction)
- **Method**: `POST`
- **Path**: `/predictions/orders/{order_id}`
- **Auth Required**: None / Public
- **Description**: Automatically pulls the order, line item quantities, and real-time inventory stock from the database, feeds all 9 features into the XGBoost ML model, updates `order.predicted_delivery_date` in PostgreSQL, and returns the forecast.
- **Path Parameters**:
  - `order_id` (UUID, required): Target order identifier.
- **Example Request**:
```http
POST /api/v1/predictions/orders/f47ac10b-58cc-4372-a567-0e02b2c3d479
```
- **Response (`200 OK`)**:
```json
{
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "predicted_fulfillment_days": 5.18,
  "predicted_delivery_date": "2026-09-28T14:32:00Z",
  "model_version": "xgboost-v2",
  "training_data_type": "dummy_historical_csv"
}
```

#### 9.2 Predict Order Delivery Days (Manual Feature Inputs)
- **Method**: `POST`
- **Path**: `/predictions/delivery`
- **Auth Required**: None / Public
- **Query Parameters**:
  - `order_id` (UUID): Identifier of the target order.
  - `order_date` (ISO datetime): Date when order was placed.
  - `order_quantity` (int): Total units ordered.
  - `number_of_items` (int): Distinct items in order.
  - `current_stock` (int): Available inventory in warehouse.
  - `reorder_level` (int): Product threshold for restocking.
  - `supplier_lead_time` (int, days): Supplier replenishment lead time.
  - `processing_time` (int, days): Internal picking/packing duration.
  - `shipping_time` (int, days): Carrier transit duration.

- **Example Request URL**:
```text
POST /api/v1/predictions/delivery?order_id=f47ac10b-58cc-4372-a567-0e02b2c3d479&order_date=2026-09-23T10%3A00%3A00Z&order_quantity=50&number_of_items=3&current_stock=20&reorder_level=10&supplier_lead_time=5&processing_time=1&shipping_time=2
```

- **Response (`200 OK`)**:
```json
{
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "predicted_fulfillment_days": 7.42,
  "predicted_delivery_date": "2026-09-30T20:04:48Z",
  "model_version": "xgboost-v2",
  "training_data_type": "dummy_historical_csv"
}
```

---

## Setup, Execution & Database Migrations

### 1. Environment Configuration
Create a `.env` file in the root backend directory:
```env
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/inventory_db
SECRET_KEY=super_secret_jwt_signing_key_at_least_32_characters_long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=5
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 2. Dependency Installation
```bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Database Migrations (Alembic)
Run migrations to generate all tables, foreign keys, and indexes:
```bash
alembic upgrade head
```

### 4. Running the Application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Training the Delivery Prediction Machine Learning Model
To retrain or rebuild `app/ml/models/delivery_model.pkl`:
```bash
python -m app.ml.train
```
*(Evaluates MAE, RMSE, R² score, and saves the binary model bundle).*
