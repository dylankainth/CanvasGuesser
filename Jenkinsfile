pipeline {
    stages {
        stage('run') {
            steps {
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    sh 'python /web/app.py'
                }
            }
        }
    }
}
