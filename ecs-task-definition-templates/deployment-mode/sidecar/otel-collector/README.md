## OpenTelemetry Collector for Amazon ECS task and container metrics

The sample Amazon ECS task definitions in this folder deploy the upstream [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/) (`otel/opentelemetry-collector-contrib`) as a sidecar to your application. The collector's `awsecscontainermetrics` receiver reads the [task metadata endpoint version 4](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-metadata-endpoint-v4.html) and sends task-level and container-level metrics to Amazon CloudWatch over OTLP. You query them with PromQL.

* [otel-collector-ec2.json](otel-collector-ec2.json): sample ECS task definition for the EC2 launch type (`bridge` network mode).
* [otel-collector-fargate.json](otel-collector-fargate.json): sample ECS task definition for the Fargate launch type (`awsvpc` network mode). It also works for Amazon ECS Managed Instances when you change `requiresCompatibilities`.
* [collector-ecs-metrics.yaml](collector-ecs-metrics.yaml): the collector configuration. Store it in an SSM parameter (see below).
* [dashboard/dashboard.json](dashboard/dashboard.json): a CloudWatch dashboard (PromQL) built for this configuration.
* [dashboard/build_dashboard.py](dashboard/build_dashboard.py): regenerates the dashboard, for example for another Region.

These samples were tested with `otel/opentelemetry-collector-contrib:0.165.0` on Fargate, EC2 (`bridge`), and ECS Managed Instances. For the full setup guide, metric reference, and troubleshooting, see [Collecting Amazon ECS metrics with the OpenTelemetry Collector](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/deploy-container-insights-ECS-otel-collector.html).

### Replace the placeholders

Replace all the placeholders (with ```{{ }}```) in the task definitions with your information:

* ```{{task-role-arn}}```: ECS task role ARN.
  * The collector signs requests to CloudWatch with this role. Allow `cloudwatch:PutMetricData`:
    ```json
    {
      "Version": "2012-10-17",
      "Statement": [{ "Effect": "Allow", "Action": "cloudwatch:PutMetricData", "Resource": "*" }]
    }
    ```
* ```{{execution-role-arn}}```: ECS task execution role ARN.
  * Ensure that the ```AmazonECSTaskExecutionRolePolicy``` and ```AmazonSSMReadOnlyAccess``` policies are attached, so that ECS can pull the image and read the configuration parameter.
* ```{{awslogs-region}}```: The AWS Region of your cluster, e.g. ```us-west-2```. It's also used as `AWS_REGION` for the CloudWatch endpoint.
* ```{{demo-app-image}}```: your application image.

You can also adjust the resource limits (`cpu` and `memory`) for your use case. In testing, the collector used about 45 MiB of memory.

### Store the collector configuration

Create an SSM parameter (```ecs-otel-collector-sidecar-ec2``` or ```ecs-otel-collector-sidecar-fargate```) in the Region where your cluster is located, with the contents of [collector-ecs-metrics.yaml](collector-ecs-metrics.yaml):

```bash
aws ssm put-parameter --name ecs-otel-collector-sidecar-fargate --type String \
  --value file://collector-ecs-metrics.yaml
```

The configuration requires the `metric_start_time` processor. Without it, CloudWatch rejects the receiver's cumulative metrics (`StartTimeUnixNano is required`).

### Verify

In the CloudWatch console, open Query Studio and run:

```
count by ("@resource.aws.ecs.service.name") ({"ecs.task.memory.utilized"})
```

It returns one series per running task within a few minutes.

### Create the dashboard

```bash
aws cloudwatch put-dashboard --dashboard-name ecs-metrics \
  --dashboard-body file://dashboard/dashboard.json
```

The dashboard defaults to `us-west-2`. Change the Region filter on the dashboard, or regenerate it with `python3 dashboard/build_dashboard.py --region <region> --out dashboard/dashboard.json`. `put-dashboard` may return messages saying that the `x` property will be ignored; the dashboard is still created with its layout.
