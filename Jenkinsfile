pipeline {
    stages {
        stage('Build Docker') {
            // build the docker image from the source code using the BUILD_ID parameter in image name
                sh "sudo docker build -t flask-app -f web/dockerfile ."
        }
        stage("run docker container"){
                sh "sudo docker run -p 5001:5001 --name flask-app -d flask-app "
        }
    }
}
