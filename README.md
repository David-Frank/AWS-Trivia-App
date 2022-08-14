# AWS-Trivia-App

         ___        ______     ____ _                 _  ___  
        / \ \      / / ___|   / ___| | ___  _   _  __| |/ _ \ 
       / _ \ \ /\ / /\___ \  | |   | |/ _ \| | | |/ _` | (_) |
      / ___ \ V  V /  ___) | | |___| | (_) | |_| | (_| |\__, |
     /_/   \_\_/\_/  |____/   \____|_|\___/ \__,_|\__,_|  /_/ 
 ----------------------------------------------------------------- 
 
--Deploying The Application:

I started by creating an AWS Cloud9 environment for my development environment. In this environment, I downloaded and extracted the source code that I used to deploy the front-end and back-end of a serverless application. 

I deployed the application’s backend infrastructure by using the AWS Serverless Application Model Command Line Interface (AWS SAM CLI). I also used AWS SAM to create all the resources that host the backend of the application: an Amazon API Gateway gateway, AWS Lambda functions, an Amazon DynamoDB table, and an AWS Step Functions state machine. 

I also deployed the application frontend: a React web application that’s hosted on an S3 bucket, which acts as the web server. After the application was up and running, I put the application under source control by using AWS CodeCommit.



--Testing the Application:

The local build contains linting (or static analysis) of the code and unit tests. Next, I ran an integration test. 

The integration test (The integration test uses the AWS SAM stack to find the Websocket endpoint, so the stack is passed in the AWS_SAM_STACK_NAME environment variable) finds the API Gateway Websocket endpoint, and it simulates a player completing a game. Then I added a simple feature to the code. Finally, I fixed the unit tests and committed the changes to this repository.



--Using AWS CodeBuild to Test the Application Once More:

I began by updating the application with a buildspec file, and using CodeBuild to test the application. 

The buildspec file contains the same tests I performed with the local build: linting with pylint, and unit tests with pytest. I also used CodeBuild to run the unit tests against the application, and then I viewed the log output.
