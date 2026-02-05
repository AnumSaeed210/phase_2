# Task
- Multi-User Task Management Application

A modern, full-stack web application for efficient task management with priority-based organization, built using Next.js, FastAPI, and PostgreSQL.

## ✨ Features

- **Secure User Authentication** - Complete sign up, sign in, and sign out flow with JWT-based authentication
- **Comprehensive Task Management** - Full CRUD operations for tasks with intuitive interface
- **Priority-Based Organization** - Categorize tasks by low, medium, or high priority levels
- **Flexible Task Status** - Toggle tasks between complete and incomplete states
- **Responsive Design** - Seamless experience across desktop, tablet, and mobile devices
- **Real-time Synchronization** - Optimistic UI updates with automatic server synchronization

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16+, React 19, TypeScript, Tailwind CSS |
| Backend | Python FastAPI, SQLModel ORM |
| Database | PostgreSQL (Neon Serverless) |
| Authentication | Better Auth with JWT tokens |
| UI Icons | lucide-react |

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+ (Python 3.12 recommended)
- PostgreSQL connection string (Neon recommended)

### Installation & Setup

**Backend Setup:**
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\Activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your DATABASE_URL and BETTER_AUTH_SECRET
python main.py
# Server runs on http://localhost:8000
```

**Frontend Setup:**
```bash
cd frontend
npm install --legacy-peer-deps
cp .env.example .env.local
# Edit .env.local with NEXT_PUBLIC_API_BASE_URL
npm run dev
# Application runs on http://localhost:3000
```

## 📁 Project Structure
```
taskie-todo-app/
├── frontend/              # Next.js application
│   ├── src/
│   │   ├── app/          # App routes, pages, and layouts
│   │   ├── components/   # Reusable React components
│   │   └── lib/          # Utilities, custom hooks, API client
│   └── package.json
├── backend/               # FastAPI application
│   ├── src/
│   │   ├── api/          # REST API endpoints
│   │   ├── auth/         # Authentication & authorization logic
│   │   ├── models.py     # SQLModel database models
│   │   └── schemas.py    # Pydantic request/response schemas
│   ├── main.py           # Application entry point
│   └── requirements.txt  # Python dependencies
├── specs/                 # Feature specifications & documentation
└── README.md             # Project documentation
```

## 🔌 API Endpoints

### Authentication Routes

- `POST /auth/signup` - Register a new user account
- `POST /auth/signin` - Authenticate and login user
- `POST /auth/signout` - Logout and invalidate session

### Task Management Routes

- `GET /api/{userId}/tasks` - Retrieve all tasks for a user
- `POST /api/{userId}/tasks` - Create a new task
- `PUT /api/{userId}/tasks/{taskId}` - Update an existing task
- `PATCH /api/{userId}/tasks/{taskId}/status` - Update task completion status
- `DELETE /api/{userId}/tasks/{taskId}` - Delete a task

## ⚙️ Environment Configuration

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@host:port/database
BETTER_AUTH_SECRET=your_secure_secret_key_minimum_32_characters
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your_secure_secret_key_minimum_32_characters
NODE_ENV=development
```

## 💻 Development Guidelines

- **Spec-Driven Development** - All features are defined in `specs/` directory before implementation
- **Type Safety** - Full TypeScript coverage in frontend and Pydantic schemas in backend
- **Code Quality** - Run `npm run build` (frontend) to verify production build integrity
- **Version Control** - Feature branches merged to main branch after thorough code review

## 🚢 Deployment

### Frontend Deployment
Deploy the `frontend/` directory to platforms like:
- **Vercel** (Recommended for Next.js)
- **Netlify**
- **AWS Amplify**

### Backend Deployment
Deploy the `backend/` directory to platforms like:
- **Railway** (Recommended)
- **Render**
- **Heroku**
- **AWS EC2**

### Database
PostgreSQL connection configured for Neon Serverless (no additional setup required)

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## 👨‍💻 Author

**Your Name**
- GitHub: [@AnumSaeed210](https://github.com/AnumSaeed210)

---

**Note:** Make sure to keep your `.env` and `.env.local` files secure and never commit them to version control.
