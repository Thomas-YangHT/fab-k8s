from fabric.api import *

def test():
    with cd("/home/core/coreos-k8s"):
        run("ls")

def prepare():
    remote_dir_tar='/home/core/coreos-k8s.tgz'
    put('coreos-k8s.tgz', '')
    run('tar zxvf coreos-k8s.tgz')
    run('ls coreos-k8s')
    run('ls coreos-k8s/*tar |awk \'{print "docker load <"$1}\'|sh')
    run('docker images')
    run('sudo mkdir -p /opt/{bin,cni/bin}')
    run('sudo tar -C /opt/cni/bin -xzvf coreos-k8s/cni-plugins-amd64-v0.6.0.tgz')
    run('sudo cp /home/core/coreos-k8s/{kubeadm,kubelet,kubectl} /opt/')
    run('sudo chmod +x /opt/bin/{kubeadm,kubelet,kubectl}')
    run('ls -l /opt/*')
    run('sudo mkdir -p /etc/systemd/system/kubelet.service.d')
    run('sudo cp  coreos-k8s/kubelet.service  /etc/systemd/system/kubelet.service')
    run('sudo cp  coreos-k8s/10-kubeadm.conf  /etc/systemd/system/kubelet.service.d/10-kubeadm.conf')
    run('sudo systemctl enable kubelet && sudo systemctl start kubelet')

def master():
    run('export PATH=$PATH:/opt/bin')
    run('sudo kubeadm reset -f ')
    run('sudo kubeadm init --kubernetes-version=v1.12.1 --pod-network-cidr=10.244.0.0/16 --apiserver-advertise-address=0.0.0.0')
    run('mkdir -p $HOME/.kube')
    run('sudo cp  /etc/kubernetes/admin.conf $HOME/.kube/config')
    run('sudo chown $(id -u):$(id -g) $HOME/.kube/config')
   # run('kubectl apply -f coreos-k8s/kube-flannel.yml')
   ###calico
    run('kubectl apply -f  coreos-k8s/etcd.yaml')
    run('kubectl apply -f  coreos-k8s/rbac.yaml')
    run('kubectl apply -f  coreos-k8s/calico.yaml')
   ###calico
    run('sed -i "/^\  ports:/i \  type: NodePort"  coreos-k8s/kubernetes-dashboard.yaml')
    run('kubectl apply -f  coreos-k8s/kubernetes-dashboard.yaml')
    run('kubectl apply -f  coreos-k8s/dashboard-adminuser.yaml')
    run('kubectl apply -f  coreos-k8s/dashboard-rolebonding.yaml')
    run('kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep admin-user | awk \'{print $1}\')')
    run('kubectl get svc --all-namespaces')

def node():
    put('join.sh','')
    run('sudo chmod +x ./join.sh')
    run('sudo kubeadm reset -f')
    run('sudo modprobe ip_vs')
    run('./join.sh')

def ingress():
    run('tar zxvf coreos-k8s/ingress-nginx.tgz -C coreos-k8s/')
    run('sed -i "/- --anno/a \            - --enable-ssl-passthrough" coreos-k8s/ingress-nginx/deploy/mandatory.yaml ')
    run('kubectl apply -f  coreos-k8s/ingress-nginx/deploy/mandatory.yaml')
    run('kubectl apply -f  coreos-k8s/ingress-nginx/deploy/provider/baremetal/service-nodeport.yaml')
    run('kubectl apply -f  coreos-k8s/ingress-dashboard.yml')
    run('kubectl get ingress --all-namespaces')

def helm():
    run('tar zxvf coreos-k8s/helm-v2.11.0-linux-amd64.tar.gz -C coreos-k8s/')
    run('sudo cp coreos-k8s/linux-amd64/helm /opt/bin/helm')
    run('helm init --upgrade -i registry.cn-hangzhou.aliyuncs.com/google_containers/tiller:v2.11.0 --stable-repo-url https://kubernetes.oss-cn-hangzhou.aliyuncs.com/charts')
    run('kubectl create serviceaccount --namespace kube-system tiller')
    run('kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller')
    run('kubectl patch deploy --namespace kube-system tiller-deploy -p \'{"spec":{"template":{"spec":{"serviceAccount":"tiller"}}}}\'')
    run('kubectl get pods --all-namespaces')
