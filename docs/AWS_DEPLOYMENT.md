# AWS Deployment Runbook

1. Create VPC across two Availability Zones.
2. Public subnets for ALB.
3. Private subnets for ECS/Fargate.
4. Private DB subnets for RDS PostgreSQL.
5. Create ECR repository `quickeats-backend`.
6. Build/tag/push backend image.
7. Create RDS PostgreSQL.
8. Create ECS cluster, task definition and service.
9. Put ECS service behind ALB target group.
10. Health check `/health`.
11. Host React build using S3/CloudFront or a frontend container.
12. Configure frontend API URL.
13. Test login, food listing, order, cancellation and admin CRUD.
14. Check CloudWatch logs, ECS events and ALB target health.

Do not hard-code credentials. Use IAM/Jenkins credentials/secret storage.
After testing, stop resources as instructed for review; do not terminate resources that must remain for review.
