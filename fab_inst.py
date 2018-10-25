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
    run('kubectl apply -f coreos-k8s/kube-flannel.yml')
    run('kubectl apply -f coreos-k8s/kubernetes-dashboard.yaml')
    run('kubectl apply -f coreos-k8s/dashboard-adminuser.yaml')
    run('kubectl apply -f coreos-k8s/dashboard-rolebonding.yaml')

def node():
    put('join.sh','')
    run('sudo chmod +x ./join.sh')
    run('sudo kubeadm reset -f')
    run('sudo modprobe ip_vs')
    run('./join.sh')
