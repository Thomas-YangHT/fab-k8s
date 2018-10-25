#!/usr/bin/bash
#if no fab cmd, then install fabric
which fab;[ $? -eq 1 ] && echo "install fabric" && yum install -y fabric 

#import hosts config
source ./hosts

#prepare
fab -H $master,$node -f fab_inst.py prepare -u core -P --colorize-errors

#master
fab -H $master -f fab_inst.py master -u core --colorize-errors |tee log

#find join command
cat log |grep kubeadm|grep join |awk -F'out:' '{print "sudo "$2}' >join.sh

#node
fab -H $node -f fab_inst.py node -u core -P --colorize-errors 
