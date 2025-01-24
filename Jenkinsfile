pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "troopsassemble3002/rag-conversational-qa-chatbot" // Docker Hub username and image name
        DOCKER_REGISTRY_CREDENTIALS = 'docker_hub_credentials' // Jenkins credential ID
        GITHUB_REPO = "https://github.com/Charan-BG/RAG_QA_Chatbot.git"
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: "${env.GITHUB_REPO}"
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Build Docker Image') {
            steps {
                // Pass the environment variable explicitly in the bat command
                bat """
                SETLOCAL ENABLEDELAYEDEXPANSION
                docker build -t %DOCKER_IMAGE%:latest .
                ENDLOCAL
                """
            }
        }

        stage('Push to Docker Registry') {
            steps {
                withDockerRegistry([credentialsId: "${DOCKER_REGISTRY_CREDENTIALS}", url: '']) {
                    // Pass the environment variable explicitly in the bat command
                    bat """
                    SETLOCAL ENABLEDELAYEDEXPANSION
                    docker push %DOCKER_IMAGE%:latest
                    ENDLOCAL
                    """
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
