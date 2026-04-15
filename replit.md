# Workspace

## Overview

Django 4.2 airline management and reservation mini-project for a lab demo. The Django app is the primary user-facing project and runs from `manage.py` on port 5000 in Replit.

## Django Airline System

- **Project**: `airline_manager`
- **Apps**:
  - `accounts` — Login/logout, sample user/admin accounts, passenger records, My Bookings
  - `flights` — City, aircraft, route, schedule, flight search, dashboard and admin-only Control Tower data entry
  - `seats` — Seat map and cabin pricing modifiers
  - `bookings` — Reservations, coupons, payments, dynamic pricing signals
  - `tracking` — Live C&D/check-in/gate event log and Aviationstack redirect fallback for flight-number lookup when `AVIATIONSTACK_ACCESS_KEY` is configured
  - `agents` — Staff/agent-assisted bookings
  - `chatbot` — Database-backed FAQ entries, chat messages, and chatbot quick ticket booking
  - `delays` — Admin delay alerts and passenger accommodation support
- **Database**: SQLite by default (`db.sqlite3`, generated locally); settings include environment hooks for PostgreSQL-style DB variables.
- **Async stack**: Celery configured in `airline_manager/celery.py` with Redis URL support through `REDIS_URL`; eager execution is enabled by default for the lab preview so the app works without a separate worker.
- **Demo logins**:
  - Sample passenger: `sample_user` / `user12345`
  - Admin: `admin` / `admin12345`
- **Key features**:
  - Flight listing and city/route search
  - User login and personal My Bookings page
  - Admin-only Control Tower at `/control-tower/` for adding cities, coupons, flights with generated seat maps, sample bookings, and delay messages
  - Dynamic fare calculation through booking signals
  - Visual seat selection with economy, premium, and business pricing
  - Passenger and agent-assisted booking flows
  - Chatbot ticket booking that creates a real PNR
  - PNR-based live tracking for flight status, check-in, and document/C&D checks
  - Delay communication from admin shown in My Bookings and Live Tracking
  - Coupon chatbot using database FAQ rows and stored chat messages
  - Custom Django admin labels and registered model admin panels
- **Seed data**: `flights.seed.ensure_seed_data()` creates users, cities, aircraft, routes, seats, coupons, agents, FAQ entries, delay alerts, and sample bookings. It is called from the main views so the lab demo stays populated.

## Key Commands

- `python manage.py makemigrations` — create Django migrations
- `python manage.py migrate` — apply database migrations
- `python manage.py migrate && python manage.py runserver 0.0.0.0:5000` — run the Django app in Replit
- `python manage.py runserver 127.0.0.1:8080` — recommended local Windows command if port 8000 is blocked
- `python manage.py createsuperuser` — optional Django admin user

## Original Workspace Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Original Workspace Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally
