## CloudWatch Agent for ECS Instance Logs Collection Quick Start

The cloudformation template in this folder helps you to quickly deploy Fluent-Bit as a daemon-service to collect ECS Container Instance Logs.

* [fluent-bit-ecs-instance-logs-cfn.yaml](fluent-bit-ecs-instance-logs-cfn.yaml): sample cloudformation template


Run following aws cloudformation command with the cloudformation template file to deploy the Fluent-Bit Daemonset with required IAM roles. ***Please assign the actual ECS cluster name and the cluster region in the first two lines of the command separately.***

```
ClusterName=<your-ecs-cluster-name>
Region=<your-ecs-cluster-region>
aws cloudformation create-stack --stack-name Fluent-Bit-${ClusterName}-${Region} \
    --template-body file://fluent-bit-ecs-instance-logs-cfn.yaml \
    --parameters ParameterKey=ClusterName,ParameterValue=${ClusterName} \
                 ParameterKey=CreateIAMRoles,ParameterValue=True \
    --capabilities CAPABILITY_NAMED_IAM \
    --region ${Region}
```