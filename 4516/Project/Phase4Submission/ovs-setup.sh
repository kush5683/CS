#!/bin/sh
echo "Creating OVS-bridge br0 and adding Host 1 MAC addr to it..."
ovs-vsctl add-br br0 -- set bridge br0 other_config:hwaddr=52:54:00:00:03:4a
echo "Adding ens3 as port to br0..."
ovs-vsctl add-port br0 ens3
echo "Removing IP addr from ens3..."
ifconfig ens3 0
echo "Adding IP addr to br0..."
ifconfig br0 10.61.17.1
echo "Connecting br0 to controller..."
ovs-vsctl set-controller br0 tcp:10.61.17.4:6653
echo "Configuration done. OVS show:"
ovs-vsctl show
