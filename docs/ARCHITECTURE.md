# QuickEats 3-Tier Architecture

Presentation Tier: React + Nginx (or S3 + CloudFront)
Application Tier: ALB -> ECS/Fargate -> Flask API
Database Tier: RDS PostgreSQL

VPC:
- Public subnets: ALB
- Private application subnets: ECS/Fargate
- Private database subnets: RDS

Flow:
User -> Presentation -> ALB -> Flask -> RDS -> Flask -> Presentation -> User

Security:
Internet -> ALB 80/443
ALB SG -> Backend SG on application port
Backend SG -> RDS SG on 5432
