# Workspace

## Overview

Django 4.2 airline management and reservation mini-project for a lab demo, alongside the original pnpm workspace scaffolding. The Django app is the primary user-facing project and runs from `manage.py` on port 5000.

## Django Airline System

- **Project**: `airline_manager`
- **Apps**:
  - `accounts` — Passenger/user records
  - `flights` — Aircraft, routes, schedules, flight search, dashboard seed data
  - `seats` — Seat map and cabin pricing modifiers
  - `bookings` — Reservations, coupons, payments, dynamic pricing signals
  - `tracking` — Live C&D/check-in/gate event log
  - `agents` — Staff/agent-assisted bookings
  - `chatbot` — Database-backed FAQ entries and chat messages
  - `delays` — Delay alerts and accommodation support
- **Database**: SQLite by default (`db.sqlite3`, generated locally); settings include environment hooks for PostgreSQL-style DB variables.
- **Async stack**: Celery configured in `airline_manager/celery.py` with Redis URL support through `REDIS_URL`; eager execution is enabled by default for the lab preview so the app works without a separate worker.
- **Key features**:
  - Flight listing and search
  - Operations dashboard
  - Dynamic fare calculation through booking signals
  - Visual seat selection with economy, premium, and business pricing
  - Passenger and agent-assisted booking flows
  - PNR-based live tracking for flight status, check-in, and document/C&D checks
  - Delay accommodation alerts for meal, hotel, and rebooking support
  - Coupon chatbot using database FAQ rows and stored chat messages
  - Custom Django admin labels and registered model admin panels

## Key Commands

- `python manage.py makemigrations` — create Django migrations
- `python manage.py migrate` — apply database migrations
- `python manage.py migrate && python manage.py runserver 0.0.0.0:5000` — run the Django app
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
