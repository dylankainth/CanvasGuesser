pipeline {
    agent { docker { image 'python:3.7.2' } }
    stages {
        stage('build') {
            steps {
                sh 'pip3 install -r requirements.txt --user'
            }
        }
        stage('run') {
            steps {
                sh 'python /web/app.py'
            }
        }
    }
}
