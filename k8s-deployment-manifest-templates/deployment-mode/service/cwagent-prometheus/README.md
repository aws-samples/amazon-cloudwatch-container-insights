## CloudWatch Agent with Prometheus Monitoring support deployment yaml files

* [prometheus-eks.yaml](prometheus-eks.yaml) provides an example for deploying the CloudWatch Agent with Prometheus monitoring support for EKS.
* [prometheus-k8s.yaml](prometheus-k8s.yaml) provides an example for deploying the CloudWatch agent with Prometheus monitoring support for K8S on EC2.

### IAM permissions required by CloudWatch Agent for all features:
* CloudWatchAgentServerPolicy

### CloudWatch Agent Configuration:

#### CloudWatch Agent Prometheus Configuration:
CloudWatch Agent allows the customer to configure the Prometheus metrics setting in configuration map: `prometheus-cwagentconfig`.
For more information, see [CloudWatch Agent Prometheus Configuration](TBD.html).

#### Prometheus Scrape Configuration:
CloudWatch Agent allows the customer to specify a set of targets and parameters describing how to scrape them. The configuration is stored in configuration map: `prometheus-config`
The syntax is the same as [Prometheus Scrape Configuration](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#scrape_config)

### Default Prometheus Scrape Rules and EMF Metrics Configurations:
Both yaml files contain the default settings for the following containerized applications:

|Application     | Reference                                                                                                                 |
|----------------|---------------------------------------------------------------------------------------------------------------------------|
|NGINX_INGRESS   |Exposed by Helm Chart:   [stable/nginx-ingress](https://github.com/helm/charts/tree/master/stable/nginx-ingress)           |
|MEMCACHED       |Exposed by Helm Chart:   [stable/memcached](https://github.com/helm/charts/tree/master/stable/memcached)                   |
|HAPROXY_INGRESS |Exposed by Helm Chart:   [incubator/haproxy-ingress](https://github.com/helm/charts/tree/master/incubator/haproxy-ingress) |
|AWS APP MESH    |Exposed by Helm Chart:   [EKS Charts](https://github.com/aws/eks-charts/blob/master/README.md)                             |
|JAVA/JMX        |Exposed by JMX_Exporter: [JMX_Exporter](https://github.com/prometheus/jmx_exporter)                                        |
