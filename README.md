# TeamHub - Collaborative Project Management Platform

A full-stack team collaboration platform built with Vue.js and FastAPI, featuring workspaces, projects, Kanban boards, and document management.

![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D?style=flat&logo=vue.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791?style=flat&logo=postgresql)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.x-38B2AC?style=flat&logo=tailwind-css)

## ✨ Features

- **User Authentication** - Secure JWT-based registration and login
- **Workspaces** - Create and manage team workspaces with member roles
- **Projects** - Organize work into projects within workspaces
- **Kanban Board** - Drag-and-drop task management with status columns (To Do, In Progress, Review, Done)
- **Task Management** - Create, edit, delete tasks with priority levels and assignments
- **Documents** - Create and edit project documentation
- **Dashboard** - Overview of all workspaces, projects, and task statistics
- **Responsive Design** - Works on desktop and mobile devices

## 🖼️ Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Kanban Board
![Kanban Board](screenshots/kanban.png)

### Workspaces
![Workspaces](screenshots/workspaces.png)

## 🛠️ Tech Stack

### Frontend
- **Vue.js 3** - Progressive JavaScript framework with Composition API
- **Vite** - Next-generation frontend build tool
- **Vue Router** - Client-side routing
- **Pinia** - State management
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API requests

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Relational database
- **JWT** - JSON Web Tokens for authentication
- **Pydantic** - Data validation
- **Bcrypt** - Password hashing

## 📁 Project Structure

```
team-hub/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/        # API endpoints
│   │   │   └── deps.py        # Dependencies
│   │   ├── core/
│   │   │   ├── config.py      # Configuration
│   │   │   └── security.py    # Auth utilities
│   │   ├── db/
│   │   │   └── database.py    # Database connection
│   │   ├── models/            # SQLAlchemy models
│   │   └── schemas/           # Pydantic schemas
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── views/             # Page components
│   │   ├── stores/            # Pinia stores
│   │   ├── services/          # API services
│   │   ├── router/            # Vue Router config
│   │   └── App.vue
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## 🗄️ Database Schema

```
users
├── id, email, password_hash, display_name, avatar_url, role, created_at

workspaces
├── id, name, description, owner_id, created_at

workspace_members
├── id, workspace_id, user_id, role, joined_at

projects
├── id, workspace_id, name, description, created_at

tasks
├── id, project_id, title, description, status, priority
├── assignee_id, created_by, due_date, position, created_at

comments
├── id, task_id, user_id, content, created_at

documents
├── id, project_id, title, content, created_by, created_at
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Git

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create PostgreSQL database**
   ```sql
   CREATE DATABASE team_hub;
   ```

5. **Configure environment variables**
   
   Create a `.env` file in the backend directory:
   ```env
   DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/team_hub
   SECRET_KEY=your-super-secret-key-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

6. **Create database tables**
   ```bash
   python -c "from app.db.database import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine)"
   ```

7. **Start the backend server**
   ```bash
   uvicorn main:app --reload
   ```
   
   Backend will be running at `http://localhost:8000`
   
   API documentation available at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```
   
   Frontend will be running at `http://localhost:5173`

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login user |
| GET | `/api/auth/me` | Get current user |

### Workspaces
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/workspaces/` | List all workspaces |
| POST | `/api/workspaces/` | Create workspace |
| GET | `/api/workspaces/{id}` | Get workspace details |
| PATCH | `/api/workspaces/{id}` | Update workspace |
| DELETE | `/api/workspaces/{id}` | Delete workspace |

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects/` | List projects |
| POST | `/api/projects/` | Create project |
| GET | `/api/projects/{id}` | Get project |
| PATCH | `/api/projects/{id}` | Update project |
| DELETE | `/api/projects/{id}` | Delete project |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks/` | List tasks |
| POST | `/api/tasks/` | Create task |
| GET | `/api/tasks/{id}` | Get task |
| PATCH | `/api/tasks/{id}` | Update task |
| PATCH | `/api/tasks/{id}/position` | Update task position (drag-drop) |
| DELETE | `/api/tasks/{id}` | Delete task |

### Documents
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/documents/` | List documents |
| POST | `/api/documents/` | Create document |
| GET | `/api/documents/{id}` | Get document |
| PATCH | `/api/documents/{id}` | Update document |
| DELETE | `/api/documents/{id}` | Delete document |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | Get dashboard statistics |

## 🔐 Authentication Flow

1. User registers with email, password, and display name
2. Password is hashed using bcrypt before storing
3. On login, credentials are verified and JWT token is issued
4. Frontend stores token in localStorage
5. Token is sent in Authorization header for protected routes
6. Backend validates token and extracts user info

## 🎯 Future Enhancements

- [ ] Real-time updates with WebSockets
- [ ] File attachments for tasks
- [ ] Email notifications
- [ ] Task due date reminders
- [ ] Activity timeline
- [ ] Dark mode
- [ ] Mobile app

## 👨‍💻 Author

**Sagar Kumbhar**

- GitHub: [@sagarkumbhar](https://github.com/sagarkumbhar)
- LinkedIn: [Sagar Kumbhar](https://linkedin.com/in/sagarkumbhar)
- Email: sagarkumbhar326@gmail.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Built with ❤️ using Vue.js and FastAPI
