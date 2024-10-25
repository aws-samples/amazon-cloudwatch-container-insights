## Fluent-Bit for ECS Instance Logs Collection

The sample ECS task definition in this folder deploys Fluent-Bit as a DaemonService.

* [fluent-bit-ecs-instance-logs.json](fluent-bit-ecs-instance-logs.json): sample ECS task definition
* [fluent-bit.conf](fluent-bit.conf): default fluent-bit configuration
* [parsers.conf](parsers.conf): default fluent-bit parsers file

You must replace all the placeholders (with ```{{ }}```) in the above task definitions with your information:
* ```{{task-role-arn}}```: ECS task role ARN.
  * This is role that you application containers will use. The permission should be whatever your applications need.
  * Ensure that your Task role has the below permissions attached in order to access CloudWatch (for log ingestion).
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
          }
      ]
  }
  ```
  
* ```{{execution-role-arn}}```: ECS task execution role ARN.
  * This is the role that Amazon ECS agent requires to launch/execute your containers.
  * Ensure that the ```AmazonSSMReadOnlyAccess```, ```AmazonECSTaskExecutionRolePolicy``` and ```CloudWatchAgentServerPolicy``` policies are attached to your ECS Task execution role.
  * If you would like to store more sensitive data for ECS to use, refer to https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data.html.    

* ```{{aws-region}}```: The AWS region where the ECS Daemonset will be deployed: e.g. ```us-west-2```
  
* ```{{ecs-cluster-name}}```: The name of the ECS cluster in which you are deploying the Fluent-Bit Daemonset.


You can also adjust the resource limit (e.g. cpu and memory) based on your particular use cases.