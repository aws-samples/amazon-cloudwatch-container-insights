#!/usr/bin/env bash

cd "$(dirname "$0")"

OUTPUT=./cwagent-fluentd-quickstart.yaml

cat ../cloudwatch-namespace.yaml > ${OUTPUT}
echo -e "\n---\n" >> ${OUTPUT}
cat ../cwagent-kubernetes-monitoring/cwagent-serviceaccount.yaml >> ${OUTPUT}
echo -e "\n---\n" >> ${OUTPUT}
cat ../cwagent-kubernetes-monitoring/cwagent-configmap.yaml | sed "s|\"logs|\"agent\": {\\
        \"region\": \"{{region_name}}\"\\
      },\\
      \"logs|g" >> ${OUTPUT}
echo -e "\n---\n" >> ${OUTPUT}
cat ../cwagent-kubernetes-monitoring/cwagent-daemonset.yaml >> ${OUTPUT}
echo -e "\n---\n" >> ${OUTPUT}
cat ../fluentd/fluentd-configmap.yaml >> ${OUTPUT}
echo -e "\n---\n" >> ${OUTPUT}
cat ../fluentd/fluentd.yaml >> ${OUTPUT}