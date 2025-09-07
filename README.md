# Wedding Dreams - מערכת ניהול השכרות לחתונות 💍

מערכת מקצועית לניהול השכרות ציוד לחתונות ואירועים עם עוזר AI ו-37 פריטי השכרה.

---

## 🚀 איך להריץ את הפרויקט

### 🐳 **הרצה עם Docker (מומלץ - דקה אחת)**

```bash
# שכפול הפרויקט
git clone https://github.com/RAZAMZALAG/Wedding.git
cd Wedding

# הפעלת כל המערכת
docker compose up --build

# הגישה: http://localhost:5173
```

### 💻 **הרצה מקומית (למפתחים)**

**דרישות:** Python 3.13+, Node.js 18+, MongoDB

```bash
# 1. שכפול והתקנה
git clone https://github.com/RAZAMZALAG/Wedding.git
cd Wedding

# 2. סביבה וירטואלית
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r Server/requirements.txt

# 3. התקנת Frontend
cd Client && npm install && cd ..

# 4. הפעלה
# טרמינל 1 - Server:
cd Server && python main.py

# טרמינל 2 - Client:
cd Client && npm run dev

# הגישה: http://localhost:5173
```

---

## 👤 כניסה למערכת

### **👨‍💼 חשבון מנהל מערכת**
- **אימייל:** `admin@email.com`
- **סיסמה:** `admin123`
- **הרשאות:** ניהול מלא - פריטים, הזמנות, משתמשים

### **👤 חשבון משתמש רגיל**
- **אימייל:** `user@email.com`
- **סיסמה:** `user123`
- **הרשאות:** הזמנות ועיון בקטלוג

---

## 🎯 פעולות במערכת

### **👀 לכל המשתמשים:**
- 📋 עיון בקטלוג של 37 פריטי השכרה
- 🔍 חיפוש וסינון לפי קטגוריות
- 🤖 שיחה עם עוזר AI לתכנון החתונה
- 👤 רישום וכניסה למערכת

### **🛒 למשתמשים רשומים:**
- 📅 הזמנת פריטים לטווח תאריכים
- � מעקב אחר הזמנות שלי
- 💰 צפייה בעלויות והערות
- 📧 קבלת התראות אימייל

### **👨‍💼 למנהלים בלבד:**
- ➕ הוספה/עריכה/מחיקה של פריטים
- � ניהול כל ההזמנות במערכת
- � ניהול משתמשים וחסימות
- 📈 צפייה בסטטיסטיקות

---

## 📦 מה כלול במערכת?

**37 פריטי השכרה בקטגוריות:**
- 🍽️ כלי הגשה וחרסינה (6 פריטים)
- 🪑 כיסאות ושולחנות (5 פריטים)  
- ✨ אבזרי נוי ועיצוב (10 פריטים)
- 🎤 ציוד הגברה (4 פריטים)
- 🔥 ציוד בישול וחימום (5 פריטים)
- 🛠️ ציוד עזר לאירועים (5 פריטים)
- � ציוד תאורה (2 פריטים)

**טכנולוגיות:** React + Flask + MongoDB + Docker + AI Assistant

---

## � תמיכה

נתקלת בבעיה? בדוק את [הלוגים](./Server/logs/) או [צור issue](https://github.com/RAZAMZALAG/Wedding/issues) בגיטהאב.
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
