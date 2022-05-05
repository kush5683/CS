# Advanced Computer Networks Phase 2 Submission

This is the Team 17 Submission for Phase 2 of the Advanced Computer Networks Term Project

Files included are:

* This README
* ovs-setup.sh - A .sh file of the commands run to setup OVS on Host 3
* ovs-vsctl_show-output - A text file of the output of the "ovs-vsctl show" command on Host 3
* Analysis_and_Explanation.txt - A document explaining packet capture data collected on Host 3 (test.pcap), showing proper operation. This also includes a timing analysis of latency added by the controller elevation. 
* graph.py - A python script written to collect and graph data from 100 TCP connections between Host 1 and 3 for both Traditional and OpenFlow networks
* RTT_vs_Time.png - A graph comparing RTT time of our 100 trials of TCP connections (both on the Traditional and OpenFlow network)
* Trial_Comparison - A document comparing the results of the 100 trials of TCP connections on both networks.  
* host1_host3_rtt_DATA.txt - Data gathered from the 100 trials of TCP connections on the traditional network
* host1_host3_rtt_OPENFLOW_DATA.txt - Data gathered from the 100 trials of TCP connections on the OpenFlow network
* phase2controller.py - The Ryu OpenFlow controller script used on Host 4 that approves all traffic
* test.pcap - TShark packet captures on Host 3 used for analysis and to ensure proper operation through PACKET_IN and PACKET_OUT messages being sent and received by the OVS

If you have any questions, feel free to contact us at kshah2@wpi.edu, sparks@wpi.edu, and kwdesantis@wpi.edu.

