#!/bin/bash

#nohup /home/ubuntu/multisend/sender/cellsim /home/ubuntu/verizon_lte_uplink_slice.ms /home/ubuntu/verizon_lte_downlink_slice.ms 00:00:00:00:00:02 0 LTE-eth0 LTE-eth1 >/tmp/cellsim-stdout 2>/tmp/cellsim-stderr &
#nohup sudo ./cellsim trace-analysis/uplink-1677798915.pps trace-analysis/downlink-1677798915.pps 0.0 eth0 eth1 > /tmp/cellsim-stdout 2>/tmp/cellsim-stderr &
nohup sudo ./cellsim 200.pps 1000.pps 0.0 eth0 eth1 > /tmp/cellsim-stdout 2>/tmp/cellsim-stderr &
