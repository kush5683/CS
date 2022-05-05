# Host 4 Files

This host contains multiple systems, which would usually be run on different machines, including:

* A Honeypot Server that unwanted traffic is directed to
* A Ryu OpenFlow Controller
* A DNS Server

00-installer-config.yaml was edited to add an IP alias to Host 4.

named.conf.local was edited to create a zone.

db.team17.4516.cs.wpi.edu was made as a DNS record and an A record was put into it.

After DNS records were set up, bind9 was restarted using `service bind9 restart`
