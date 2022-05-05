# Advanced Computer Networks Phase 3 Submission

This is the Team 17 Submission for Phase 3 of the Advanced Computer Networks Term Project

Files included are:

* This `README.md`
* `phase3_controller.py` - The Ryu OpenFlow controller script used on Host 4 which includes DNS parsing, rewriting, and firewall authorizations
* `test.pcap` - TShark packet captures demonstrating proper operation of the network
* `PacketCaptureDiscussion.txt` - a discussion and explanation of the packet capture.
* `DNS_output.txt` - The output on Host 1 of running over 110 trials of `tcpping www.team17.4516.cs.wpi.edu`, including response times and virutal IPs assigned (also illustrating proper behavior of the network)
* `DigOutput.png` - A screenshot of the output of running `dig www.team17.4516.cs.wpi.edu` from Host 1, with a virtual IP answer field of `10.61.17.139`
* `CodeAndMethodsExplanation.txt` - A file explaining our methods and code used to make `phase3controller.py`
* `graph.py` - A script written and used to graph the results of `tcpping` trials, both alone and compared to Phase 2 data
* `Trial_Comparison.png` - The RTT data from Phase 2 overlaid with the new data with DNS editing for comparison. NOTE: X axis was edited to align the data better for reading
* `DNS_Edit_RTT.png` - The data gathered from Phase 3, showing RTT in ms of `tcpping` with DNS editing

If you have any questions, feel free to contact us at kshah2@wpi.edu, sparks@wpi.edu, and kwdesantis@wpi.edu.

