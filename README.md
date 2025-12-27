# AI Tool Finder - Backend Documentation

## Project Overview
**AI Tool Finder** is a robust backend platform for discovering, filtering, and reviewing AI tools. It is designed to simulate a real-world backend system focusing on data integrity, API design, advanced filtering, rating computation, and admin moderation. The platform supports multi-condition queries, ensures accurate aggregation of ratings, and provides a clear separation between user and admin functionalities.

---

## Core Data Models

### AI Tool
Represents an AI tool in the platform.

| Field         | Type    | Description |
|---------------|---------|-------------|
| `tool_id`     | string  | Unique identifier for the tool |
| `tool_name`   | string  | Name of the AI tool |
| `use_case`    | string  | Purpose, e.g., Text Summarization, Code Assistance, Image Generation |
| `category`    | string  | Domain category, e.g., NLP, Computer Vision, Productivity, Dev Tools |
| `pricing_type`| string  | Pricing model: `FREE`, `PAID`, `SUBSCRIPTION` |
| `avg_rating`  | float   | Average rating calculated from approved reviews (1–5 stars) |
| `created_at`  | datetime| Timestamp of creation |
| `updated_at`  | datetime| Timestamp of last update |

**Constraints:**
- `tool_name` must be unique.
- `avg_rating` is a derived field, auto-calculated from approved reviews.

---

### Review
Represents a user review for an AI tool.

| Field             | Type    | Description |
|------------------|---------|-------------|
| `review_id`      | string  | Unique identifier for the review |
| `tool_id`        | string  | Foreign key to AI Tool |
| `user_id`        | string  | Identifier of the user submitting the review |
| `user_rating`    | int     | Rating from 1 to 5 |
| `comment`        | string  | Optional text feedback |
| `approval_status`| string  | `PENDING`, `APPROVED`, `REJECTED` |
| `created_at`     | datetime| Timestamp of submission |
| `updated_at`     | datetime| Timestamp of last status change |

**Rules:**
- Only `APPROVED` reviews contribute to `avg_rating`.
- Reviews start with `PENDING` status and require admin moderation.

---

### User
Represents a user in the system.

| Field       | Type    | Description |
|------------|---------|-------------|
| `user_id`  | string  | Unique identifier |
| `username` | string  | Unique username |
| `email`    | string  | Unique email |
| `first_name`| string | First name |
| `last_name` | string | Last name |
| `role`     | string  | `USER` or `ADMIN` |
| `password` | string  | Hashed password |
| `created_at`| datetime| Account creation timestamp |

---

## API Endpoints

### Public APIs

#### GET `/tools`
Fetch all AI tools.

**Query Parameters for Filtering:**
- `category` – Partial, case-insensitive match
- `pricing_type` – `FREE | PAID | SUBSCRIPTION`
- `min_rating` – Minimum average rating (0–5, 0.5 increments)

**Example Request:**
```
/tools?category=NLP&pricing_type=FREE&min_rating=4
```

**Response:**
```json
[
  {
    "tool_id": "123",
    "tool_name": "AI Writer",
    "use_case": "Text Generation",
    "category": "NLP",
    "pricing_type": "FREE",
    "avg_rating": 4.5
  }
]
```

---

#### POST `/review`
Submit a review for a tool. Reviews are initially `PENDING`.

**Request Body:**
```json
{
  "tool_id": "123",
  "user_rating": 5,
  "comment": "Highly useful for summarizing text!"
}
```

**Response:**
```json
{
  "review_id": "456",
  "status": "PENDING"
}
```

**Behavior:**
- Stores the review separately.
- Does not affect `avg_rating` until approved.
- Admins can later approve or reject reviews.

---

### Admin APIs

#### POST `/admin/add-tool`
Add a new AI tool.

**Request Body:**
```json
{
  "tool_name": "AI Writer Pro",
  "use_case": "Text Summarization",
  "category": "NLP",
  "pricing_type": "PAID"
}
```

**Response:** Returns created tool with `tool_id`.

---

#### PUT `/admin/Update_tool/{tool_id}`
Update an existing AI tool.

**Request Body:**
```json
{
  "tool_name": "AI Writer Pro Updated",
  "use_case": "Text Summarization",
  "category": "NLP",
  "pricing_type": "SUBSCRIPTION"
}
```

**Response:** Updated tool object.

---

#### DELETE `/admin/delete_tool/{tool_id}`
Delete a tool by ID.  
**Response:** `204 No Content` if successful.

---

#### PATCH `/admin/approve_review/{review_id}`
Approve a review. Updates the tool’s `avg_rating`.

**Response:**
```json
{
  "review_id": "456",
  "status": "APPROVED",
  "new_avg_rating": 4.6
}
```

---

#### PATCH `/admin/reject_review/{review_id}`
Reject a review. Does not affect `avg_rating`.

---

## Rating & Review Computation
- **Step 1:** Store review as `PENDING`.
- **Step 2:** Admin approves review.
- **Step 3:** Recalculate `avg_rating`:
```text
avg_rating = SUM(approved_ratings) / COUNT(approved_reviews)
```
- **Step 4:** Update tool record.

**Edge Cases:**
- No approved reviews → `avg_rating = 0`.
- Updating/deleting a review triggers recalculation.

---

## Filtering Logic
- Supports multi-condition filtering.
- Partial matches supported for categories.
- Ratings filter works on `avg_rating` only (computed from approved reviews).
- Pricing filter is exact match.

**Example Combined Filters:**
```
/tools?category=Computer%20Vision&min_rating=4.5&pricing_type=SUBSCRIPTION
```

---

## Security & Access Control
- Users must authenticate to submit reviews.
- Admin endpoints require JWT with `role=ADMIN`.
- Passwords are hashed before storing.
- JWT tokens are used for authorization in all protected routes.

---

## Example Schemas

### AI Tool Schema
```json
{
  "tool_id": "string",
  "tool_name": "string",
  "use_case": "string",
  "category": "string",
  "pricing_type": "FREE",
  "avg_rating": 0
}
```

### Review Schema
```json
{
  "review_id": "string",
  "tool_id": "string",
  "user_rating": 0,
  "comment": "string",
  "status": "PENDING"
}
```

### User Schema
```json
{
  "user_id": "string",
  "username": "string",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "role": "USER",
  "password": "hashed_string"
}
```

### Token Schema
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

---

## Advanced Features & Best Practices
1. **Derived Fields:** `avg_rating` is computed, not stored directly by user input.  
2. **Separation of Roles:** Clear distinction between user and admin endpoints.  
3. **Atomic Operations:** Rating updates occur atomically to prevent inconsistencies.  
4. **Filtering Performance:** Indexing on `category`, `pricing_type`, and `avg_rating` recommended for large datasets.  
5. **Data Validation:** All inputs are validated; invalid requests return `422` with detailed error.  
6. **Extensibility:** Additional filters, pagination, or sorting can be added without modifying core logic.

---
# AI Tool Finder - Team Contributions

## Team Members and Responsibilities

| Area of Work                          | Team Members                                  | Responsibilities |
|--------------------------------------|-----------------------------------------------|-----------------|
| **Authentication & Authorization**    | Hem Kishore Pradhan & Arya Aditanshu Behera  | - Implement user registration and login <br> - Secure password hashing <br> - JWT-based access control for users and admins |
| **API Design / Routes**               | Hemanthbugata & Raghul Jayaraj               | - Define API `POST()`, `PUT()`, `PATCH()`, and `DELETE()` endpoints for users and admins <br> - Design request/response schemas <br> - Ensure RESTful API standards and consistency |
| **Database Modeling / DB Design / API** | Ravee Raghul C & Amal Falah                  | - Design database schema for AI tools, reviews, and users <br> - Implement relationships and constraints <br> - Optimize for filtering and rating computation <br> - Define API `GET()` endpoints. |
