Flask JWT API with MongoDB and Redis

This is a scalable RESTful API built with Flask, MongoDB, and Redis. It features JWT authentication, caching, rate limiting, and Swagger API documentation.

---

Features:

- User registration and login with JWT authentication
- MongoDB database for data persistence
- Redis caching and session management
- Rate limiting to prevent abuse
- API documentation with Swagger UI
- Password hashing with Bcrypt

---

Requirements:

- Docker & Docker Compose (optional, for containerized setup)
- Python 3.13+
- MongoDB (local or remote)
- Redis (local or remote)

---

Setup and Run Locally:

1. Clone the repository:
   git clone <your-repo-url>
   cd <your-repo-folder>

2. Create and activate a virtual environment:
   python3 -m venv venv
   source venv/bin/activate  (Linux/Mac)
   venv\Scripts\activate     (Windows)

3. Install dependencies:
   pip install -r requirements.txt

4. Set environment variables (create a .env file):
   MONGO_URI=mongodb://localhost:27017/flask_api
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=your_secret_key
   JWT_SECRET_KEY=your_jwt_secret_key
   API_BASE_URL=http://localhost:8080

5. Run the Flask app:
   flask run --host=0.0.0.0 --port=8080

6. Access API docs at:
   http://localhost:8080/

---

Using Docker Compose:

To run the app with MongoDB and Redis using Docker Compose:
   docker-compose up --build

---

API Endpoints:

- POST /auth/register - Register a new user
- POST /auth/login    - User login
- POST /auth/refresh  - Refresh JWT token
- GET  /protected    - Protected route example (requires JWT)

---

License:

This project is licensed under the MIT License - see the LICENSE file for details.

MIT License

---

Author:

thoeurn ratha - thoeurn.ratha.kh@gmail.com
