# 📦 Barangay Connect - Download Package

## Available Download Files

Two versions of the same project (choose one):

1. **barangay-connect-clean.tar.gz** (258 KB)
   - Best for Mac/Linux users
   - Extract: `tar -xzf barangay-connect-clean.tar.gz`

2. **barangay-connect-clean.zip** (297 KB)
   - Best for Windows users
   - Extract: Right-click → Extract All

## 📁 What's Included

```
barangay-connect/
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore rules
├── README.md                 # Complete documentation
├── auth_testing.md           # Testing guide
├── design_guidelines.json    # Design system
│
├── backend/
│   ├── auth.py              # Authentication logic
│   ├── models.py            # Database models
│   ├── server.py            # FastAPI application
│   └── requirements.txt     # Python dependencies
│
└── frontend/
    ├── .env.example         # Frontend env template
    ├── src/
    │   ├── components/      # UI components (shadcn/ui)
    │   ├── contexts/        # React contexts (Auth)
    │   ├── pages/           # All pages (Landing, Login, Dashboard, etc.)
    │   ├── utils/           # API client
    │   ├── App.js           # Main app
    │   └── index.css        # Styles (Tropical Modernism)
    ├── package.json         # Node dependencies
    ├── tailwind.config.js   # Tailwind config
    └── yarn.lock            # Dependency lock file
```

## 🚀 Quick Start After Download

### 1. Extract the Archive
```bash
# For .tar.gz
tar -xzf barangay-connect-clean.tar.gz
cd barangay-connect

# For .zip (Windows)
# Right-click → Extract All
# Then open folder
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env
# Edit .env and add your API keys

# Start backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
yarn install

# Create .env file
cp .env.example .env.local
# Edit .env.local (set REACT_APP_BACKEND_URL=http://localhost:8001)

# Start frontend
yarn start
```

### 4. MongoDB Setup
```bash
# Make sure MongoDB is running
mongod --dbpath /path/to/data

# The app will auto-create collections
```

## 🔑 Required API Keys

Get these keys and add to `.env`:

1. **EMERGENT_LLM_KEY** (for AI features)
   - Get from: https://emergent.sh/profile
   
2. **STRIPE_API_KEY** (for payments)
   - Get from: https://dashboard.stripe.com/apikeys
   - Use test keys: `sk_test_...`
   
3. **SENDGRID_API_KEY** (for emails)
   - Get from: https://app.sendgrid.com/settings/api_keys
   - Optional for basic testing

## 📝 What's NOT Included (and why)

These are excluded for security/size:
- ❌ node_modules/ (huge, reinstall with `yarn install`)
- ❌ venv/ (Python virtualenv, recreate with `python -m venv venv`)
- ❌ .env files with real API keys (security!)
- ❌ __pycache__/ (Python cache)
- ❌ build/ (compiled output)

## 🌐 Upload to GitHub

```bash
cd barangay-connect
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_URL
git push -u origin main
```

The `.gitignore` is already configured to protect your secrets!

## 📚 Documentation

See `README.md` for:
- Complete feature list
- Tech stack details
- API documentation
- Deployment guides
- User roles explanation

## 🆘 Need Help?

1. Check `README.md` for detailed setup
2. See `auth_testing.md` for authentication testing
3. View `design_guidelines.json` for design specs

## ✨ Features Included

✅ Payment processing (Stripe, GCash, PayPal)
✅ User authentication (JWT + Google OAuth)
✅ Admin dashboard with analytics
✅ AI-powered announcement drafting
✅ Document management
✅ Event calendar
✅ Discussion boards
✅ Email notifications (SendGrid)
✅ Role-based access control
✅ Beautiful Tropical Modernism UI

Built with ❤️ for Filipino communities!
