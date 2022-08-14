# AWS-Trivia-App

I started by creating an AWS Cloud9 environment for my development environment. In this environment, I downloaded and extract the source code that I used to deploy the front-end and back-end of a server less application. 

I deployed the application’s backend infrastructure by using the AWS Serverless Application Model Command Line Interface (AWS SAM CLI). I also used AWS SAM to create all the resources that host the backend of the application: an Amazon API Gateway gateway, AWS Lambda functions, an Amazon DynamoDB table, and an AWS Step Functions state machine. 

I also deployed the application frontend: a React web application that’s hosted on an S3 bucket, which acts as the web server. After the application was up and running, I put the application under source control by using AWS CodeCommit.
