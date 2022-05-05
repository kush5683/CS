from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.packet import *

class Phase2Switch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Phase2Switch, self).__init__(*args, **kwargs)

    # For phase two the controller should approve all traffic
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def react_to_packet_in(self, ev):

        ########### LAYOUT OF OVS PORTS #####################
        #                     _______________________________
        # OTHER_MACHINES <--> | Port_1 - |OVS| - Port_66534 | <--> Host 3 (running OVS)
        #                     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
        #####################################################

        # List of our VM's IPs
        ip_hosts = ["10.61.17.1", "10.61.17.2", "10.61.17.3", "10.61.17.4"]
        # List of our VM's MAC Addresses
        eth_hosts = ["52:54:00:00:03:4a","52:54:00:00:03:4b","52:54:00:00:03:4c","52:54:00:00:03:4d"]

        # This is a reprentation of the PACKET_IN message that the switch sent
        message = ev.msg

        # This is a datapath (docs say effectively a representation of the switch)
        datapath_of_switch = message.datapath

        # A reference to the switch's OpenFlow Protocol, used to access protocols and constants
        ofproto = datapath_of_switch.ofproto

        # This gets a packet representation of the packet sent to the switch (it's encapsulated in the PACKET_IN message)
        packt = packet.Packet(message.data)

        # This gets the MAC addresses involved
        prot = packt.get_protocol(ethernet.ethernet)

        # The source MAC address
        src = prot.src
        # The destination MAC address
        dst = prot.dst
        # Debugging print outs if the packets our from out VMs
        if src in eth_hosts:
             pass
#            print("\nPacket Received")
#            print("From: " + src + " Headed to: " + dst)
#            print("In port: " + str(message.in_port))

        ofp_parser = datapath_of_switch.ofproto_parser # a built in parser of the switch's protocol
        # If the dst is a broadcast MAC addr (src doesn't know the dst MAC)
        if(dst == "ff:ff:ff:ff:ff:ff"):
             # Then FLOOD
             out_port = ofproto.OFPP_FLOOD
        # If the dst is Host 3's MAC addr
        elif(dst == "52:54:00:00:03:4c"):
            # Then send it out the Host 3 port
            out_port = 65534
        # If it is other traffic
        else:
            # Send out port 1
            out_port = 1

        # Creation of action to send back to switch
        actions = [datapath_of_switch.ofproto_parser.OFPActionOutput(out_port)]

        # TODO here is where we would add a flow if there isn't one already. I don't think we need it for Phase 2 though.

        # This is for deciding if we need to send back the whole packet or just the
        # buffer id (if the switch has the packet stored)
        data = None
        if message.buffer_id == ofproto.OFP_NO_BUFFER: # if there is no buffer id
            data = message.data # then the switch doesn't remember the packet, so we have to send it the packet back

        # Craft our PACKET_OUT message
        out = ofp_parser.OFPPacketOut(datapath=datapath_of_switch, buffer_id=message.buffer_id, in_port=message.in_port, actions=actions, data=data)

        # Send the message
        datapath_of_switch.send_msg(out)
