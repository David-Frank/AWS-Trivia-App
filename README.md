# AWS-Trivia-App

         ___        ______     ____ _                 _  ___  
        / \ \      / / ___|   / ___| | ___  _   _  __| |/ _ \ 
       / _ \ \ /\ / /\___ \  | |   | |/ _ \| | | |/ _` | (_) |
      / ___ \ V  V /  ___) | | |___| | (_) | |_| | (_| |\__, |
     /_/   \_\_/\_/  |____/   \____|_|\___/ \__,_|\__,_|  /_/ 
 ----------------------------------------------------------------- 
 
Deploying The Application:

I started by creating an AWS Cloud9 environment for my development environment. In this environment, I downloaded and extracted the source code that I used to deploy the front-end and back-end of a serverless application. 

I deployed the application’s backend infrastructure by using the AWS Serverless Application Model Command Line Interface (AWS SAM CLI). I also used AWS SAM to create all the resources that host the backend of the application: an Amazon API Gateway gateway, AWS Lambda functions, an Amazon DynamoDB table, and an AWS Step Functions state machine. 

I also deployed the application frontend: a React web application that’s hosted on an S3 bucket, which acts as the web server. After the application was up and running, I put the application under source control by using AWS CodeCommit.



Testing the Application:

The local build contains linting (or static analysis) of the code and unit tests. Next, I ran an integration test. 

The integration test finds the API Gateway Websocket endpoint, and it simulates a player completing a game. I then added a simple feature to the code. Finally, I fixed the unit tests and committed the changes to this repository.

