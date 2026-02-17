# Food Science Toolbox AI Teaching Assistant

A specialized AI-powered platform exclusively designed for food science and consumer science educators. This production-ready application helps food science teachers create comprehensive, curriculum-aligned teaching materials in minutes.

## 🎯 Overview

Food Science Toolbox AI Teaching Assistant is your dedicated companion for food science education. Generate engaging, scientifically-accurate teaching content specifically tailored to food science curricula - from nutrition and food chemistry to culinary techniques and food safety. Built with modern technologies and following advanced AI prompting best practices for human-like, warm, and conversational output.

**Project Name**: Food Science Toolbox AI Teaching Assistant

---

## 🚀 Key Features

### Content Generation
- **Lesson Starter Generator**: Create engaging lesson openers with key concepts, discussion questions, and teacher scripts
- **Learning Objectives Generator**: Generate measurable, grade-appropriate learning objectives aligned with educational standards
- **Discussion Questions Generator**: Build thought-provoking questions that promote critical thinking
- **Slide Generator** *(Coming Soon)*: Generate professional presentation slides

### Platform Features
- **AI-Powered Content**: GPT-4o integration with prompts specifically optimized for food science education, delivering engaging, curriculum-relevant output
- **Authentication & Authorization**: Secure JWT-based authentication with role-based access control
- **Subscription Management**: Flexible membership tiers (Free, Starter, Pro) with usage tracking
- **Document Export**: Download generated content as Word (DOCX) or PDF documents
- **Favorites System**: Save and organize frequently used content
- **Responsive Design**: Fully responsive UI with modern, accessible design
- **Real-time Updates**: React Query for optimistic UI updates and caching

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 5
- **UI Components**: Radix UI with Tailwind CSS
- **State Management**: React Query (TanStack Query) for server state
- **Routing**: React Router v6
- **HTTP Client**: Axios with interceptors for authentication
- **Form Handling**: React Hook Form with Zod validation
- **Styling**: Tailwind CSS with custom design tokens
- **Icons**: Lucide React

### Backend
- **Framework**: Django 5.0 + Django REST Framework 3.14+
- **Database**: PostgreSQL 15
- **Task Queue**: Celery 5.3+ with Redis (optional)
- **Cache**: Redis (with local memory fallback)
- **AI Integration**: OpenAI Python SDK (GPT-4o)
- **Document Generation**: python-docx (DOCX), FPDF2 (PDF)
- **Payment Processing**: Stripe Python SDK
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Email**: Django email backend with SMTP
- **Environment**: python-decouple for configuration

### DevOps & Deployment
- **Containerization**: Docker with multi-stage builds
- **Web Server**: Nginx (frontend), Gunicorn (backend)
- **Deployment**: Nixpacks support for Coolify
- **Version Control**: Git with GitHub

---

## 📋 Prerequisites

### Frontend
- Node.js >= 18.0.0
- npm >= 9.0.0

### Backend
- Python 3.11+
- PostgreSQL 15
- Redis (optional, for Celery and caching)

---

## 🏗️ Installation & Setup

### Frontend Setup

```bash
# Navigate to project root
cd teachai-assistant

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Edit .env with your configuration
# VITE_API_BASE_URL=http://localhost:8000

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:8080`

### Backend Setup

```bash
# Navigate to backend directory
cd teachai-assistant/Backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/development.txt

# Create environment file
cp .env.example .env

# Edit .env with your configuration (see Environment Variables section)

# Run database migrations
python manage.py migrate

# Initialize membership tiers
python manage.py init_data

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

The backend API will be available at `http://localhost:8000`

---

## 🏗️ Project Structure

```
teachai-assistant/
├── Backend/                        # Django backend application
│   ├── apps/                       # Django apps (modular architecture)
│   │   ├── accounts/              # User authentication & profiles
│   │   ├── memberships/           # Subscription tiers & usage tracking
│   │   ├── payments/              # Stripe payment integration
│   │   ├── generators/            # AI content generation (OpenAI)
│   │   ├── downloads/             # Document export (DOCX/PDF)
│   │   ├── notifications/         # Email templating & notifications
│   │   ├── admin_dashboard/       # Admin interface APIs
│   │   ├── legal/                 # Legal document management
│   │   └── core/                  # Shared utilities, middleware, pagination
│   ├── config/                    # Django configuration
│   │   ├── settings/              # Environment-specific settings
│   │   │   ├── base.py           # Common settings
│   │   │   ├── development.py    # Development settings
│   │   │   ├── production.py     # Production settings
│   │   │   └── testing.py        # Test settings
│   │   ├── urls.py               # URL routing
│   │   ├── wsgi.py               # WSGI application
│   │   └── celery.py             # Celery configuration
│   ├── templates/                 # HTML templates
│   │   ├── downloads/            # Document templates (DOCX/PDF)
│   │   └── emails/               # Email templates
│   ├── requirements/              # Python dependencies
│   │   ├── base.txt              # Core dependencies
│   │   ├── development.txt       # Dev dependencies
│   │   ├── production.txt        # Production dependencies
│   │   └── testing.txt           # Test dependencies
│   ├── manage.py                  # Django management script
│   ├── start.sh                   # Production startup script
│   └── Dockerfile                 # Backend containerization
│
├── src/                           # Frontend React application
│   ├── components/               # Reusable UI components
│   │   ├── auth/                # Authentication components
│   │   ├── generators/          # Content generator forms
│   │   ├── layout/              # Layout components
│   │   └── ui/                  # Base UI components (shadcn/ui)
│   ├── contexts/                # React contexts
│   │   └── AuthContext.tsx      # Authentication state management
│   ├── hooks/                   # Custom React hooks
│   │   ├── useAuth.ts          # Authentication hook
│   │   ├── useGenerators.ts    # Content generation hook
│   │   └── useMembership.ts    # Membership management hook
│   ├── lib/                     # Utilities and API clients
│   │   ├── api/                # API service layer
│   │   │   ├── client.ts       # Axios instance with interceptors
│   │   │   ├── auth.ts         # Auth API calls
│   │   │   ├── generators.ts   # Generator API calls
│   │   │   └── membership.ts   # Membership API calls
│   │   └── utils/              # Utility functions
│   │       ├── contentFormatter.ts  # Content formatting logic
│   │       └── cn.ts               # Tailwind class merging
│   ├── pages/                   # Page components
│   │   ├── Home.tsx            # Landing page
│   │   ├── Dashboard.tsx       # Main dashboard
│   │   ├── LessonStarter.tsx   # Lesson starter generator
│   │   ├── LearningObjectives.tsx  # Learning objectives generator
│   │   ├── BellRinger.tsx      # Discussion questions generator
│   │   └── account/            # Account management pages
│   ├── App.tsx                 # Root component
│   ├── main.tsx                # Application entry point
│   └── index.css               # Global styles
│
├── public/                        # Static assets
├── dist/                          # Production build output
├── vite.config.ts                # Vite configuration
├── tailwind.config.ts            # Tailwind CSS configuration
├── tsconfig.json                 # TypeScript configuration
├── Dockerfile                    # Frontend containerization
├── nginx.conf                    # Nginx configuration
└── nixpacks.toml                 # Nixpacks deployment config
```

---

## 🌐 Environment Variables

### Frontend (.env)

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
```

### Backend (.env)

#### Required Variables

```env
# Django Core
SECRET_KEY=your-secret-key-here-generate-with-django
DEBUG=False
ALLOWED_HOSTS=*

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname
# OR individual database settings:
DB_NAME=teachai_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# OpenAI Integration (Required for content generation)
OPENAI_API_KEY=sk-your-openai-api-key

# Stripe Payment Integration (Required for subscriptions)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

#### Optional Variables

```env
# Redis (for caching and Celery)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Configuration (SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=mail.your-domain.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_USE_TLS=False
EMAIL_HOST_USER=admin@your-domain.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=admin@your-domain.com

# Frontend URL (for CORS and redirects)
FRONTEND_URL=https://your-frontend-domain.com
```

#### Email Configuration Notes

- **Port 465**: Uses SSL/TLS encryption (set `EMAIL_USE_SSL=True`, `EMAIL_USE_TLS=False`)
- **Port 587**: Uses STARTTLS (set `EMAIL_USE_TLS=True`, `EMAIL_USE_SSL=False`)
- Test email: `python manage.py shell` then `from django.core.mail import send_mail; send_mail(...)`

#### Stripe Configuration Notes

To get Stripe Price IDs:
1. Go to https://dashboard.stripe.com/test/products (Test mode)
2. Create products for each tier (Starter: $12/month, Pro: $25/month)
3. Copy the Price IDs (format: `price_1Ab2Cd3Ef4Gh5Ij6Kl7Mn8Op9Qr0St`)
4. Update in Django Admin → Membership Tiers → Stripe Price ID field

---

## 📡 API Endpoints

All API endpoints are prefixed with `/api/`:

### Authentication (`/api/accounts/`)
- `POST /api/accounts/register/` - User registration
- `POST /api/accounts/login/` - User login (returns JWT tokens)
- `POST /api/accounts/token/refresh/` - Refresh access token
- `GET /api/accounts/profile/` - Get user profile
- `PUT /api/accounts/profile/` - Update user profile
- `POST /api/accounts/change-password/` - Change password
- `POST /api/accounts/reset-password/` - Request password reset
- `POST /api/accounts/reset-password-confirm/` - Confirm password reset

### Membership (`/api/memberships/`)
- `GET /api/memberships/tiers/` - List all membership tiers
- `GET /api/memberships/current/` - Get current user's membership
- `GET /api/memberships/usage/` - Get usage statistics

### Payments (`/api/payments/`)
- `POST /api/payments/create-checkout-session/` - Create Stripe checkout session
- `POST /api/payments/webhook/` - Stripe webhook handler
- `GET /api/payments/subscription/` - Get subscription details
- `POST /api/payments/cancel-subscription/` - Cancel subscription

### Content Generation (`/api/generators/`)
- `POST /api/generators/lesson-starter/` - Generate lesson starter
- `POST /api/generators/learning-objectives/` - Generate learning objectives
- `POST /api/generators/discussion-questions/` - Generate discussion questions
- `GET /api/generators/content/` - List generated content
- `GET /api/generators/content/{id}/` - Get specific content
- `DELETE /api/generators/content/{id}/` - Delete content
- `POST /api/generators/content/{id}/favorite/` - Toggle favorite status

### Document Downloads (`/api/downloads/`)
- `GET /api/downloads/{content_id}/docx/` - Download as Word document
- `GET /api/downloads/{content_id}/pdf/` - Download as PDF

### Admin Dashboard (`/api/admin-dashboard/`)
- `GET /api/admin-dashboard/stats/` - Platform statistics
- `GET /api/admin-dashboard/users/` - User management
- `GET /api/admin-dashboard/content/` - Content analytics

### Legal (`/api/legal/`)
- `GET /api/legal/terms/` - Terms of service
- `GET /api/legal/privacy/` - Privacy policy

### Health Check
- `GET /api/health/` - API health check endpoint

---

## 🎨 Frontend Architecture

### State Management
- **Server State**: React Query (TanStack Query) for API data caching and synchronization
- **Auth State**: React Context API for authentication state
- **Form State**: React Hook Form for form validation and submission
- **URL State**: React Router for navigation and route parameters

### Key Design Patterns
- **Component Composition**: Reusable UI components built with Radix UI primitives
- **Custom Hooks**: Encapsulate business logic (useAuth, useGenerators, useMembership)
- **API Service Layer**: Centralized Axios client with interceptors for auth
- **Error Boundaries**: Graceful error handling throughout the app
- **Optimistic Updates**: Immediate UI feedback with React Query mutations

### Styling Approach
- **Tailwind CSS**: Utility-first CSS framework
- **Custom Design Tokens**: Defined in `tailwind.config.ts`
- **Component Variants**: Using `class-variance-authority` (cva)
- **Responsive Design**: Mobile-first approach with breakpoints

---

## 🔧 Backend Architecture

### Design Patterns
- **Service-Oriented Architecture**: Business logic in service classes
- **Repository Pattern**: Database access abstraction
- **Middleware**: Custom middleware for CORS, authentication, error handling
- **Signals**: Django signals for event-driven operations
- **Serializers**: DRF serializers for data validation and transformation

### AI Content Generation (GPT-4o)
Located in `Backend/apps/generators/`:

#### Key Components
- **`openai_service.py`**: OpenAI API integration with GPT-5.2
- **`prompt_templates.py`**: Optimized prompts following GPT-5.2 best practices
- **`document_formatter.py`**: DOCX/PDF formatting with metadata stripping
- **`views.py`**: API endpoints for content generation

#### Prompt Engineering Features
- **Human-like Output**: Warm, conversational tone suitable for classroom instruction
- **Persona Definition**: "Experienced food science teacher" perspective
- **Forbidden Phrases**: Blocks AI-sounding language ("delve into", "it's important to note")
- **Verbosity Constraints**: Precise word counts for each section
- **Level Differentiation**: Distinct cognitive verbs for each grade level
- **Quality Checks**: Self-verification before output

#### Content Types
1. **Lesson Starter**: 180-200 word teacher script with discussion question
2. **Learning Objectives**: 3-7 measurable objectives with action verbs
3. **Discussion Questions**: Grade-appropriate questions with scenario-based framing

### Document Generation
- **DOCX**: Uses `python-docx` with custom formatting (Arial fonts, specific spacing)
- **PDF**: Uses `FPDF2` with HTML templates for consistent styling
- **Metadata Stripping**: Category field collected but excluded from output

---

# Deployment to SiteGround (frontend) & Render (backend)

## Frontend — automatic deploy (SiteGround)

- A GitHub Action is included: `.github/workflows/deploy-frontend-siteground.yml` — it builds the `dist/` production bundle and uploads via `rsync` over SSH to your SiteGround subdomain folder.

- Required GitHub repository secrets (add in Settings → Secrets → Actions):
  - `SITEGROUND_HOST` — SFTP/SSH host (example: `ssh.siteground.com` or your hosting host)
  - `SITEGROUND_USER` — SFTP username
  - `SITEGROUND_PATH` — remote path for `ai.foodsciencetoolbox.com` (example: `/home/<account>/public_html/ai/`)
  - `SITEGROUND_SSH_PRIVATE_KEY` — private SSH key for the SFTP user (no passphrase recommended)

- Manual alternative:
  - Local build: `VITE_API_BASE_URL=https://api.foodsciencetoolbox.com npm ci && npm run build`
  - Upload with rsync: `rsync -avz dist/ user@host:/home/<account>/public_html/ai/`
  - Or run the helper script: `SITEGROUND_HOST=... SITEGROUND_USER=... SITEGROUND_PATH=... SITEGROUND_SSH_KEY=~/.ssh/id_rsa npm run deploy:siteground`

---

## Backend — recommended host: Render

- A `Backend/render.yaml` manifest is included so Render can auto-detect and deploy the Django service when you connect this GitHub repository.
- On Render, create a new Web Service and select this repo — Render will use `Backend/render.yaml` and the `Backend/Dockerfile`.
- Required environment variables in Render:
  - `SECRET_KEY`, `DATABASE_URL` (or attach a managed Postgres), `DJANGO_SETTINGS_MODULE=config.settings.production`, `ALLOWED_HOSTS=api.foodsciencetoolbox.com`, `CORS_ALLOWED_ORIGINS=https://ai.foodsciencetoolbox.com`, plus any Stripe/OpenAI keys.
- Add the custom domain `api.foodsciencetoolbox.com` in Render; Render will provide a CNAME target. Add that CNAME to SiteGround DNS (Domain → DNS Zone Editor → add CNAME `api` → value from Render).

---

## DNS & SSL

- Frontend subdomain `ai.foodsciencetoolbox.com` already exists on SiteGround. Ensure its document root contains the `dist/` contents.
- For the backend, add a DNS CNAME record for `api` pointing to Render's CNAME target (or an A record if you host elsewhere).
- After DNS is set, SiteGround (frontend) and Render (backend) will issue TLS automatically (Let's Encrypt).

---

## Quick verification commands

- Check frontend is reachable: `curl -I https://ai.foodsciencetoolbox.com`
- Check backend health: `curl -I https://api.foodsciencetoolbox.com/api/health/`
- Check CORS header from backend (simulate frontend origin):
  `curl -H "Origin: https://ai.foodsciencetoolbox.com" -I https://api.foodsciencetoolbox.com/`

---

### Next steps

If you want, I can now:
1) Run a local production build and produce `dist/` for you to upload, and/or
2) Create a Pull Request with these changes so you can review, or
3) Guide you through adding the GitHub secrets and connecting Render.

Tell me which of the three to do next.


### Payment Integration
- **Stripe Checkout**: Server-side session creation for PCI compliance
- **Webhooks**: Handle subscription lifecycle events
- **Usage Tracking**: Real-time usage limits based on membership tier

---

## 📜 Available Scripts

### Frontend

```bash
npm run dev          # Start development server (port 8080)
npm run build        # Build for production
npm run build:dev    # Build in development mode
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm start            # Serve production build
```

### Backend

```bash
python manage.py runserver         # Start development server
python manage.py migrate           # Run database migrations
python manage.py makemigrations    # Create new migrations
python manage.py createsuperuser   # Create admin user
python manage.py init_data         # Initialize membership tiers
python manage.py test              # Run Django tests
pytest --cov                       # Run tests with coverage
python manage.py shell             # Django shell
python manage.py collectstatic     # Collect static files
```

---

## 🧪 Testing

### Frontend Testing
```bash
# Run tests (when configured)
npm test

# Run tests with coverage
npm run test:coverage
```

### Backend Testing
```bash
# Django test runner
python manage.py test

# Pytest with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest apps/generators/tests/test_openai_service.py
```

### Test Coverage
- Unit tests for API endpoints
- Integration tests for payment flows
- Service layer tests for AI generation
- Serializer validation tests

---

## 🚢 Deployment

### Production Build

#### Frontend
```bash
npm run build
```
Output: `dist/` directory with optimized static files

#### Backend
```bash
# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput

# Initialize data
python manage.py init_data
```

### Docker Deployment

#### Full Stack with Docker Compose
```bash
docker-compose up -d
```

#### Individual Services

**Frontend:**
```bash
cd teachai-assistant
docker build -t teachai-frontend .
docker run -p 80:80 teachai-frontend
```

**Backend:**
```bash
cd teachai-assistant/Backend
docker build -t teachai-backend .
docker run -p 8000:8000 teachai-backend
```

### Nixpacks Deployment (Coolify/Railway)

The project includes `nixpacks.toml` for automatic deployment:

**Frontend:**
- Build command: `npm run build`
- Start command: `nginx -g 'daemon off;'`
- Port: 80

**Backend:**
- Build command: `pip install -r requirements/production.txt`
- Start command: `./start.sh`
- Port: 8000

### Production Checklist

#### Pre-Deployment
1. ✅ Set all required environment variables
2. ✅ Generate Django SECRET_KEY
3. ✅ Set DEBUG=False
4. ✅ Configure DATABASE_URL
5. ✅ Add ALLOWED_HOSTS
6. ✅ Set up OpenAI API key
7. ✅ Configure Stripe keys
8. ✅ Set up email SMTP settings
9. ✅ Configure CORS_ALLOWED_ORIGINS

#### Post-Deployment
1. ✅ Run database migrations
2. ✅ Initialize membership tiers
3. ✅ Create superuser
4. ✅ Collect static files
5. ✅ Test payment webhook
6. ✅ Test email sending
7. ✅ Verify AI generation works
8. ✅ Check HTTPS certificate

#### Monitoring
- Django logs: `logs/django.log`
- Gunicorn logs: `logs/gunicorn.log`
- Celery logs: `logs/celery.log`
- Nginx access/error logs

---

## 🔒 Security Considerations

### Authentication
- JWT tokens with expiration
- Refresh token rotation
- Password hashing with bcrypt
- CSRF protection enabled

### Data Protection
- Environment variables for secrets
- SQL injection protection (ORM)
- XSS protection (React escaping)
- CORS configuration

### Payment Security
- PCI compliance via Stripe
- Server-side session creation
- Webhook signature verification
- No credit card data stored

---

## 📊 Database Schema

### Key Models

#### User (accounts.User)
- Custom user model extending AbstractUser
- Email as username
- Profile fields (name, preferences)

#### MembershipTier (memberships.MembershipTier)
- name, description, price
- monthly_generation_limit
- stripe_price_id
- features (JSONField)

#### UserMembership (memberships.UserMembership)
- user, tier
- stripe_subscription_id
- start_date, end_date
- is_active

#### GeneratedContent (generators.GeneratedContent)
- user, content_type
- topic, grade_level, category
- content (TextField)
- tokens_used, generation_time
- is_favorite
- created_at, updated_at

#### UsageTracking (memberships.UsageTracking)
- user_membership
- month, year
- generations_count
- last_reset_date

---

## 🎓 Content Generation Specifications

### Grade Levels
- Elementary
- Middle School
- High School
- Undergraduate/College

### Subjects/Categories
- Food Science (default)
- Consumer Science
- Nutrition
- Food Safety
- Food Processing

### Output Format

#### Lesson Starter
```
Lesson Starter
Grade Level: [level]
Topic: [topic]

Key Lesson Ideas to Explore
• [4-6 bullet points]

Prior Knowledge to Connect
[3-5 sentences for teacher planning]

Teacher Opening Script
[180-200 words, student-facing]

Discussion Question (5 minutes)
[Italicized open-ended question]
```

#### Learning Objectives
```
Lesson Objectives
Grade Level: [level]
Topic: [topic]

By the end of this lesson, students will be able to:
1. [Measurable objective with action verb]
2. [Measurable objective with action verb]
[3-7 objectives total]
```

#### Discussion Questions
```
Discussion Questions
Grade Level: [level]
Topic: [topic]

1. [Question with scenario-based framing]
2. [Question with scenario-based framing]
[Exact number requested]
```

---

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes with clear, descriptive commits
4. Run tests: `npm test` (frontend), `pytest` (backend)
5. Push to branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Code Style
- **Frontend**: ESLint + TypeScript strict mode
- **Backend**: PEP 8 with type hints
- **Commits**: Conventional Commits format
- **Documentation**: Update README for new features

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 📞 Support & Contact

For support, bug reports, or feature requests:
- Open an issue in the repository
- Contact the development team
- Check documentation in code comments

---

## 🙏 Acknowledgments

- Built with ❤️ for food science educators
- Powered by OpenAI GPT-5.2
- UI components from Radix UI and shadcn/ui
- Icons from Lucide React

---

**Last Updated**: December 2025  
**Version**: 1.0.0  
**Maintainer**: Development Team
