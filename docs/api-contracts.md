# Supply Chain Management - REST API Contracts
## 1. Authentication
### 1.1 Register User

Method: POST

Endpoint:
/api/auth/register

Purpose:
Create a new user account.

Authentication:
Not required

Request Body:
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}

Success Response:
201 Created


### 1.2 Login User

Method: POST

Endpoint:
/api/auth/login

Purpose:
Authenticate a user and return an access token.

Authentication:
Not required

Request Body:
{
  "email": "user@example.com",
  "password": "password123"
}

Success Response:
200 OK


### 1.3 Get Current User

Method: GET

Endpoint:
/api/auth/me

Purpose:
Return the currently authenticated user's profile and role.

Authentication:
Required

Request Body:
None

Success Response:
200 OK


### 1.4 Logout User

Method: POST

Endpoint:
/api/auth/logout

Purpose:
Log out the currently authenticated user.

Authentication:
Required

Request Body:
None

Success Response:
204 No Content

## 2. Products
### 2.1 Get All Products

Method: GET

Endpoint:
/api/products

Purpose:
Get all products.

Authentication:
Required

Request Body:
None

Success Response:
200 OK


### 2.2 Get Product by ID

Method: GET

Endpoint:
/api/products/{product_id}

Purpose:
Get details of a specific product.

Authentication:
Required

Path Parameter:
product_id

Request Body:
None

Success Response:
200 OK


### 2.3 Create Product

Method: POST

Endpoint:
/api/products

Purpose:
Create a new product.

Authentication:
Required

Allowed Roles:
admin

Request Body:
{
  "sku": "MILK-001",
  "name": "Milk",
  "description": "Fresh milk product",
  "category": "Dairy",
  "unit": "litre",
  "reorder_level": 100
}

Success Response:
201 Created


### 2.4 Update Product

Method: PATCH

Endpoint:
/api/products/{product_id}

Purpose:
Update an existing product.

Authentication:
Required

Allowed Roles:
admin

Path Parameter:
product_id

Request Body:
{
  "name": "Updated Milk",
  "reorder_level": 150
}

Success Response:
200 OK


### 2.5 Delete Product

Method: DELETE

Endpoint:
/api/products/{product_id}

Purpose:
Delete a product.

Authentication:
Required

Allowed Roles:
admin

Path Parameter:
product_id

Request Body:
None

Success Response:
204 No Content

## 3. Suppliers
### 3.1 Get All Suppliers

Method: GET

Endpoint:
/api/suppliers

Purpose:
Get all suppliers.

Authentication:
Required

Request Body:
None

Success Response:
200 OK


### 3.2 Get Supplier by ID

Method: GET

Endpoint:
/api/suppliers/{supplier_id}

Purpose:
Get details of a specific supplier.

Authentication:
Required

Path Parameter:
supplier_id

Request Body:
None

Success Response:
200 OK


### 3.3 Create Supplier

Method: POST

Endpoint:
/api/suppliers

Purpose:
Create a new supplier.

Authentication:
Required

Allowed Roles:
admin
procurement

Request Body:
{
  "supplier_code": "SUP-001",
  "name": "Supplier A",
  "contact_person": "John",
  "email": "supplier@example.com",
  "phone": "9876543210",
  "address": "Coimbatore",
  "city": "Coimbatore",
  "country": "India"
}

Success Response:
201 Created


### 3.4 Update Supplier

Method: PATCH

Endpoint:
/api/suppliers/{supplier_id}

Purpose:
Update an existing supplier.

Authentication:
Required

Allowed Roles:
admin
procurement

Path Parameter:
supplier_id

Request Body:
{
  "name": "Updated Supplier A",
  "phone": "9876500000",
  "status": "active"
}

Success Response:
200 OK


### 3.5 Delete Supplier

Method: DELETE

Endpoint:
/api/suppliers/{supplier_id}

Purpose:
Delete or deactivate a supplier.

Authentication:
Required

Allowed Roles:
admin
procurement

Path Parameter:
supplier_id

Request Body:
None

Success Response:
204 No Content
## 4. Inventory


## 5. Purchase Orders

## 6. Production Orders

## 7. Shipments

## 8. Events

## 9. Alerts

## 10. Risks

## 11. Recommendations

# Common API Rules

## Base URL

/api

## Authentication

Protected APIs require a valid Supabase authentication token.

## Standard HTTP Methods

GET    - Read data
POST   - Create data
PATCH  - Update data
DELETE - Delete data

## Standard Success Status Codes

200 OK
201 Created
204 No Content

## Standard Error Status Codes

400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Unprocessable Entity
500 Internal Server Error

## API Module Structure

### Authentication
/api/auth

### Products
/api/products

### Suppliers
/api/suppliers

### Inventory
/api/inventory

### Purchase Orders
/api/purchase-orders

### Production Orders
/api/production-orders

### Shipments
/api/shipments

### Events
/api/events

### Alerts
/api/alerts

### Risks
/api/risks

### Recommendations
/api/recommendations