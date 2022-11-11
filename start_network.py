"""
Creates a project topology using Mininet
"""
import sys
import atexit

from utils_net import mn_get_host_ip, mn_get_host_mac
from utils_ports import get_out_port_for_src, get_in_port_for_dst

import networkx as nx
from mininet.topo import Topo
from mininet.node import RemoteController
from mininet.link import TCLink
from mininet.util import custom
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.clean import cleanup
from mininet.log import lg

from scapy.all import sendp, send

from tabulate import tabulate
import crayons as cr

def read_isp_graph(file_path):
    graph = None
    try:
        graph = nx.read_graphml(file_path)
    except Exception as ex:
        print(ex)
    return graph


class ProjectTopology(Topo):
    def __init__(self, topo_file, *args, **kwargs):
        self.graph = read_isp_graph(topo_file)
        super(ProjectTopology, self).__init__(*args, **kwargs)
        
    def build(self):
        """ Creates a Mininet topology

        Effect:
            Creating final topology

        Returns:
            None
        """
        # Add switches, hosts and links based on self.graph
        # Using networkx:
        # self.graph is a networkx Graph object
        # A Graph has nodes and edges. 
        # Each node or edge may have additional data associated with it
        # To access all nodes with their data, 
        #       consider calling: self.graph.nodes(data=True)
        # To access all edges with their data, 
        #       consider calling: self.graph.edges.data()
        # Switch name is: sX, where X is the switch ID
        # Host name is: hX, where X is the host ID
        # Port Configuration:
        # * Port numbers start from 1
        # * A host has one port only (its number=1)
        # * The port at a switch with port=1 is the one connected to its host
        # * For each switch, the remaining ports are numbered ascendingly based on its neighbour switches
        # *** Check the `get_in_port_for_dst` and `get_out_port_for_src` functions for more details
        # Node and Edge Attributes
        # Each edge has bw and delay values:
        #       You *must* configure links of the Mininet network accordingly.
        # If a node has the attribute:
        ## 1. udp_server=True:, the corresponding *host* runs a UDP server.
        ##   The node *must* have a `udp_port` attribute as well.
        ## 2. tcp_server=True:, the corresponding *host* runs a TCP server.
        ##   The node may have a `tcp_port` attribute as well.

        for node, node_data in self.graph.nodes(data=True):
            switch_id = 's%s' % node
            host_id = 'h%s' % node
            host_ip = mn_get_host_ip(node)
            host_mac = mn_get_host_mac(node)
            self.addSwitch(switch_id)
            self.addHost(host_id, mac=host_mac, ip=host_ip)
            self.addLink(host_id, switch_id, port1=1, port2=1)

        for edge_tuple in self.graph.edges.data():
            p1 = 's%s' % edge_tuple[0]
            p2 = 's%s' % edge_tuple[1]
            tc_info = edge_tuple[2]
            src_port = get_out_port_for_src(self.graph, src=edge_tuple[0], dst=edge_tuple[1])
            dst_port = get_in_port_for_dst(self.graph, src=edge_tuple[0], dst=edge_tuple[1])
            delay = '%sms' % tc_info.pop('delay', 1)
            bw = int(tc_info.pop('bw', 1))
            self.addLink(p1, p2, port1=src_port, port2=dst_port, cls=TCLink, delay=delay, bw=bw)

class ProjectCLI(CLI):
    prompt = 'cmpt471> '

    helpStr = (
        'You may also send a command to a node using:\n'
        '  <node> command {args}\n'
        'For example:\n'
        '  cmpt471> h1 ifconfig\n'
        '\n'
        'The interpreter automatically substitutes IP addresses\n'
        'for node names when a node is the first arg, so commands\n'
        'like\n'
        '  cmpt471> h2 ping h3\n'
        'should work.\n'
        '\n'
        'Some character-oriented interactive commands require\n'
        'noecho:\n'
        '  cmpt471> noecho h2 vi foo.py\n'
        'However, starting up an xterm/gterm is generally better:\n'
        '  cmpt471> xterm h2\n\n'
    )

    def __init__(self, mininet):
        atexit.register(lambda: self.do_bye(None))

        CLI.__init__(self, mininet)

    def do_list_hosts(self, _line):
        """List hosts"""

        servers = []
        for host in self.mn.hosts:
            servers.append([cr.normal(host), cr.normal(host.IP()), cr.normal(host.MAC())])
        lg.output(tabulate(servers, headers=[cr.normal('Host', bold=True), cr.normal('IP', bold=True), cr.normal('MAC', bold=True)],
                           tablefmt='grid'))
        lg.output('\n')

    def do_list_switches(self, _line):
        """List switches"""

        switches = []
        for switch in self.mn.switches:
            connectedStr = cr.red('NO')
            if switch.connected():
                connectedStr = cr.green('YES')
            switches.append([cr.normal(switch), cr.normal(switch.dpid), connectedStr])

        lg.output(tabulate(switches, headers=[cr.normal('Switch', bold=True), cr.normal('Dpid', bold=True), cr.normal('Connected?', bold=True)],
                           tablefmt='grid'))
        lg.output('\n')

    def do_bye(self, _line):
        lg.output('Bye :)')
        lg.output('\n')

def ProjectNet(**kwargs):
    """ Creates the Project topology and Mininet network.

    Args:
        **kwargs: additional kwargs to the Mininet object

    Returns:
        The Mininet network with the corresponding topology.
        None if the topology file is invalid
    """
    topo_file = kwargs.pop('topo_file', 'isp.graphml')
    topo = ProjectTopology(topo_file=topo_file)
    network = Mininet(topo, controller=RemoteController, waitConnected=False, **kwargs)

    return network

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('sudo -E python3 ./start_network <topo_file_path>')
        exit(1)

    network = ProjectNet(topo_file=sys.argv[1])
    if not network:
        print('The Mininet network was not created!')
        exit(1)

    # 1. Set up ARP rules; no need for our switches to forward ARP pkts
    # 2. Use iperf3 to run the TCP and UDP servers
    #       You need to inspect the graph to identify the hosts and server ports.
    #       The default server port values are:
    #           TCP server: 80
    #           UDP server: 8080
    # 3. The iperf3 commands are (use the cmd() function in Mininet APIs):
    #       For a TCP server:
    #           'iperf3 -s -p %d -D --logfile %s-tcp-server.log' % (tcp_port, h.name)
    #       For a UDP server:
    #           'iperf3 -s -p %d -D --logfile %s-udp-server.log' % (udp_port, h.name)
    # 4. Add default gateways for hosts
    # 5. Diable IPv6 for hosts and switches
    graph = network.topo.graph
    for h in network.hosts:
        node_id = h.name[1:]
        has_tcp_server = graph.nodes[node_id].get('tcp_server', False)
        has_udp_server = graph.nodes[node_id].get('udp_server', False)
        
        if has_tcp_server:
            tcp_port = graph.nodes[node_id].get('tcp_port', 80)
            h.cmd('iperf3 -s -p %d -D --logfile %s-tcp-server.log' % (tcp_port, h.name))
        
        if has_udp_server:
            udp_port = graph.nodes[node_id].get('udp_port', 8080)
            h.cmd('iperf3 -s -p %d -D --logfile %s-udp-server.log' % (udp_port, h.name))

        # Set up ARP rules; no need for our switches to forward ARP pkts
        for h_other in network.hosts:
            if h != h_other:
                h.cmd('arp -s %s -i %s-eth1 %s' % (h_other.IP(), h, h_other.MAC()))
        # Add default gateways for h1 and h2, as they are in separate subnets
        h.cmd("ip route add default via %s" % h.IP())

        # Diable IPv6 for hosts and switches
        h.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        h.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        h.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
    
    for sw in network.switches:
        sw.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

    network.start()
    ProjectCLI(mininet=network)
    network.stop()
