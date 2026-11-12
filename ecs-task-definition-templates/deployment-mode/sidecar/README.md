## Example Amazon ECS task definitions for Sidecar deployment mode

This folder contains the example Amazon ECS task definitions for Sidecar deployment mode.

Check the sub folders for different functionality:

### [cwagent-emf](cwagent-emf)
The sample Amazon ECS task definitions in this folder deploy the CloudWatch Agent as a Sidecar to your application to enable Amazon CloudWatch Embedded Metric Format (EMF).

### [cwagent-statsd](cwagent-statsd)
This folder provides the functionality that enables you to deploy the CloudWatch Agent to utilize `StatsD`.

### [cwagent-sdkmetrics](cwagent-sdkmetrics)
This folder provides the functionality that enables you to deploy the CloudWatch Agent to utilize AWS SDK Metrics.
### [otel-collector](otel-collector)
This folder provides sample task definitions that deploy the upstream OpenTelemetry Collector as a sidecar to send task-level and container-level metrics to Amazon CloudWatch over OTLP, with a CloudWatch PromQL dashboard.
