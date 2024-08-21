## Fluent-Bit for ECS Instance Logs Collection

The sample ECS task definition in this folder deploys Fluent-Bit as a DaemonService.

* [fluent-bit-ecs-instance-logs.json](fluent-bit-ecs-instance-logs.json): sample ECS task definition
* [fluent-bit.conf](fluent-bit.conf): sample fluent-bit configuration
* [parsers.conf](parsers.conf): sample fluent-bit parsers file

You must replace all the placeholders (with ```{{ }}```) in the above task definitions with your information:
* ```{{task-role-arn}}```: ECS task role ARN.
  * This is role that you application containers will use. The permission should be whatever your applications need.
  * Ensure that your Task role has the below permissions attached in order to access CloudWatch (for log ingestion) and SSM parameters (for the Fluent-Bit configuration).
  ```
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Action": [
                  "logs:CreateLogStream",
                  "logs:CreateLogGroup",
                  "logs:PutLogEvents"
              ],
              "Resource": "*",
              "Effect": "Allow",
              "Sid": "FluentBitLogs"
          },
          {
              "Action": [
                  "ssm:GetParameters",
                  "ssm:GetParameter"
              ],
              "Resource": [
                  "arn:aws:ssm:{{region}}:{{account-id}}:parameter/*"
              ],
              "Effect": "Allow",
              "Sid": "FluentBitSSMParameterAccess"
          }
      ]
  }
  ```
  
* ```{{execution-role-arn}}```: ECS task execution role ARN.
  * This is the role that Amazon ECS requires to launch/execute your containers, e.g. get the parameters from SSM parameter store.
  * Ensure that the ```AmazonSSMReadOnlyAccess```, ```AmazonECSTaskExecutionRolePolicy``` and ```CloudWatchAgentServerPolicy``` policies are attached to your ECS Task execution role.
  * If you would like to store more sensitive data for ECS to use, refer to https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data.html.    

* ```{{aws-region}}```: The AWS region where the ECS Daemonset will be deployed: e.g. ```us-west-2```

* ```{{fluent-bit-config-ssm-parameter-name}}```: The name of the SSM parameter used to store the Fluent-Bit configuration. [fluent-bit.conf](fluent-bit.conf) contains a sample configuration from which you can create an SSM parameter.

* ```{{fluent-bit-parser-ssm-parameter-name}}```: The name of the SSM parameter used to store the Fluent-Bit parsers. [parsers.conf](parsers.conf) contains a sample fluent-bit parser configuration from which you can create an SSM parameter.
  
* ```{{ecs-cluster-name}}```: The name of the ECS cluster in which you are deploying the Fluent-Bit Daemonset.


You can also adjust the resource limit (e.g. cpu and memory) based on your particular use cases.