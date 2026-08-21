# QuickEats - 3 Tier DevOps Project

Database-driven food ordering application for AWS/DevOps readiness.

## Architecture
Presentation: React + Nginx
Application: Flask REST API
Database: PostgreSQL

## DevOps flow
GitHub -> Jenkins -> Test -> Docker Build -> ECR -> ECS/Fargate -> ALB -> RDS PostgreSQL

## Local
Prerequisites: Docker Desktop + Git

Run:
```bash
docker compose up --build
```
Frontend: http://localhost:5173
Backend health: http://localhost:5000/health

Stop:
```bash
docker compose down
```

Demo admin:
admin@quickeats.local / admin123

## Git workflow
Recommended: main, develop, feature/*
```bash
git checkout -b feature/order-status
git add .
git commit -m "Add order status management"
git push -u origin feature/order-status
```
Use Pull Requests and review before merging.

## Review
See docs/REVIEW_CHECKLIST.md, docs/ARCHITECTURE.md, docs/TROUBLESHOOTING.md and docs/DEMO_FLOW.md.
