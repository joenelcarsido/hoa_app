# Barangay Connect - HOA Management System

A comprehensive homeowners association management platform built for Filipino communities.

## Features

### 🏠 For Residents
- **Multiple Payment Options**: Pay HOA dues via GCash, Stripe (credit/debit cards), or PayPal
- **Payment History**: View all past payments and download receipts
- **Receipt Upload**: Upload and manage payment receipts
- **Announcements**: Stay updated with community announcements
- **Event Calendar**: View and register for community events
- **Discussion Board**: Engage with neighbors and board members
- **Document Library**: Access HOA rules, meeting minutes, and policies
- **Profile Management**: Update your contact info and unit details

### 👨‍💼 For Admins & Board Members
- **Admin Dashboard**: View analytics (total members, payments, revenue)
- **AI-Powered Announcements**: Draft professional announcements with GPT-5.2
- **User Management**: View and manage all community members
- **Document Management**: Upload and organize HOA documents
- **Event Management**: Create and manage community events
- **Payment Tracking**: Monitor all payments and outstanding balances
- **Bulk Notifications**: Send emails to all members via SendGrid

### 🔐 Security Features
- Email/Password authentication with JWT
- Google OAuth (via Emergent Auth)
- Role-based access control (Resident, Board Member, Admin)
- Secure payment processing via Stripe
- Password hashing with bcrypt

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB
- **Authentication**: JWT + Emergent Google Auth
- **Payment Processing**: Stripe (emergentintegrations)
- **Email**: SendGrid
- **AI**: OpenAI GPT-5.2 (emergentintegrations)

### Frontend
- **Framework**: React 19
- **UI Components**: shadcn/ui + Radix UI
- **Styling**: Tailwind CSS (Tropical Modernism design)
- **Forms**: React Hook Form + Zod validation
- **Routing**: React Router v7
- **Notifications**: Sonner

## Design System

**Theme**: Tropical Modernism
- **Primary Color**: Deep Emerald (#064E3B)
- **Secondary Color**: Terracotta (#C2410C)
- **Fonts**: Manrope (headings), Satoshi (body), JetBrains Mono (code)
- **Style**: Rounded-full buttons, rounded-2xl cards, generous spacing

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB 4.4+
- Yarn package manager

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd barangay-connect
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
cp .env.example .env
# Edit .env with your configuration

# Start the backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
yarn install

# Create .env file
cp .env.example .env.local
# Edit .env.local with your backend URL

# Start the frontend
yarn start
```

### 4. MongoDB Setup
```bash
# Start MongoDB (if not running)
mongod --dbpath /path/to/your/data/directory

# The app will create collections automatically
```

## Environment Variables

### Backend (.env)
```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="barangay_connect"
CORS_ORIGINS="http://localhost:3000"
JWT_SECRET_KEY="your-secret-key-here"
EMERGENT_LLM_KEY="your-emergent-key-here"
STRIPE_API_KEY="your-stripe-key-here"
SENDGRID_API_KEY="your-sendgrid-key-here"
SENDER_EMAIL="noreply@yourdomain.com"
```

### Frontend (.env.local)
```bash
REACT_APP_BACKEND_URL=http://localhost:8001
```

## Getting API Keys

1. **Emergent LLM Key**: https://emergent.sh/profile (for AI features)
2. **Stripe**: https://dashboard.stripe.com/apikeys (for payments)
3. **SendGrid**: https://app.sendgrid.com/settings/api_keys (for emails)

## User Roles

1. **Resident** (default)
   - View announcements, events, documents
   - Make payments and upload receipts
   - Participate in discussions
   - Manage own profile

2. **Board Member**
   - All resident permissions
   - Create announcements with AI drafting
   - Upload documents
   - Create events

3. **Admin**
   - All board member permissions
   - View analytics dashboard
   - Manage all users
   - Access admin APIs

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Project Structure

```
barangay-connect/
├── backend/
│   ├── server.py           # Main FastAPI application
│   ├── models.py           # Pydantic models
│   ├── auth.py             # Authentication logic
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables (gitignored)
├── frontend/
│   ├── public/            # Static files
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── contexts/      # React contexts (Auth)
│   │   ├── hooks/         # Custom hooks
│   │   ├── pages/         # Page components
│   │   ├── utils/         # Utilities (API client)
│   │   ├── App.js         # Main app component
│   │   └── index.css      # Global styles
│   ├── package.json       # Node dependencies
│   └── .env.local         # Environment variables (gitignored)
├── design_guidelines.json # Design system specs
├── auth_testing.md        # Authentication testing guide
└── README.md             # This file
```

## Testing

See `/auth_testing.md` for authentication testing guidelines.

## Deployment

### Backend Deployment (Example: Railway)
1. Connect your GitHub repository
2. Set environment variables
3. Deploy!

### Frontend Deployment (Example: Vercel)
1. Connect your GitHub repository
2. Set `REACT_APP_BACKEND_URL` to your backend URL
3. Deploy!

### MongoDB (Example: MongoDB Atlas)
1. Create a free cluster
2. Get connection string
3. Update `MONGO_URL` in backend .env

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this for your community!

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

- Built with ❤️ for Filipino communities
- Powered by Emergent.sh integrations
- UI components by shadcn/ui