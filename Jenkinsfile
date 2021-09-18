pipeline {
    agent { docker { image 'python:3.7.2' } }
    stages {
        stage('build') {
            steps {
                sh 'pip install flask'
            }
        }
        stage('run') {
            steps {
                sh 'python /web/app.py'
            }
        }
    }
}
