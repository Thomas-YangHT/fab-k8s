#!/usr/bin/bash
D1=`date +%s`

#if no fab cmd, then install fabric
which fab;[ $? -eq 1 ] && echo "install fabric" && yum install -y fabric 
#or: pip install fabric==1.14.0

#import config
source ./CONFIG

#prepare
fab -H $master,$node -f fab_inst.py prepare -u core -P --colorize-errors

#master
fab -H $master -f fab_inst.py master -u core --colorize-errors |tee log

#find join command
cat log |grep kubeadm|grep join |awk -F'out:' '{print "sudo "$2}' >join.sh

#node
fab -H $node -f fab_inst.py node -u core -P --colorize-errors 

#ingress
[ $ingress = true ] && echo "install ingress" && \
fab -H $master -f fab_inst.py ingress -u core --colorize-errors 

#helm
[ $helm = true ] && echo "install helm" && \
fab -H $master -f fab_inst.py helm -u core --colorize-errors

#cost seconds
D2=`date +%s`
echo Install finished in $((D2-D1)) seconds
