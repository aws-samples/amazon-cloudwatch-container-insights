## CloudWatch Agent and Fluent-Bit for ECS Instance Metrics and Logs Collection Quick Start

The cloudformation template in this folder helps you to quickly deploy both the CloudWatch agent and Fluent-Bit as daemon-services using a single CloudFormation stack to collect ECS Container Instance Metrics and Logs.

* [fluent-bit-cwagent-combined-cfn.yaml](fluent-bit-cwagent-combined-cfn.yaml): sample cloudformation template


Run following aws cloudformation command with the cloudformation template file to deploy the Fluent-Bit and CloudWatch agent Daemonsets with required IAM roles. ***Please assign the actual ECS cluster name and the cluster region in the first two lines of the command separately.***

```
ClusterName=<your-ecs-cluster-name>
Region=<your-ecs-cluster-region>
aws cloudformation create-stack --stack-name CloudWatch-Fluent-Bit-${ClusterName}-${Region} \
    --template-body file://fluent-bit-cwagent-combined-cfn.yaml \
    --parameters ParameterKey=ClusterName,ParameterValue=${ClusterName} \
                 ParameterKey=CreateIAMRoles,ParameterValue=True \
    --capabilities CAPABILITY_NAMED_IAM \
    --region ${Region}
```