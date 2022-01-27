pipeline {
  agent { label 'linux' }
  options {
    buildDiscarder(logRotator(numToKeepStr: '5'))
  }
  environment {
    DOCKERHUB_CREDENTIALS = credentials('vishblip93-dockerhub')
  }
  stages {
    stage('Build') {
      steps {
        sh 'docker build -t vishblip93/baywa:latest .'
      }
    }
    stage('Login') {
      steps {
        sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
      }
    }
    stage('Push') {
      steps {
        sh 'docker push vishblip93/baywa:latest'
      }
    }
  }
  post {
    always {
      sh 'docker logout'
    }
  }
}