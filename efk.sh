 L=`cat k8s-addon/efk/kibana-deployment.yaml |grep -n SERVER_BASEPATH|awk -F':' '{print $1+1}'`
 sed  -i "$L s/.*/#\0/" k8s-addon/efk/kibana-deployment.yaml 
 
 L=`cat k8s-addon/efk/fluentd-es-ds.yaml |grep -n nodeSelector|awk -F':' '{print $1+1}'` && \
 sed  -i "$L s/.*/#\0/" k8s-addon/efk/fluentd-es-ds.yaml

kubectl set image  daemonset fluentd-es-v2.2.1  fluentd-es=k8s.gcr.io/fluentd-elasticsearch:v2.2.1 -n kube-system
kubectl apply -f k8s-addon/efk/
