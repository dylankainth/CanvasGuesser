pipeline {
    agent { docker { image 'python:3.7.2' } }
    stages {
        stage('build') {
            steps {
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    sh 'pip3 install -r requirements.txt --user'
                }             
            }
        }
        stage('run') {
            steps {
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    sh 'python /web/app.py'
                }
            }
        }
    }
}