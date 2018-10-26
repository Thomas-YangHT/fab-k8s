#!/usr/bin/bash
#
#Script for install k8s1.12.1 on CoreOS by LinuxMan
#  _       _                          __  __                 
# | |     (_)  _ __    _   _  __  __ |  \/  |   __ _   _ __  
# | |     | | | '_ \  | | | | \ \/ / | |\/| |  / _` | | '_ \ 
# | |___  | | | | | | | |_| |  >  <  | |  | | | (_| | | | | |
# |_____| |_| |_| |_|  \__,_| /_/\_\ |_|  |_|  \__,_| |_| |_|
#                                                             
#
#start timestamp
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

#network
[ $net = "calico" ] && echo "install calico" && \
fab -H $master -f fab_inst.py calico -u core --colorize-errors 
[ $net = "flannel" ] && echo "install flannel" && \
fab -H $master -f fab_inst.py flannel -u core --colorize-errors 

#find join command
cat log |grep kubeadm|grep join |awk -F'out:' '{print "sudo "$2}' >join.sh

#node
fab -H $node -f fab_inst.py node -u core -P --colorize-errors 

#dashboard
[ $dashboard = true ] && echo "install dashboard" && \
fab -H $master -f fab_inst.py dashboard -u core --colorize-errors |tee -a log

#cost seconds
D2=`date +%s`
echo Install k8s base-structure finished in $((D2-D1)) seconds
#stage base finish.
#
echo "Start addon install..."
#addon prepare
( [ $ingress = true ] || [ $helm = true ] || [ $prometheus = true ] || [ $efk = true ] ) && \
fab -H $master,$node -f fab_inst.py addon -u core -P --colorize-errors 

#ingress
[ $ingress = true ] && echo "install ingress" && \
fab -H $master -f fab_inst.py ingress -u core --colorize-errors 

#helm
[ $helm = true ] && echo "install helm" && \
fab -H $master -f fab_inst.py helm -u core --colorize-errors

#prometheus
[ $prometheus = true ] && echo "install prometheus" && \
fab -H $master -f fab_inst.py prometheus -u core --colorize-errors

#efk
[ $efk = true ] && echo "install efk" && \
fab -H $master -f fab_inst.py efk -u core --colorize-errors

#cost seconds
D2=`date +%s`
echo ALL Mission completed in $((D2-D1)) seconds

#END.
