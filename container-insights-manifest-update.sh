#!/usr/bin/env bash

cd "$(dirname "$0")"

# Version definitions
newK8sVersion="k8s/1.3.38"
agentVersion="public.ecr.aws/cloudwatch-agent/cloudwatch-agent:1.300060.0b1248"
fluentdVersion="fluent/fluentd-kubernetes-daemonset:v1.10.3-debian-cloudwatch-1.0"
fluentBitVersion="public.ecr.aws/aws-observability/aws-for-fluent-bit:2.32.4"
fluentBitWindowsVersion="public.ecr.aws/aws-observability/aws-for-fluent-bit:windowsservercore-stable"

# update all YAML and JSON files
find . -type f \( -name "*.yaml" -o -name "*.json" \) -exec bash -c '
    file="$1"
    echo "Processing $file"
    sed -i".bak" "s|k8s/[0-9]*\.[0-9]*\.[0-9a-z]*|'"$newK8sVersion"'|g;s|public\.ecr\.aws/cloudwatch-agent/cloudwatch-agent:[0-9]*\.[0-9]*\.[0-9a-z]*|'"$agentVersion"'|g" "$file"
    rm -f "$file.bak"
' bash {} \;

# update fluent-related files
find . -type f -name "fluent*.yaml" -exec bash -c '
    file="$1"
    if [[ $file == *"windows"* ]]; then
        sed -i".bak" "s|public\.ecr\.aws/aws-observability/aws-for-fluent-bit.*|'"$fluentBitWindowsVersion"'|g" "$file"
    elif [[ $file == *"fluent-bit"* ]]; then
        sed -i".bak" "s|public\.ecr\.aws/aws-observability/aws-for-fluent-bit.*|'"$fluentBitVersion"'|g" "$file"
    elif [[ $file == *"fluentd"* ]]; then
        sed -i".bak" "s|fluent/fluentd-kubernetes-daemonset:.*|'"$fluentdVersion"'|g" "$file"
    fi
    rm -f "$file.bak"
' bash {} \;

# generate quickstart manifests
k8sMonitoringPrefix="./k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring"
OUTPUT="${k8sMonitoringPrefix}/quickstart/cwagent-fluentd-quickstart.yaml"
OUTPUT_FLUENT_BIT="${k8sMonitoringPrefix}/quickstart/cwagent-fluent-bit-quickstart.yaml"
OUTPUT_FLUENT_BIT_WINDOWS="${k8sMonitoringPrefix}/quickstart/cwagent-fluent-bit-quickstart-windows.yaml"

# generate cwagent-fluentd-quickstart.yaml
cat ${k8sMonitoringPrefix}/cloudwatch-namespace.yaml > ${OUTPUT}
echo -e "\n---\n" >> ${OUTPUT}
cat ${k8sMonitoringPrefix}/cwagent/cwagent-serviceaccount.yaml >> ${OUTPUT}
echo -e "\n---\n" >> ${OUTPUT}
cat ${k8sMonitoringPrefix}/cwagent/cwagent-configmap.yaml | sed "s|\"logs|\"agent\": {\\
        \"region\": \"{{region_name}}\"\\
      },\\
      \"logs|g" >> ${OUTPUT}
echo -e "\n---\n" >> ${OUTPUT}
cat ${k8sMonitoringPrefix}/cwagent/cwagent-daemonset.yaml >> ${OUTPUT}
echo -e "\n---\n" >> ${OUTPUT}
cat ${k8sMonitoringPrefix}/fluentd/fluentd-configmap.yaml >> ${OUTPUT}
echo -e "\n---\n" >> ${OUTPUT}
cat ${k8sMonitoringPrefix}/fluentd/fluentd.yaml >> ${OUTPUT}

# Generate cwagent-fluent-bit-quickstart.yaml
cat ${k8sMonitoringPrefix}/cloudwatch-namespace.yaml > ${OUTPUT_FLUENT_BIT}
echo -e "\n---\n" >> ${OUTPUT_FLUENT_BIT}
cat ${k8sMonitoringPrefix}/cwagent/cwagent-serviceaccount.yaml >> ${OUTPUT_FLUENT_BIT}
echo -e "\n---\n" >> ${OUTPUT_FLUENT_BIT}
cat ${k8sMonitoringPrefix}/cwagent/cwagent-configmap.yaml | sed "s|\"logs|\"agent\": {\\
        \"region\": \"{{region_name}}\"\\
      },\\
      \"logs|g" >> ${OUTPUT_FLUENT_BIT}
echo -e "\n---\n" >> ${OUTPUT_FLUENT_BIT}
cat ${k8sMonitoringPrefix}/cwagent/cwagent-daemonset.yaml >> ${OUTPUT_FLUENT_BIT}
echo -e "\n---\n" >> ${OUTPUT_FLUENT_BIT}
cat ${k8sMonitoringPrefix}/fluent-bit/fluent-bit-configmap.yaml >> ${OUTPUT_FLUENT_BIT}
echo -e "\n---\n" >> ${OUTPUT_FLUENT_BIT}
cat ${k8sMonitoringPrefix}/fluent-bit/fluent-bit.yaml >> ${OUTPUT_FLUENT_BIT}

# Generate cwagent-fluent-bit-quickstart-windows.yaml
cat ${k8sMonitoringPrefix}/cwagent/cwagent-daemonset-windows.yaml > ${OUTPUT_FLUENT_BIT_WINDOWS}
echo -e "\n---\n" >> ${OUTPUT_FLUENT_BIT_WINDOWS}
cat ${k8sMonitoringPrefix}/fluent-bit/fluent-bit-windows.yaml >> ${OUTPUT_FLUENT_BIT_WINDOWS}

echo "Version and manifest updates completed successfully!"
