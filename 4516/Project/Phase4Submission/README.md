# Advanced Computer Networks Phase 4 Submission

This is the Team 17 Submission for Phase 4 of the Advanced Computer Networks Term Project

Files included are:

* This `README.md`
* `phase4_controller.py` - The Ryu OpenFlow controller script used on Host 4 which includes all S-NAT IP rewriting and other functionality.
* `CodeExplanation.txt` - A short explanation of the changes made to the controller from Phase 3 and their purpose to complete Phase 4.
* `00-installer-config.yaml` - The new Netplan alias configuration file on Host 1, giving Host 1 all IPs in the 10.61.17.48/28 range as aliases
* `ovs-setup.sh` - A bash script to setup OVS on Host 1, showing the commands run on Host 1 to set it up and connect to the controller on Host 4.
* `Data_Comparison.txt` - A document comparing the test data from Phase 2 to the final test data from Phase 4.
* `answers.txt` - The required answer and discussion of the prompt questions for Phase 4.
* `graph.py` - A script written and used to graph the results of `tcpping` trials (and of `ping` trials), compared to Phase 2 data. The code to generate `TCPPing_Graph.png` and `Ping_Graph.png` are separated by block comments
* `pingData.txt` - The output of our `ping` trials, where we recorded RTTs between Host 1 and the web server where we only made one TCP connection, then used the created FLOW_MODs
* `tcppingData.txt` - The output of our `tcpping` trials, where we used tcpping to make a new tcp connection from Host 1 to the web server for each ping, making us go through the entire DNS resolving and virtual IP assignment process for each ping
* `Ping_Graph.png` - The graphed data comparing our `ping` trials with our data from Phase 2
* `TCPPing_Graph.png` - The graphed data comparing our `tcpping` trials with our data from Phase 2

If you have any questions, feel free to contact us at kshah2@wpi.edu, sparks@wpi.edu, and kwdesantis@wpi.edu.
