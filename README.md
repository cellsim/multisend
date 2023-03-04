# Collect trace

**saturatr** is used to saturate both uplink and downlink at the same time, keep the buffer full but still avoid flooding the network, and collect trace at both ends, which can be used for simulate the network behavior in lab environment. 

You need two interfaces on the client side to give accurate measurement on both directions. Measurement on both directions matters b/c congestion control relies on the feedbacks and congestion on the reserve direction will impact that, we can't assume the congestion is just one direction and other side has no problem, this may not be realistic in real world.

You can only run this on Linux machine, with two phones connected, and use USB tethering instead of WiFi tethering.

## Server

Run server first:

```
$ ./saturatr
```

This will use port 9001 for data and port 9002 for feedback, log will be written in current directory, with the name pattern `server_[timestamp]_[pid]`, once client starts sending data, the content of the log will include `OUTGOING ACK RECEIVED` (server as saturater received ack) and `INCOMING DATA RECEIVED` (server as receiver received data).

```
OUTGOING ACK RECEIVED senderid=1677798915, seq=41, send_time=1677798916256107327,  recv_time=1677798916773702681, rtt=0.5176, 32 => 33
INCOMING DATA RECEIVED senderid=1677798915, seq=20, send_time=1677798916769931926, recv_time=1677798916774092048, 1delay=0.0042 
```

## Client

Run client, you need two network interfaces, one for data channel (specify `test_ip` and `test_dev`), another one for feedback channel (specify `reliable_ip` and `reliable_dev`), so that the feedback won't be affected when saturating both directions, otherwise, delayed feedback will cause sender not able to adapt immediately and triggers throttling or packet drop. The sender will try to keep the queuing delay larger than 750 ms and less than 3000 ms, to maintain a backlogged queue.

```
$ ./saturatr [reliable_ip] [reliable_dev] [test_ip] [test_dev] [server_ip]
```

client log will have the pattern `client_[timestamp]_[sender_id]`, with content like:

```
INCOMING DATA RECEIVED senderid=1677798915, seq=74, send_time=1677798916774231753, recv_time=1677798917137439212, 1delay=0.3632 
OUTGOING ACK RECEIVED senderid=1677798915, seq=20, send_time=1677798916769931926,  recv_time=1677798917140007594, rtt=0.3701, 20 => 21
```

This is similar with the server one above, `INCOMING DATA RECEIVED` (client received data from server) and `OUTGOING ACK RECEIVED` (client as saturater received ack). Server log may contains logs form multiple client (`senderid`), client log will only contains those of one sender (`senderid`).

# Simulate

## trace analysis

Once has the client and server log, you can put those logs in "trace_analysis" directory, and then run "process-traces.sh", this will find all sessions in the log, and parsing both client and server logs, to generate ".pps" files for both uplink and downlink, which can be used later for simulation.

```
$ ./process-traces.sh 
Server logs are server-1677798349-10690 server-1677889861-19841 server-1677893899-20280
Server time is 1677798349
Session name is 1677798915
Session id is 1677798915
Session name is 1677890163
Session id is 1677890163
Session name is 1677893919
Session id is 1677893919
```

Generated ".pps" files, currently it just uses the receive timestamp in the log, and adjusts the offset so that the timestamp starts from 0, and records the timestamp of each packet received (packet size is not recorded since the default data packet size used in `saturatr` is 1500 Bytes).

```
$ ls *.pps
downlink-1677798915.pps  downlink-1677890163.pps  downlink-1677893919.pps  uplink-1677798915.pps  uplink-1677890163.pps  uplink-1677893919.pps
```

You can use "simulation-analysis/rate-estimate.py" to check the bitrate for each second in "pps" file.

## Simulation

`cellsim` is a user space emulator, which uses raw socket API to receive data from one interface, adds delay according the trace collected (it will not drop packets, only adds delay), and then forwards to another interface.

You can use the Raspberrypi "piem" setup, which has ethernet bridge network built in.

First, you should run `cellsim-setup.sh [ingress] [egress]`, "ingress" is the name of the device which connects with the test client device, and "egress" is the name of the device which connects to the internet.

Then you can change "cellsim-runner.sh", and replace the following parameters.

```
./cellsim 200.pps 1000.pps 0.0 eth0 eth1

# 200.pps, uplink pps file
# 1000.pss, downlink pps file
# 0.0, packet loss ratio
# eth0, internet side interface
# eth1, test client side interface
```