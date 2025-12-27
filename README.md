# AI Tool Finder Backend

## Instructions to Run the Application

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Backend_project_Team1
   ```

2. Install dependencies:
   ```bash
   pip install -r requirement.txt
   ```

3. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

4. Access the API documentation at:
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

## API Examples

### Fetch All Tools
**GET** `/tools`

Query Parameters:
- `category` (optional): Filter by category.
- `min_rating` (optional): Minimum average rating.
- `pricing_type` (optional): Filter by pricing type.

Example:
```bash
curl "http://127.0.0.1:8000/tools?category=NLP&min_rating=4&pricing_type=FREE"
```

### Submit a Review
**POST** `/review`

Payload:
```json
{
  "tool_id": "tool-uuid",
  "user_rating": 5,
  "comment": "Great tool!"
}
```

### Approve a Review
**PATCH** `/approve_review/{review_id}`

Payload:
```json
{
  "approval_status": "APPROVED"
}
```

---

Only tools matching **all conditions** are returned.

---

### 3️⃣ Review & Rating System
- Users can submit reviews with a rating (1–5 stars) and optional comments
- Reviews are stored separately from tools
- Ratings are **automatically recalculated** based on approved reviews only
- This ensures fair and accurate tool rankings

---

### 4️⃣ Admin Moderation
Admins have full control over platform content:
- Add, edit, and delete AI tools
- Approve or reject user reviews
- Control which reviews affect tool ratings

Admin APIs are clearly separated from user APIs to maintain security and structure.

---

## 🔌 API-Driven Architecture

The project exposes RESTful APIs including:
- Fetch all AI tools
- Filter tools using query parameters
- Submit user reviews
- Admin endpoints for tool and review management

The system emphasizes **clean architecture**, **separation of concerns**, and **scalable design**.

---

## 🎯 Learning Outcomes

This project demonstrates:
- Real-world backend API design
- Database modeling and relationships
- Derived data computation (average ratings)
- Role-based access (user vs admin)
- Production-style filtering logic

---

## 🚀 Use Case

The AI Tool Finder can serve as:
- A learning project for backend engineering
- A foundation for a full-stack AI discovery platform
- A demonstration of REST API best practices

---

💡 **Note:** This project focuses entirely on backend functionality. No frontend or UI components are included.
