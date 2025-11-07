pipeline {
    agent any

    environment {
        PYTHON = 'python'
    }

    triggers {
        // Run every 24 hours
        cron('H H * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set up Python environment') {
            steps {
                // Use Windows-friendly commands if Jenkins is running on Windows
                bat '''
                python -m venv venv
                call venv\\Scripts\\activate
                pip install --upgrade pip
                pip install -r requirements.txt || echo requirements.txt not found, skipping.
                '''
            }
        }

        stage('Run Twitch Scraper') {
            steps {
                bat '''
                chcp 65001 >NUL
                call venv\\Scripts\\activate
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
            echo 'Job failed — skipping email notification because SMTP not configured.'
        }
    }
}
