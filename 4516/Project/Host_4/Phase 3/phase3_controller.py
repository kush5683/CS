from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import *
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import *
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import *
from ryu.lib.packet import ether_types
from ryu.lib import addrconv
import dpkt
import socket
import random
import typing

# List of our virtual IPs
virtualIPs = [f"10.61.17.{i}" for i in range(128, 255)]
# The DNS_TTL of our DNS server
DNS_TTL = 605

"""
A class we used (alongside a dictionary attribute) to track which IPs are most recently assigned.
This is used to handle the edge case where all the IPs are allocated but the web requests aren't made,
leading to every IP to be used, so new connections would have to wait for an IP to be deallocated.
Using this usageStack we instead just give the new connection the IP that was allocated first and has
been sitting unused the longest.
"""
class usageStack(list):
    def remove(self, __value):
        super().remove(__value)
        return __value

    def push(self, __value):
        super().append(__value)
        return __value

    def pop(self):
        return self.remove(self[0])

    def peek(self):
        return self[0]

    def append(self, __object):
        return self.push(__object)

    def relocate(self, __object):
        self.push(self.remove(__object))


class SimpleSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

        # dictionary to track which virtualIPs have been assigned and which are free
        self.tracker = {}
        for i in virtualIPs:
            self.tracker.setdefault(i, False)  # meaning it is unassigned (free)
        self.usage = usageStack()

    """
    Used to add a normal flow to the controller to allow for the simple_controller functionality
    """
    def add_flow(self, datapath, in_port, dst, src, actions):
        ofproto = datapath.ofproto

        match = datapath.ofproto_parser.OFPMatch(
            in_port=in_port,
            dl_dst=haddr_to_bin(dst), dl_src=haddr_to_bin(src))

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=ofproto.OFP_DEFAULT_PRIORITY,
            flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions)
        datapath.send_msg(mod)

    """
    Used to add a flow to the controller based on IPs
    """

    def add_ip_flow(self, datapath, srcIP, dstIP, actions, ttl):
        ofproto = datapath.ofproto

        match = datapath.ofproto_parser.OFPMatch(
            dl_type=0x0800, # this was needed to make the FLOW_MOD take account of nw_src nw_dst
            nw_src=srcIP,
            nw_dst=dstIP)

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath,
            match=match,
            cookie=0,
            command=ofproto.OFPFC_ADD,
            hard_timeout=ttl,
            priority=ofproto.OFP_DEFAULT_PRIORITY,
            flags=ofproto.OFPFF_SEND_FLOW_REM,
            actions=actions)

        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        # We drop traffic that isn't between our VMs in order to clean up our debugging
        ourVMs = ["52:54:00:00:03:4a", "52:54:00:00:03:4b", "52:54:00:00:03:4c", "52:54:00:00:03:4d",
                  "ff:ff:ff:ff:ff:ff"]
        if (src not in ourVMs or dst not in ourVMs):
            # make rule to drop the packet
            self.add_flow(datapath, msg.in_port, dst, src, [])
            return
        self.logger.info("packet in %s %s %s %s", dpid, src, dst, msg.in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = msg.in_port

        if dst in self.mac_to_port[dpid]:
            # Get the port of the OVS associated with the dst MAC addr
            out_port = self.mac_to_port[dpid][dst]

            # Check if the traffic is UDP and on port 53 (DNS most likely)
            udp_proto = pkt.get_protocol(udp.udp)
            if udp_proto:
                if udp_proto.dst_port == 53 or udp_proto.src_port:
                    print("DNS packet detected...")

                    # Convert to a DNS dpkt packet to easily check if AN has any answers (if its a reply)
                    dpkt_DNS_pkt = self.convert_packet(msg.data)
                    # If a reply, then an will be a list with elements
                    is_a_reply = len(dpkt_DNS_pkt.an)
                    if is_a_reply:
                        print("The DNS packet is a reply...")
                        # trying to edit and send the packet
                        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

                        # We edit the IP with a virtual one, by editing the answer bytes with a random unallocated virtual IP
                        first_sec = msg.data[:98]
                        ip_sec = self.find_virtual_ip()
                        # Returns a tuple of BYTES, STRING of the chosen vIP
                        ip_bytes = ip_sec[0]
                        third_sec = msg.data[102:]
                        # Make out new packet byte array
                        new_data = first_sec + ip_bytes + third_sec

                        # Use the new data to make a packet
                        udp_pack = packet.Packet(new_data)  # make a Ryu Packet from the new data
                        udp_pack.get_protocol(
                            udp.udp).csum = 0  # set the checksum of the UDP to be automatically calculated
                        udp_pack.serialize()  # updates the checksum

                        # We send out the new PACKET_OUT
                        out_msg = datapath.ofproto_parser.OFPPacketOut(datapath=datapath,
                                                                       buffer_id=msg.buffer_id,
                                                                       in_port=msg.in_port,
                                                                       actions=actions,
                                                                       data=udp_pack.data)
                        self.tracker[ip_sec[1]] = True # Set the allocated IP to True
                        self.usage.push(ip_sec[1])  # add the allocated IP to the usageStack
                        datapath.send_msg(out_msg)
                        return

            # Here we check if the packet is web traffic from Host 1 to a virtual IP and validate if the IP has been assigned
            try:
                srcIP = pkt.get_protocol(ipv4.ipv4).src
                dstIP = pkt.get_protocol(ipv4.ipv4).dst
            except AttributeError:
                srcIP = None
                dstIP = None
            if srcIP == "10.61.17.1" and dstIP in virtualIPs:
                print("Web Request with Alias Detected...")
                # Check that the virtual IP is valid (self.validate_web_packet handles FLOW MODS), if invalid, drop and return
                if not self.validate_web_packet(datapath, srcIP, dstIP, self.mac_to_port[dpid][src],
                                                self.mac_to_port[dpid][dst]):
                    print("Not valid, dropping packet")
                    out_msg = datapath.ofproto_parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                                                   in_port=msg.in_port, actions=[], data=None)
                    datapath.send_msg(out_msg)
                    return

        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=actions, data=data)
        datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        msg = ev.msg
        reason = msg.reason
        port_no = msg.desc.port_no

        ofproto = msg.datapath.ofproto
        if reason == ofproto.OFPPR_ADD:
            self.logger.info("port added %s", port_no)
        elif reason == ofproto.OFPPR_DELETE:
            self.logger.info("port deleted %s", port_no)
        elif reason == ofproto.OFPPR_MODIFY:
            self.logger.info("port modified %s", port_no)
        else:
            self.logger.info("Illegal port state %s %s", port_no, reason)

    """
    Validates if a given dst IP has been assigned by our controller.
    If it is, add a flow allowing it for the TTL.
    If not, add a rule dropping all traffic for a short time, and the caller will be responsible for dropping the packet
    """

    def validate_web_packet(self, datapath, srcIP, dstIP, srcPort, dstPort):
        valid = self.tracker.get(dstIP)
        print("Dst IP: " + str(dstIP) + " Valid? " + str(valid))
        if valid:
            # add flows allowing this connection for the TTL and free the virtual IP
            # think there's some problems with my action creation (initial packet is being forwarded and rule is being made but not forwarding properly)
            print("Alias " + dstIP + " found to be valid, creating flow rule...")
            self.add_ip_flow(datapath, srcIP, dstIP, [datapath.ofproto_parser.OFPActionOutput(dstPort)], DNS_TTL)
            self.add_ip_flow(datapath, dstIP, srcIP, [datapath.ofproto_parser.OFPActionOutput(srcPort)], DNS_TTL)
            # Free the virtual IP
            self.tracker[dstIP] = False
            self.usage.remove(dstIP)  # remove from usage list
        else:
            # drop this packet and make short rule to drop the rest of the traffic
            self.add_ip_flow(datapath, srcIP, dstIP, [], 1)
            self.add_ip_flow(datapath, dstIP, srcIP, [], 1)

        return valid

    """
    Conversion between RYU and DPKT DNS packets
    """

    def convert_packet(self, data):
        dpkt_pkt = dpkt.ethernet.Ethernet(data).data.data
        dns_pkt = dpkt.dns.DNS(dpkt_pkt.data)
        return dns_pkt

    """
    Get a random virtual IP that is free (if none are free get the least accessed one)
    """
    def find_virtual_ip(self):
        # gets all the available IPs
        # get a random FREE ip from the list; if none are free, take the one that hasnt been used recently
        curr_contenders = None
        try:
            curr_contenders = random.choice([(k, v) for k, v in self.tracker.items() if not v])
        except:
            pass
        if not curr_contenders:
            curr_contenders = [self.usage[0]]

        # chooses a random one
        # c = random.choice(curr_contenders)
        return socket.inet_aton(curr_contenders[0]), curr_contenders[0]
