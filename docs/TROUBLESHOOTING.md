# Troubleshooting

Docker:
```bash
docker compose ps
docker compose logs backend
docker compose logs frontend
docker compose logs db
docker inspect <container>
```

Database:
```bash
docker exec -it quickeats-db pg_isready -U quickeats -d quickeats
```

Backend:
```bash
curl http://localhost:5000/health
```

Jenkins:
- Check Console Output
- Git checkout
- Python/npm dependencies
- Docker daemon access
- AWS credentials
- ECR repository and image tag
- ECS service events

AWS:
- ECS task stopped reason
- CloudWatch logs
- ALB target health
- Security groups
- RDS connectivity
- ECR image/tag
- IAM permissions
