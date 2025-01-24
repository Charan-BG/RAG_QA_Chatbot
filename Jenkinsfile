pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "troopsassemble3002/rag-conversational-qa-chatbot" // Update with your Docker Hub username
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

        //stage('Run Tests') {
          //  steps {
            //    bat 'pytest' // Add test cases in your repository
            //}
        //}

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t ${DOCKER_IMAGE}:latest .'
            }
        }

        stage('Push to Docker Registry') {
            steps {
                withDockerRegistry([credentialsId: "${DOCKER_REGISTRY_CREDENTIALS}", url: '']) {
                    bat 'docker push ${DOCKER_IMAGE}:latest'
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
