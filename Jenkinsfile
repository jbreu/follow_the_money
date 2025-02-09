pipeline {
    agent any

    environment {
        DOCKER_IMAGE_NAME = 'follow-the-money'
        DOCKER_CONTAINER_NAME = 'follow-the-money-container'
    }

    stages {
        stage('Cleanup') {
            steps {
                script {
                    // Remove existing container if it exists
                    sh '''
                        if docker ps -a | grep -q ${DOCKER_CONTAINER_NAME}; then
                            docker rm -f ${DOCKER_CONTAINER_NAME}
                        fi
                    '''
                    // Remove existing image if it exists
                    sh '''
                        if docker images | grep -q ${DOCKER_IMAGE_NAME}; then
                            docker rmi -f ${DOCKER_IMAGE_NAME}
                        fi
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image
                    sh 'docker build -t ${DOCKER_IMAGE_NAME} .'
                }
            }
        }

        stage('Run Container') {
            steps {
                script {
                    // Run the container with the specified name
                    sh '''
                        docker run -d -p 5000:5000 \
                            --name ${DOCKER_CONTAINER_NAME} \
                            ${DOCKER_IMAGE_NAME}
                    '''
                }
            }
        }
    }

    post {
        failure {
            // Cleanup on failure
            sh '''
                docker rm -f ${DOCKER_CONTAINER_NAME} || true
                docker rmi -f ${DOCKER_IMAGE_NAME} || true
            '''
        }
    }
}