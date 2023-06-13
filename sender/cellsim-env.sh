#! /bin/bash
#set -xv
set -e

if [ `whoami` != root ]; then
    echo "Please run this script using sudo"
    exit
fi

COMMAND_LINE_OPTIONS_HELP="
Usage:  $0 setup [ingress] [egress]
        $0 teardown [ingress] [egress]
"

usage() {
   echo "$COMMAND_LINE_OPTIONS_HELP"
   exit 3
}

case "$1" in

setup)
    if [ "$#" -ne 3 ]; then
        usage
    fi
    ingress=$2
    egress=$3

    echo "Put both interfaces $ingress and $egress in promisc mode."
    ip link set $ingress promisc on
    ip link set $egress promisc on

    echo "Disable segmentation offloading on $ingress and $egress."
    ethtool --offload $ingress gso off tso off gro off
    ethtool --offload $egress gso off tso off gro off

    echo "Add iptable rule to drop forwarding packets"
    iptables -A FORWARD -j DROP
    ;;

teardown)
    if [ "$#" -ne 3 ]; then
        usage
    fi
    ingress=$2
    egress=$3
    echo "Turn off promisc mode on interfaces $ingress and $egress."
    ip link set $ingress promisc off
    ip link set $egress promisc off

    echo "Restore default segmentation offloading on $ingress and $egress."
    ethtool --offload $ingress gso on tso off gro on
    ethtool --offload $egress gso on tso off gro on

    echo "Delete iptale rule to drop forwarding packets"
    iptables -D FORWARD -j DROP
    ;;

*)
    usage
    ;;

esac
