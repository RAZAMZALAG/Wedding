# Wedding Planner - מערכת ניהול השכרות לאירועים 💍

מערכת מקצועית לניהול השכרות ציוד לאירועים עם עוזר AI, ניהול לקוחות וזמינות ציוד.

## 🚀 איך להריץ את הפרויקט

### אופציה 1: הרצה עם Docker (מומלץ)

```bash
# 1. שכפול הפרויקט
git clone https://github.com/RAZAMZALAG/Wedding.git
cd Wedding

# 2. הפעלת המערכת (כולל טעינת מסד נתונים אוטומטית)
docker compose up --build

# גישה: http://localhost:5000
# עצירה: docker compose down
```

**מה קורה מאחורי הקלעים:**
- המערכת אוטומטית מורידה תמונות קטלוג
- יוצרת 100+ משתמשים דמו במערכת
- מייצרת 200+ מוצרים מגוונים מכל הקטגוריות
- מתחילה את השרת Flask על פורט 5000

### אופציה 2: הרצה מקומית (כולל טעינת DB)

**התקנה חד פעמית:**
```bash
# 1. התקן דרישות: Python 3.13+, Node.js 18+, MongoDB
winget install MongoDB.Server  # Windows
winget install Python.Python.3.13
winget install OpenJS.NodeJS

# 2. שכפול והתקנה
git clone https://github.com/RAZAMZALAG/Wedding.git
cd Wedding

# 3. סביבה וירטואלית
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r Server/requirements.txt

# 4. התקנת frontend
cd Client
npm install
cd ..
```

**הפעלה יומיומית:**
```bash
# 1. הפעל MongoDB
net start MongoDB  # Windows

# 2. טעינת DB (רק פעם ראשונה או לאיפוס)
cd Server
python migrate_to_mongo.py

# 3. הפעל שרת (טרמינל 1)
python main.py

# 4. הפעל frontend (טרמינל 2)
cd ../Client
npm run dev

# גישה: http://localhost:5173
```

## 👤 כניסה למערכת

| משתמש | סיסמה | תפקיד |
|-------|--------|--------|
| admin@email.com | password | מנהל |
| user@email.com | password | משתמש |

---

**טכנולוגיות:** React, Flask, MongoDB, AI Assistant

# Wedding Planner - Event Equipment Rental System 💍✨

A complete wedding equipment rental management system with inventory tracking, booking management, and AI-powered assistance.

![Wedding Planner](https://img.shields.io/badge/Wedding-Planner-pink?style=for-the-badge)
![React](https://img.shields.io/badge/React-18-blue?style=for-the-badge&logo=react)
![Flask](https://img.shields.io/badge/Flask-Python-green?style=for-the-badge&logo=flask)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?style=for-the-badge&logo=docker)

## 📋 Project Overview

Wedding Planner is a comprehensive rental management system designed for wedding equipment businesses. It features:

- 🎯 **Complete Equipment Catalog** - Manage wedding items across multiple categories
- 📅 **Advanced Booking System** - Date-range based availability and rental management
- 👥 **Customer Management** - User accounts, authentication, and booking history
- 🤖 **AI Assistant** - Powered by Google Gemini for wedding planning advice
- 🌍 **Multi-language Support** - Hebrew, English, Arabic, and Russian
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 📊 **Admin Dashboard** - Complete business management tools

## 🎪 Equipment Categories

- 🍽️ **Tableware & Serving** - Plates, glasses, serving dishes
- 🪑 **Furniture** - Chairs, tables, seating arrangements  
- ✨ **Decorations** - Centerpieces, lighting, floral arrangements
- 🎤 **Audio/Visual** - Sound systems, microphones, lighting
- � **Catering Equipment** - Chafing dishes, warmers, serving tools
- 🎪 **Event Support** - Tents, arches, backdrops
- 💌 **Stationery** - Invitations, place cards, signage
- 💎 **Accessories** - Jewelry, veils, decorative items
- 🚗 **Transportation** - Wedding car decorations

## 🚀 Quick Start Guide

### Option 1: Docker Setup (Recommended - 5 Minutes)

**Prerequisites:**
- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/wedding-planner.git
cd wedding-planner

# 2. Start everything with one command
docker compose up --build
```

**That's it!** Your system is now running:
- 🌐 **Frontend**: http://localhost:5173
- 🔌 **API**: http://localhost:5000
- 🗄️ **Database**: PostgreSQL (internal)

### Option 2: Manual Setup

**Prerequisites:**
- Node.js 18+
- Python 3.8+
- PostgreSQL 12+

#### Database Setup
```bash
# MongoDB will start automatically with Docker Compose
# No manual database creation needed

# Or start MongoDB manually:
mongosh
# In MongoDB shell:
use wedding_planner
```

#### Backend Setup
```bash
cd Server

# Create and activate virtual environment
python -m venv .venv

# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database settings

# Initialize database and create sample data
python migrate_to_mongo.py

# Start server
python main.py
```

#### Frontend Setup
```bash
cd Client

# Install dependencies
npm install

# Start development server
npm run dev
```

## ⚙️ Configuration

### Environment Variables (.env file)

```env
# MongoDB Configuration
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=admin123
MONGO_DATABASE=wedding_planner

# Application
CLIENT_PORT=5000
ENV=DEV
DEV_MONGO_URI=mongodb://admin:admin123@localhost:27017/wedding_planner?authSource=admin

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-here
FLASK_JWT_SECRET_KEY=your-super-secret-jwt-key-here

# Email Notifications (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# AI Assistant (Optional)
GEMINI_API_KEY=your-google-gemini-api-key
```

## � Default User Accounts

| Role | Email | Password | Access Level |
|------|-------|----------|--------------|
| Admin | admin@email.com | admin123 | Full system access |
| Customer | user@email.com | user123 | Rental and booking |

**⚠️ Change these passwords in production!**

## 🏗️ Technology Stack

### Frontend
- **React 18** - Modern UI framework
- **Material-UI** - Component library and theming
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing
- **i18next** - Internationalization

### Backend
- **Flask** - Python web framework
- **PyMongo** - MongoDB driver for Python  
- **JWT** - Authentication and authorization
- **Flask-Mail** - Email notifications
- **Google Gemini AI** - AI assistant integration

### Database
- **MongoDB** - Primary NoSQL database
- **Docker MongoDB** - Containerized database

### DevOps
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Production web server (optional)

## � API Documentation

### Authentication Endpoints
```
POST /auth/login       - User login
POST /auth/register    - User registration
POST /auth/logout      - User logout
GET  /auth/verify      - Email verification
```

### Catalog Endpoints
```
GET    /items          - Get all items
GET    /items/:id      - Get item details
POST   /items          - Create item (admin)
PUT    /items/:id      - Update item (admin)
DELETE /items/:id      - Delete item (admin)
```

### Booking Endpoints
```
GET    /bookings       - Get user bookings
POST   /bookings       - Create new booking
GET    /bookings/:id   - Get booking details
PUT    /bookings/:id   - Update booking status (admin)
```

### Admin Endpoints
```
GET    /admin/users    - Manage users
GET    /admin/bookings - Manage all bookings
GET    /admin/stats    - System statistics
```

## 🐛 Troubleshooting

### Common Issues

#### Docker Issues
```bash
# If containers won't start
docker compose down
docker compose up --build --force-recreate

# Check container logs
docker compose logs

# Reset everything
docker compose down -v
docker compose up --build
```

#### Port Conflicts
```bash
# Find what's using port 5173 (Windows)
netstat -ano | findstr :5173

# Find what's using port 5173 (macOS/Linux)
lsof -i :5173

# Kill the process or change ports in docker-compose.yml
```

#### Database Connection Issues
```bash
# Reset database completely
docker compose down -v
docker volume prune
docker compose up --build
```

#### Frontend Build Issues
```bash
cd Client
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Performance Tips
- Allocate at least 4GB RAM to Docker Desktop
- Close other development tools while running
- Use SSD storage for better database performance

## � Project Structure

```
├── Client/                 # React Frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/         # Application pages
│   │   ├── context/       # React context providers
│   │   └── styles/        # Theme and styling
│   └── package.json
├── Server/                 # Flask Backend
│   ├── models.py          # MongoDB data models
│   ├── auth.py           # Authentication routes
│   ├── users.py          # User management
│   ├── items.py          # Wedding items catalog
│   ├── bookings.py       # Rental system
│   ├── ai_assistant.py   # AI chatbot integration
│   └── requirements.txt
├── docker-compose.yaml    # Multi-container setup
├── Dockerfile            # Server container config
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/wedding-planner/issues)
- **Email**: wedding.dreams.orders@gmail.com
- **Documentation**: This README and inline code comments

## 🎯 Roadmap

- [ ] Mobile app development
- [ ] Payment gateway integration
- [ ] Advanced reporting and analytics
- [ ] Multi-location support
- [ ] Integration with wedding planning platforms
- [ ] Advanced AI recommendations

---

**Built with ❤️ for wedding professionals**

## פיצ'רים מיוחדים

- 🤖 עוזר בינה מלאכותית עם Google Gemini
- 📱 ממשק רספונסיבי
- 🌍 תמיכה רב-לשונית
- 📧 התראות אימייל אוטומטיות
- 🛒 עגלת קניות מתקדמת
- 📊 דשבורד ניהול

## רישיונות

פרויקט זה נבנה כחלק ממערכת ניהול חנות חתונות מקצועית.

## צור קשר

לשאלות ותמיכה: wedding.dreams.orders@gmail.com
