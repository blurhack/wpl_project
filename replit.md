# Workspace

## Overview

Django airline management and reservation mini-project for a lab demo, alongside the original pnpm workspace scaffolding. The Django app is the primary user-facing project and runs from `manage.py` on port 5000.

## Django Airline System

- **Project**: `airline_manager`
- **App**: `reservations`
- **Database**: SQLite (`db.sqlite3`, generated locally)
- **Key features**:
  - Flight listing and search
  - Dynamic fare calculation based on demand and departure time
  - Visual seat selection with economy, premium, and business pricing
  - Passenger and agent-assisted booking flows
  - PNR-based live tracking for flight status, check-in, and document checks
  - Delay accommodation messaging for meal, hotel, and rebooking support
  - Coupon chatbot with rule-based responses

## Key Commands

- `python manage.py makemigrations reservations` — create Django migrations
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
