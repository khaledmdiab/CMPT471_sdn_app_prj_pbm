from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from webob import Response

from app_fw import FirewallApp
from app_l2 import L2ConnectivityApp
from app_te import TEApp

INSTANCE_NAME = 'prj_api'
GRAPH_PATH = './test_case/isp.graphml'

class SDNController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(SDNController, self).__init__(*args, **kwargs)
        self.datapaths = {}
        wsgi = kwargs['wsgi']
        wsgi.register(ControllerInterface, {INSTANCE_NAME: self})
        
        # The three apps initialized with None's
        self.app_fw = None
        self.app_l2 = None
        self.app_te = None

    def add_flow(self, datapath, match, actions, priority, hard_timeout=0):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = ofp_parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    hard_timeout=hard_timeout,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def on_state_change(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if not datapath.id in self.datapaths:
                self.logger.info('Register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.info('Unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def on_switch_features(self, ev):
        datapath = ev.msg.datapath
        self._install_table_miss(datapath)
        self.logger.info('Switch: %s Connected', datapath.id)

    def _install_table_miss(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        match = ofp_parser.OFPMatch()
        actions = [ofp_parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, match=match, actions=actions, priority=0)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def on_packet_in(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        dpid = datapath.id

        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocols(ethernet.ethernet)[0]
        dst_mac = eth_pkt.dst

        self.logger.info('Received a packet!')


class ControllerInterface(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(ControllerInterface, self).__init__(req, link, data, **config)
        self.controller = data[INSTANCE_NAME]

    @route('prj', '/firewall/start', methods=['POST'])
    def firewall_start(self, req, **kwargs):
        controller = self.controller
        input_file = req.POST.get('input_file', './test_case/firewall.json')
        # Initializes `app_fw` in `controller` and calls `from_json`
        # Calls `calculate_firewall_rules`
        # Returns status code 200
        controller.app_fw = FirewallApp(input_file, controller)
        controller.app_fw.from_json()
        controller.app_fw.calculate_firewall_rules()
        return Response(status=200)

    @route('prj', '/l2/start', methods=['GET', 'POST'])
    def l2_start(self, req, **kwargs):
        controller = self.controller
        # Initializes `app_l2` in `controller`
        # Calls `calculate_connectivity_rules`
        # Returns status code 200
        controller.app_l2 = L2ConnectivityApp(GRAPH_PATH, controller)
        controller.app_l2.calculate_connectivity_rules()
        return Response(status=200)

    @route('prj', '/te/start', methods=['POST'])
    def te_start(self, req, **kwargs):
        controller = self.controller
        input_file = req.POST.get('input_file', './test_case/te.json')
        # Initializes `app_te` in `controller` and calls `from_json`
        # Returns status code 200
        controller.app_te = TEApp(GRAPH_PATH, input_file, controller)
        controller.app_te.from_json()
        return Response(status=200)

    @route('prj', '/te/provision_pass_by_paths', methods=['GET', 'POST'])
    def te_provision_pass_by_paths(self, req, **kwargs):
        controller = self.controller
        # *if* `controller.app_te` is initialized
        #   Call `app_te.provision_pass_by_paths` 
        #   Return status code 200
        # Otherwise,
        #   Return status code 500
        if controller.app_te is None:
            return Response(status=500)
        controller.app_te.provision_pass_by_paths()
        return Response(status=200)
        
    @route('prj', '/te/provision_min_latency_paths', methods=['GET', 'POST'])
    def te_provision_min_latency_paths(self, req, **kwargs):
        controller = self.controller
        # *if* `controller.app_te` is initialized
        #   Call `app_te.provision_min_latency_paths` 
        #   Return status code 200
        # Otherwise,
        #   Return status code 500
        if controller.app_te is None:
            return Response(status=500)
        controller.app_te.provision_min_latency_paths()
        return Response(status=200)

    @route('prj', '/te/provision_max_bandwidth_paths', methods=['GET'])
    def te_provision_max_bandwidth_paths(self, req, **kwargs):
        controller = self.controller
        # BONUS
        # *if* `controller.app_te` is initialized
        #   Call `app_te.provision_max_bandwidth_paths` 
        #   Return status code 200
        # Otherwise,
        #   Return status code 500
        if controller.app_te is None:
            return Response(status=500)
        controller.app_te.provision_max_bandwidth_paths()
        return Response(status=200)