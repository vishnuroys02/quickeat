pipeline {
  agent any
  environment {
    AWS_REGION      = 'ap-south-1'
    AWS_ACCOUNT_ID  = credentials('aws-account-id')
    BACKEND_REPO    = 'quickeats-backend'
    FRONTEND_REPO   = 'quickeats-frontend'
    IMAGE_TAG       = "${BUILD_NUMBER}"
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Backend Test') {
      steps {
        sh '''
          python3 -m venv .ci-venv
          . .ci-venv/bin/activate
          pip install -r backend/requirements.txt
          pytest -q backend/test_app.py
        '''
      }
    }

    stage('Frontend Build') {
      steps { sh 'cd frontend && npm ci && npm run build' }
    }

    stage('Docker Build') {
      steps {
        sh '''
          docker build -t ${BACKEND_REPO}:${IMAGE_TAG} ./backend
          docker build -t ${FRONTEND_REPO}:${IMAGE_TAG} ./frontend
        '''
      }
    }

    stage('ECR Push') {
      when { branch 'main' }
      steps {
        withCredentials([[$class:'AmazonWebServicesCredentialsBinding',
          credentialsId:'aws-jenkins',
          accessKeyVariable:'AWS_ACCESS_KEY_ID',
          secretKeyVariable:'AWS_SECRET_ACCESS_KEY']]) {
          sh '''
            aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

            docker tag ${BACKEND_REPO}:${IMAGE_TAG} ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${BACKEND_REPO}:${IMAGE_TAG}
            docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${BACKEND_REPO}:${IMAGE_TAG}

            docker tag ${FRONTEND_REPO}:${IMAGE_TAG} ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${FRONTEND_REPO}:${IMAGE_TAG}
            docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${FRONTEND_REPO}:${IMAGE_TAG}
          '''
        }
      }
    }

    stage('Deploy to ECS') {
      when { branch 'main' }
      steps {
        withCredentials([[$class:'AmazonWebServicesCredentialsBinding',
          credentialsId:'aws-jenkins',
          accessKeyVariable:'AWS_ACCESS_KEY_ID',
          secretKeyVariable:'AWS_SECRET_ACCESS_KEY']]) {
          sh '''
            aws ecs update-service \
              --cluster quickeats-cluster \
              --service quickeats-backend-service \
              --force-new-deployment \
              --region ${AWS_REGION}

            aws ecs update-service \
              --cluster quickeats-cluster \
              --service quickeats-frontend-service \
              --force-new-deployment \
              --region ${AWS_REGION}
          '''
        }
      }
    }
  }
  post {
    always { sh 'rm -rf .ci-venv || true' }
  }
}
