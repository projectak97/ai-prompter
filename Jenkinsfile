pipeline {
    agent any
    
    environment {
        // AWS Configuration
        AWS_DEFAULT_REGION = 'us-east-1'  // Change to your preferred region
        AWS_ACCOUNT_ID = '123456789012'   // Replace with your AWS Account ID
        ECR_REPOSITORY = 'ai-prompt-generator'
        IMAGE_TAG = "${BUILD_NUMBER}"
        IMAGE_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPOSITORY}"
        
        // Application Configuration
        APP_NAME = 'ai-prompt-generator'
        DOCKERFILE_PATH = '.'
        
        // Credentials - Using separate secret text credentials
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        DEEPSEEK_API_KEY = credentials('deepseek-api-key')
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
                
                script {
                    // Get git commit info
                    env.GIT_COMMIT_SHORT = sh(
                        script: "git rev-parse --short HEAD",
                        returnStdout: true
                    ).trim()
                    env.GIT_BRANCH = sh(
                        script: "git rev-parse --abbrev-ref HEAD",
                        returnStdout: true
                    ).trim()
                }
            }
        }
        
        stage('Build Info') {
            steps {
                echo "Building ${APP_NAME}"
                echo "Branch: ${env.GIT_BRANCH}"
                echo "Commit: ${env.GIT_COMMIT_SHORT}"
                echo "Build Number: ${BUILD_NUMBER}"
                echo "Image URI: ${IMAGE_URI}:${IMAGE_TAG}"
                echo "AWS Region: ${AWS_DEFAULT_REGION}"
            }
        }
        
        
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    try {
                        // Build the Docker image
                        def dockerImage = docker.build(
                            "${IMAGE_URI}:${IMAGE_TAG}",
                            "--no-cache --build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ') --build-arg BUILD_VERSION=${BUILD_NUMBER} --build-arg GIT_COMMIT=${env.GIT_COMMIT_SHORT} ${DOCKERFILE_PATH}"
                        )
                        
                        // Tag with latest
                        dockerImage.tag('latest')
                        
                        echo 'Docker image built successfully ✓'
                        
                        // Store image for later stages
                        env.DOCKER_IMAGE_ID = dockerImage.id
                        
                    } catch (Exception e) {
                        error("Docker build failed: ${e.getMessage()}")
                    }
                }
            }
        }
        
        
        
        stage('Configure AWS CLI') {
            steps {
                echo 'Configuring AWS CLI...'
                script {
                    try {
                        // Configure AWS CLI with credentials
                        sh """
                            # Configure AWS credentials
                            aws configure set aws_access_key_id ${AWS_ACCESS_KEY_ID}
                            aws configure set aws_secret_access_key ${AWS_SECRET_ACCESS_KEY}
                            aws configure set default.region ${AWS_DEFAULT_REGION}
                            aws configure set default.output json
                            
                            # Verify AWS CLI configuration
                            echo 'Testing AWS CLI configuration...'
                            aws sts get-caller-identity
                        """
                        echo 'AWS CLI configured successfully ✓'
                    } catch (Exception e) {
                        error("AWS CLI configuration failed: ${e.getMessage()}")
                    }
                }
            }
        }
        
        stage('AWS ECR Login') {
            steps {
                echo 'Logging in to AWS ECR...'
                script {
                    try {
                        // Login to ECR using AWS CLI
                        sh """
                            # Get ECR login token and login to Docker
                            aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | \
                            docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com
                        """
                        echo 'ECR login successful ✓'
                    } catch (Exception e) {
                        error("ECR login failed: ${e.getMessage()}")
                    }
                }
            }
        }
        
        stage('Create ECR Repository') {
            steps {
                echo 'Ensuring ECR repository exists...'
                script {
                    try {
                        // Check if repository exists, create if it doesn't
                        def repoExists = sh(
                            script: "aws ecr describe-repositories --repository-names ${ECR_REPOSITORY} --region ${AWS_DEFAULT_REGION}",
                            returnStatus: true
                        )
                        
                        if (repoExists != 0) {
                            echo 'Creating ECR repository...'
                            sh """
                                aws ecr create-repository \
                                    --repository-name ${ECR_REPOSITORY} \
                                    --region ${AWS_DEFAULT_REGION} \
                                    --image-scanning-configuration scanOnPush=true \
                                    --encryption-configuration encryptionType=AES256
                            """
                            echo 'ECR repository created ✓'
                        } else {
                            echo 'ECR repository already exists ✓'
                        }
                        
                        // Set lifecycle policy to manage image retention
                        sh """
                            aws ecr put-lifecycle-configuration \
                                --repository-name ${ECR_REPOSITORY} \
                                --region ${AWS_DEFAULT_REGION} \
                                --lifecycle-policy-text '{
                                    "rules": [
                                        {
                                            "rulePriority": 1,
                                            "description": "Keep last 10 images",
                                            "selection": {
                                                "tagStatus": "any",
                                                "countType": "imageCountMoreThan",
                                                "countNumber": 10
                                            },
                                            "action": {
                                                "type": "expire"
                                            }
                                        }
                                    ]
                                }' || true
                        """
                        
                    } catch (Exception e) {
                        error("ECR repository setup failed: ${e.getMessage()}")
                    }
                }
            }
        }
        
        stage('Push to ECR') {
            steps {
                echo 'Pushing Docker image to ECR...'
                script {
                    try {
                        // Push with build number tag
                        sh "docker push ${IMAGE_URI}:${IMAGE_TAG}"
                        echo "Pushed ${IMAGE_URI}:${IMAGE_TAG} ✓"
                        
                        // Push latest tag
                        sh "docker tag ${IMAGE_URI}:${IMAGE_TAG} ${IMAGE_URI}:latest"
                        sh "docker push ${IMAGE_URI}:latest"
                        echo "Pushed ${IMAGE_URI}:latest ✓"
                        
                        // Tag with git commit
                        sh "docker tag ${IMAGE_URI}:${IMAGE_TAG} ${IMAGE_URI}:${env.GIT_COMMIT_SHORT}"
                        sh "docker push ${IMAGE_URI}:${env.GIT_COMMIT_SHORT}"
                        echo "Pushed ${IMAGE_URI}:${env.GIT_COMMIT_SHORT} ✓"
                        
                        // Tag with branch name (if not main/master)
                        if (env.GIT_BRANCH != 'main' && env.GIT_BRANCH != 'master') {
                            def safeBranchName = env.GIT_BRANCH.replaceAll(/[^a-zA-Z0-9._-]/, '-')
                            sh "docker tag ${IMAGE_URI}:${IMAGE_TAG} ${IMAGE_URI}:${safeBranchName}"
                            sh "docker push ${IMAGE_URI}:${safeBranchName}"
                            echo "Pushed ${IMAGE_URI}:${safeBranchName} ✓"
                        }
                        
                    } catch (Exception e) {
                        error("ECR push failed: ${e.getMessage()}")
                    }
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                echo 'Running security scan on ECR image...'
                script {
                    try {
                        // Trigger ECR vulnerability scan
                        sh """
                            aws ecr start-image-scan \
                                --repository-name ${ECR_REPOSITORY} \
                                --image-id imageTag=${IMAGE_TAG} \
                                --region ${AWS_DEFAULT_REGION} || true
                        """
                        
                        echo 'Security scan initiated ✓'
                        echo 'Check ECR console for scan results'
                        
                        // Wait a bit and try to get scan results
                        sh """
                            echo 'Waiting for scan to complete...'
                            sleep 30
                            aws ecr describe-image-scan-findings \
                                --repository-name ${ECR_REPOSITORY} \
                                --image-id imageTag=${IMAGE_TAG} \
                                --region ${AWS_DEFAULT_REGION} || echo 'Scan still in progress'
                        """
                        
                    } catch (Exception e) {
                        echo "Security scan warning: ${e.getMessage()}"
                        // Don't fail the pipeline for scan issues
                    }
                }
            }
        }
        
        stage('Cleanup Local Images') {
            steps {
                echo 'Cleaning up local Docker images...'
                script {
                    try {
                        // Remove local images to save space
                        sh """
                            docker rmi ${IMAGE_URI}:${IMAGE_TAG} || true
                            docker rmi ${IMAGE_URI}:latest || true
                            docker rmi ${IMAGE_URI}:${env.GIT_COMMIT_SHORT} || true
                            docker system prune -f || true
                        """
                        echo 'Local cleanup completed ✓'
                    } catch (Exception e) {
                        echo "Cleanup warning: ${e.getMessage()}"
                        // Don't fail pipeline for cleanup issues
                    }
                }
            }
        }
        
        stage('Generate Deployment Info') {
            steps {
                echo 'Generating deployment information...'
                script {
                    // Create deployment info file
                    writeFile file: 'deployment-info.json', text: """
{
    "build_number": "${BUILD_NUMBER}",
    "git_commit": "${env.GIT_COMMIT_SHORT}",
    "git_branch": "${env.GIT_BRANCH}",
    "image_uri": "${IMAGE_URI}:${IMAGE_TAG}",
    "image_latest": "${IMAGE_URI}:latest",
    "build_date": "${new Date()}",
    "aws_region": "${AWS_DEFAULT_REGION}",
    "ecr_repository": "${ECR_REPOSITORY}",
    "deployment_command": "docker run -d --name ai-prompt-generator -p 8501:8501 -e DEEPSEEK_API_KEY=your-api-key ${IMAGE_URI}:${IMAGE_TAG}"
}
"""
                    
                    // Archive the deployment info
                    archiveArtifacts artifacts: 'deployment-info.json', fingerprint: true
                    
                    echo 'Deployment information generated ✓'
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed'
            // Clean up any remaining test containers
            sh "docker stop test-${BUILD_NUMBER} || true"
            sh "docker rm test-${BUILD_NUMBER} || true"
            
            // Clean up AWS credentials from local config
            sh """
                rm -f ~/.aws/credentials || true
                rm -f ~/.aws/config || true
            """
        }
        
        success {
            echo '🎉 Pipeline succeeded!'
            echo "✅ Image pushed to ECR: ${IMAGE_URI}:${IMAGE_TAG}"
            echo "✅ Latest tag: ${IMAGE_URI}:latest"
            echo "✅ Git commit tag: ${IMAGE_URI}:${env.GIT_COMMIT_SHORT}"
            echo ""
            echo "🚀 Deployment Command:"
            echo "docker run -d --name ai-prompt-generator -p 8501:8501 -e DEEPSEEK_API_KEY=your-api-key ${IMAGE_URI}:${IMAGE_TAG}"
            echo ""
            echo "📊 AWS ECR Console: https://${AWS_DEFAULT_REGION}.console.aws.amazon.com/ecr/repositories/${ECR_REPOSITORY}"
            
            // Send success notification (optional)
            // slackSend(
            //     color: 'good',
            //     message: "✅ ${APP_NAME} build ${BUILD_NUMBER} succeeded!\nImage: ${IMAGE_URI}:${IMAGE_TAG}"
            // )
        }
        
        failure {
            echo '❌ Pipeline failed!'
            echo "Branch: ${env.GIT_BRANCH}"
            echo "Commit: ${env.GIT_COMMIT_SHORT}"
            
            // Send failure notification (optional)
            // slackSend(
            //     color: 'danger',
            //     message: "❌ ${APP_NAME} build ${BUILD_NUMBER} failed!\nBranch: ${env.GIT_BRANCH}\nCommit: ${env.GIT_COMMIT_SHORT}"
            // )
        }
        
        unstable {
            echo '⚠️ Pipeline unstable!'
        }
    }
}