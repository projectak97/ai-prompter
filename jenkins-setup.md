# Jenkins ECR Pipeline Setup Guide

## Prerequisites

### 1. AWS Configuration
- AWS Account with ECR access
- IAM user with appropriate permissions
- AWS CLI configured

### 2. Jenkins Plugins Required
Install these plugins in Jenkins:
- AWS Steps Plugin
- Docker Pipeline Plugin
- Pipeline Plugin
- Git Plugin
- Credentials Plugin

## Setup Steps

### 1. Configure AWS Credentials in Jenkins

1. Go to `Jenkins → Manage Jenkins → Manage Credentials`
2. Add new credentials:
   - **Kind**: AWS Credentials
   - **ID**: `aws-ecr-credentials`
   - **Access Key ID**: Your AWS Access Key
   - **Secret Access Key**: Your AWS Secret Key

### 2. Configure DeepSeek API Key

1. In Jenkins Credentials, add:
   - **Kind**: Secret text
   - **ID**: `deepseek-api-key`
   - **Secret**: Your DeepSeek API Key

### 3. Update Jenkinsfile Variables

Edit the Jenkinsfile and update:

```groovy
environment {
    AWS_DEFAULT_REGION = 'your-aws-region'     // e.g., 'us-east-1'
    AWS_ACCOUNT_ID = 'your-aws-account-id'     // e.g., '123456789012'
    ECR_REPOSITORY = 'ai-prompt-generator'     // Your desired repo name
}
```

### 4. Required IAM Permissions

Your AWS user needs these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:CreateRepository",
                "ecr:DescribeRepositories",
                "ecr:StartImageScan",
                "ecr:DescribeImageScanFindings"
            ],
            "Resource": "*"
        }
    ]
}
```

### 5. Create Jenkins Pipeline Job

1. Create new Pipeline job in Jenkins
2. Configure Pipeline script from SCM
3. Point to your Git repository
4. Set Script Path to `Jenkinsfile`

## Pipeline Features

### 🔄 **Build Process**
- Validates environment and required files
- Builds Docker image with multiple tags
- Tests image functionality
- Pushes to AWS ECR

### 🏷️ **Image Tagging Strategy**
- `${BUILD_NUMBER}` - Unique build identifier
- `latest` - Most recent successful build
- `${GIT_COMMIT_SHORT}` - Git commit reference

### 🔒 **Security Features**
- ECR vulnerability scanning
- Credential management
- Image testing before push

### 📊 **Monitoring**
- Build notifications
- Detailed logging
- Pipeline status tracking

## Usage

### Automatic Builds
- Trigger on Git push (configure webhook)
- Scheduled builds (configure cron)
- Manual builds via Jenkins UI

### Manual Deployment
```bash
# Pull and run the image
docker pull ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/ai-prompt-generator:latest

docker run -d \
  --name ai-prompt-generator \
  -p 8501:8501 \
  -e DEEPSEEK_API_KEY="your-api-key" \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/ai-prompt-generator:latest
```

## Troubleshooting

### Common Issues

1. **ECR Login Failed**
   - Check AWS credentials
   - Verify IAM permissions
   - Ensure correct region

2. **Docker Build Failed**
   - Check Dockerfile syntax
   - Verify base image availability
   - Review build logs

3. **Push Failed**
   - Check ECR repository exists
   - Verify push permissions
   - Check image size limits

### Debugging
```bash
# Check Jenkins logs
docker logs jenkins

# Verify AWS CLI access
aws ecr describe-repositories --region us-east-1

# Test Docker build locally
docker build -t test-image .
```

## Advanced Configuration

### Multi-Environment Support
Add environment-specific stages:

```groovy
stage('Deploy to Dev') {
    when { branch 'develop' }
    steps {
        // Deploy to development environment
    }
}

stage('Deploy to Prod') {
    when { branch 'main' }
    steps {
        // Deploy to production environment
    }
}
```

### Notification Setup
Configure Slack/email notifications in the `post` section.

### Parallel Builds
Add parallel testing for multiple environments.