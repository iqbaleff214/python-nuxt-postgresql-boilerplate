# Full-Stack Boilerplate — Nuxt.js + FastAPI

A production-ready, batteries-included boilerplate with authentication, profile management, user management, real-time notifications, background jobs, cloud storage, and 2FA.

## Stack

| Layer | Technology |
|---|---|
| Frontend | Nuxt.js 3 + TypeScript + Tailwind CSS |
| Backend | FastAPI (Python 3.12+) |
| Database | PostgreSQL 16 |
| Queue / Cache | Redis 7 |
| Background Jobs | ARQ (async Redis Queue) |
| Storage | S3-compatible (MinIO in dev, AWS/R2 in prod) |
| Auth | JWT + TOTP 2FA |
| Email | SMTP / SendGrid / Resend (configurable) |
| Container | Docker + Docker Compose |

## Features

- **Authentication** — register, email verification, login, logout, forgot/reset password, change password
- **Two-Factor Authentication (2FA)** — TOTP (Google Authenticator, Authy), QR code setup, 8 recovery codes
- **Profile Management** — avatar upload, display name, bio, email change, account self-deletion with 30-day undo
- **User Management** — superadmin panel: list/filter/search users, create, update, activate/deactivate/ban, delete
- **Real-Time Notifications** — WebSocket push + persisted history, unread count badge
- **Background Jobs** — email sending, notification delivery, daily maintenance (token cleanup, hard-deletes)
- **Cloud Storage** — S3-compatible backend (MinIO for dev), swappable via env var
- **Email Templates** — 9 HTML transactional email templates (Jinja2)
- **Docker** — single `docker compose up` to run the full stack

---

## Quick Start (Development)

### Prerequisites
- Docker + Docker Compose v2
- `make` (optional, for convenience commands)

### 1. Clone & configure

```bash
git clone <repo>
cd <repo>
cp .env.example .env.dev
```

Edit `.env.dev` and fill in:
- `SECRET_KEY` — at least 32 random characters
- `TOTP_ENCRYPTION_KEY` — generate with `make gen-key`

### 2. Start the stack

```bash
make dev
# or: docker compose -f docker-compose.dev.yml up --build
```

This starts: **frontend** (3000) · **backend** (8000) · **PostgreSQL** (5432) · **Redis** (6379) · **MinIO** (9000/9001) · **MailHog** (8025) · **Redis Commander** (8081)

### 3. Open the app

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API docs (Swagger) | http://localhost:8000/docs |
| MailHog (email UI) | http://localhost:8025 |
| MinIO console | http://localhost:9001 (admin/minioadmin) |
| Redis Commander | http://localhost:8081 |

---

## Project Structure

```
.
├── frontend/              # Nuxt.js 3 application
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── api/v1/        # REST API endpoints
│   │   ├── ws/            # WebSocket endpoint
│   │   ├── core/          # Config, DB, Redis, security
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── jobs/          # ARQ background jobs
│   │   ├── templates/     # Jinja2 email templates
│   │   └── migrations/    # Alembic migrations
├── docker-compose.yml     # Simple production (no reverse proxy)
├── docker-compose.prod.yml # Production with Traefik
├── docker-compose.dev.yml # Development (with dev tools)
├── .env.example           # Environment variable template
├── Makefile               # Convenience commands
└── PRD.md                 # Product Requirements Document
```

---

## API Overview

Base URL: `http://localhost:8000/api/v1`

### Auth
| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Register new user |
| POST | `/auth/verify-email` | Verify email with token |
| POST | `/auth/resend-verification` | Resend verification email |
| POST | `/auth/login` | Login (returns tokens or MFA challenge) |
| POST | `/auth/verify-2fa` | Complete 2FA login |
| POST | `/auth/logout` | Logout (revoke refresh token) |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/forgot-password` | Request password reset |
| POST | `/auth/reset-password` | Reset password with token |
| POST | `/auth/change-password` | Change password (authenticated) |

### Profile
| Method | Path | Description |
|---|---|---|
| GET | `/profile/me` | Get own profile |
| PATCH | `/profile/me` | Update profile |
| POST | `/profile/avatar` | Upload avatar |
| POST | `/profile/change-email` | Request email change |
| GET | `/profile/verify-email-change` | Confirm email change |
| POST | `/profile/delete-account` | Request account deletion |
| GET | `/profile/cancel-delete` | Cancel account deletion |
| GET | `/profile/2fa/setup` | Get 2FA QR code |
| POST | `/profile/2fa/enable` | Enable 2FA |
| POST | `/profile/2fa/disable` | Disable 2FA |
| POST | `/profile/2fa/regenerate-codes` | Regenerate recovery codes |

### Notifications
| Method | Path | Description |
|---|---|---|
| GET | `/notifications/` | List notifications |
| GET | `/notifications/unread-count` | Get unread count |
| PATCH | `/notifications/{id}/read` | Mark one as read |
| PATCH | `/notifications/read-all` | Mark all as read |

### Admin (Superadmin only)
| Method | Path | Description |
|---|---|---|
| GET | `/users/` | List users (paginated, filterable) |
| GET | `/users/{id}` | Get user detail |
| POST | `/users/` | Create user |
| PATCH | `/users/{id}` | Update user |
| PATCH | `/users/{id}/status` | Change user status |
| DELETE | `/users/{id}` | Delete user |
| POST | `/admin/broadcast` | Send announcement to all users |

### WebSocket
```
ws://localhost:8000/ws/notifications?token=<access_token>
```

---

## Environment Variables

See [`.env.example`](.env.example) for full reference with descriptions.

---

## Makefile Commands

```bash
make help                # Show all commands
make dev                 # Start dev stack
make down                # Stop dev stack
make logs                # Tail all logs
make migrate             # Run Alembic migrations
make gen-key             # Generate TOTP_ENCRYPTION_KEY
make shell-be            # Shell into backend container
make shell-db            # Open psql
make mailhog             # Open MailHog UI
make minio               # Open MinIO console
make docs                # Open Swagger UI
make prod-traefik        # Start production stack with Traefik
make prod-traefik-down   # Stop Traefik production stack
make prod-traefik-logs   # Tail logs from Traefik production stack
```

---

## Production Deployment

### Option A — Simple (no reverse proxy)

1. Copy `.env.example` to `.env` and fill in all production values:
   - Strong `SECRET_KEY` and `TOTP_ENCRYPTION_KEY`
   - Real `DATABASE_URL`, `REDIS_URL`
   - Real email provider (`MAIL_PROVIDER=sendgrid` or `resend`)
   - Real S3 credentials (`STORAGE_BACKEND=s3`)
   - Set `APP_ENV=production` and `DEBUG=false`

2. Start the stack:
   ```bash
   docker compose up --build -d
   ```

3. Migrations run automatically on backend startup.

### Option B — With Traefik (recommended)

This option puts all services behind a shared Traefik reverse proxy that handles TLS termination via Let's Encrypt. Multiple apps can share the same Traefik instance on one server.

#### Prerequisites
- A domain pointing to your server
- The shared Traefik instance running (see `traefik/`)

#### 1. Start Traefik (once per server)

```bash
cd traefik/
cp .env.example .env          # set TRAEFIK_DOMAIN and ACME_EMAIL
docker compose up -d
cd ..
```

#### 2. Configure environment

```bash
# Backend secrets
cp backend/.env.example backend/.env
# Edit backend/.env — fill in SECRET_KEY, TOTP_ENCRYPTION_KEY, DATABASE_URL,
# REDIS_URL (use redis://:PASSWORD@redis:6379/0), email, S3, etc.

# Compose-level vars (domain + postgres/redis passwords)
cp .env.example .env.prod
# Edit .env.prod — at minimum set: DOMAIN, POSTGRES_PASSWORD, REDIS_PASSWORD
```

#### 3. Deploy

```bash
make prod-traefik
# or: docker compose -f docker-compose.prod.yml --env-file .env.prod up --build -d
```

#### 4. Access

| Service | URL |
|---|---|
| Frontend | `https://yourdomain.com` |
| API | `https://yourdomain.com/api/v1` |
| API docs | `https://yourdomain.com/api/v1/docs` |
| Traefik dashboard | `https://traefik.yourdomain.com` |

#### Teardown

```bash
make prod-traefik-down
```

---

## Role System

| Role | Access |
|---|---|
| `user` | Dashboard, profile, notifications |
| `superadmin` | All of the above + `/admin/*` user management |

The first superadmin must be set directly in the database:
```sql
UPDATE users SET role = 'superadmin' WHERE email = 'admin@example.com';
```
