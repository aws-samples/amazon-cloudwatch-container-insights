## Example Amazon ECS task definitions for DaemonService deployment mode

This folder contains the example Amazon ECS task definitions for DaemonService deployment mode.

Check the sub folders for different functionality:

### [cwagent-ecs-instance-metric](cwagent-ecs-instance-metric)
This folder provides the functionality that enables you to deploy the CloudWatch Agent to collect ECS Instance Metrics.

### [fluent-bit-ecs-instance-logs]( fluent-bit-ecs-instance-logs)
This folder provides the functionality that enables you to deploy Fluent-Bit to collect ECS Container Instance.

### [fluent-bit-cwagent-combined-cfn]( fluent-bit-cwagent-combined-cfn)
This folder provides the functionality that enables you to deploy both the CloudWatch Agent and Fluent-Bit in a single CloudFormation stack.