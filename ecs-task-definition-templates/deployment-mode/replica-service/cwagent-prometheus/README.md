## CloudWatch Agent for ECS Prometheus Monitoring

The sample ECS task definitions in this folder deploy the CloudWatch Agent as a Replica Service. For more information, see [AWS Public Link TBD](link to be do).

* [cwagent-prometheus-task-definition.json](cwagent-prometheus-task-definition.json): sample ECS task definition

You must replace all the placeholders (with ```{{ }}```) in the above task definitions with your information:
* ```{{task-role-arn}}```: ECS task role ARN.
  * This is the role that your CloudWatch Agent container will use. The required permissions:
    * ```CloudWatchAgentServerPolicy``` policy
    * A customer managed policy with the following readonly permissions for ECS Prometheus target discovery:
        ```
        ECS:ListTasks,
        ECS:DescribeContainerInstances,
        ECS:DescribeTasks,
        ECS:DescribeTaskDefinition
        EC2:DescribeInstances
        ```

* ```{{execution-role-arn}}```: ECS task execution role ARN.
  * This is the role that Amazon ECS requires to launch/execute your containers, e.g. get the parameters from SSM parameter store.
  * Ensure that the ```AmazonSSMReadOnlyAccess```, ```AmazonECSTaskExecutionRolePolicy``` and ```CloudWatchAgentServerPolicy``` policies are attached to your ECS Task execution role.
  * If you would like to store more sensitive data for ECS to use, refer to https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data.html.    

* ```{{awslogs-region}}```: The AWS region where the container logs should be published: e.g. ```us-west-2```

* ```{{launchtype}}```: [Amazon ECS launch type](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html#requires_compatibilities)

* ```{{networkmode}}```: [Amazon ECS network mode](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html#network_mode)

* ```{{ssm-prometheus-config}}```: AWS Systems Manager Parameter name for Prometheus Scraping Config

* ```{{ssm-cwagent-config}}```: AWS Systems Manager Parameter name for CloudWatch Agent Config

You can also adjust the resource limit (e.g. cpu and memory) based on your particular use cases.

## Supported Matrix
CloudWatch Agent with Prometheus Monitoring can be deployed in the following modes

|ECS Launch Type         | ECS Network Mode    |
|------------------------|---------------------|
|FARGATE                 | awsvpc              |
|EC2 (Linux)             | awsvpc              |
|EC2 (Linux)             | bridge              |
|EC2 (Linux)             | host                |


## Examples

**Sample Prometheus Config SSM Parameter**

For more information, see [Prometheus Scraping Config](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#scrape_config)
```
global:
  scrape_interval: 1m
  scrape_timeout: 10s
scrape_configs:
  - job_name: cwagent-ecs-file-sd-config
    sample_limit: 10000
    file_sd_configs:
      - files: [ "/tmp/cwagent_ecs_auto_sd.yaml" ]
```

**Sample CWAgent Config**

For more information, see [CWAgent Prometheus Monitoring Config for ECS](TBD)
```
{
  "agent": {
    "debug": true
  },
  "logs": {
    "metrics_collected": {
      "prometheus": {
        "prometheus_config_path": "env:PROMETHEUS_CONFIG_CONTENT",
        "ecs_service_discovery": {
          "sd_frequency": "1m",
          "sd_result_file": "/tmp/cwagent_ecs_auto_sd.yaml",
          "docker_label": {
            "sd_port_label": "ECS_PROMETHEUS_EXPORTER_PORT",
            "sd_job_name_label": "ECS_PROMETHEUS_JOB_NAME"
          },
          "task_definition_list": [
            {
              "sd_job_name": "bugbash-workload-java-ec2-awsvpc-task-def-sd",
              "sd_metrics_ports": "9404;9406",
              "sd_task_definition_arn_pattern": ".*:task-definition/targets-workload-java-ec2-awsvpc:[0-9]+"
            }
          ]
        },
        "emf_processor": {
          "metric_declaration_dedup": true,
          "metric_declaration": [
            {
              "source_labels": ["Java_EMF_Metrics"],
              "label_matcher": "^true$",
              "dimensions": [["ClusterName","TaskDefinitionFamily"]],
              "metric_selectors": [
                "^jvm_threads_current$",
                "^jvm_threads_daemon$",
                "^catalina_globalrequestprocessor_requestcount$",
                "^catalina_globalrequestprocessor_errorcount$",
                "^catalina_globalrequestprocessor_processingtime$"
              ]
            },
            {
              "source_labels": ["Java_EMF_Metrics"],
              "label_matcher": "^true$",
              "dimensions": [["ClusterName","TaskDefinitionFamily","pool"]],
              "metric_selectors": [
                "^jvm_memory_pool_bytes_used$"
              ]
            }
          ]
        }
      }
    },
    "force_flush_interval": 5
  }
}

```

**Creating CWAgent ECS Task Definition**

Create the CWAgent ECS Task definition for the ECS `EC2` Cluster with `bridge` network mode in region `ca-central-1`. 
```
ECSTaskRoleName=CWAgentPrometheusECSTaskRole
ECSExecutionRoleName=CWAgentPrometheusECSExecutionRole
AWSRegion=ca-central-1
PrometheusSSMConfigName=AmazonCloudWatch-prometheus-yaml-config
CWAgentSSMConfigName=AmazonCloudWatch-prometheus-appmesh-config
ECSLaunchType=EC2
ECSNetworkMode=bridge

cat cwagent-prometheus-task-definition.json \
| sed "s/{{task-role-arn}}/${ECSTaskRoleName}/g" \
| sed "s/{{execution-role-arn}}/${ECSExecutionRoleName}/g" \
| sed "s/{{launchtype}}/${ECSLaunchType}/g" \
| sed "s/{{networkmode}}/${ECSNetworkMode}/g" \
| sed "s/{{awslogs-region}}/${AWSRegion}/g" \
| sed "s/{{ssm-prometheus-config}}/${PrometheusSSMConfigName}/g" \
| sed "s/{{ssm-cwagent-config}}/${CWAgentSSMConfigName}/g" \
| xargs -0 aws ecs register-task-definition --region ${AWSRegion} --cli-input-json
```

**Creating CWAgent ECS Replica Service**

Run the CWAgent with Prometheus Monitoring as replica service (with replica=1).

```
ECSClusterName=sample-ecs-ec2-cluster
AWSRegion=ca-central-1

aws ecs create-service \
--cluster ${ECSClusterName} \
--service-name sample-prometheus-cwagent-service-EC2-bridge \
--task-definition ecs-cwagent-prometheus-replica-service-EC2-bridge \
--launch-type EC2 \
--scheduling-strategy REPLICA \
--desired-count 1 \
--region ${AWSRegion}
```
