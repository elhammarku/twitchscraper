pipeline {
    agent any

    environment {
        PYTHON = 'python3'
    }

    triggers {
        // Schedule job to run once every 24 hours
        cron('H H * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                // Pull the Twitch scraper code from source control
                checkout scm
            }
        }

        stage('Set up Python environment') {
            steps {
                sh '''
                python -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Twitch Scraper') {
            steps {
                sh '''
                . venv/bin/activate
                python twitch_scraper_fixed.py
                '''
            }
        }

        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: '*_twitch_combined_data.csv', fingerprint: true
            }
        }
    }

    post {
        failure {
            mail to: 'your_email@example.com', subject: 'Twitch Scraper Job Failed', body: 'The Jenkins job for Twitch Scraper has failed. Please check logs.'
        }
    }
}
