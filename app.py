from abc import ABC, abstractmethod

import networkx as nx

from utils_ports import find_ports_per_switch
from rule import Action, ActionType, Rule, MatchPattern


class NetworkApp(ABC):
    def __init__(self, topo_file, json_file, of_controller, priority):
        self.topo_file = topo_file
        self.topo = None
        if self.topo_file:
            self.topo = nx.read_graphml(topo_file)
        self.json_file = json_file
        self.of_controller = of_controller
        self.priority = priority
        self.rules = [] # list of OpenFlow Rule objects to be sent to switches

    # Send the `rule` to a specific Ryu's `datapath`
    # Notice that this function should be called by `self.send_openflow_rules`
    # The goal is to translate our object model (Rule, Action, MatchPattern) to Ryu's:
    # First, the function needs to translate the `match_pattern` to OpenFlow `kwargs`
    #       of_match = ofp_parser.OFPMatch(**kwargs)
    # Second, it needs to decide the action based on `action_type`` and `out_port`
    #       of_actions = [...]
    # Finally, it should call:
    #       self.of_controller.add_flow(datapath, match=of_match, actions=of_actions, priority=self.priority)
    def send_openflow_rules_to_dp(self, rule, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        match_pattern = rule.match_pattern
        src_mac = match_pattern.src_mac
        dst_mac = match_pattern.dst_mac
        mac_proto = match_pattern.mac_proto
        ip_proto = match_pattern.ip_proto
        src_ip = match_pattern.src_ip
        dst_ip = match_pattern.dst_ip
        src_port = match_pattern.src_port
        dst_port = match_pattern.dst_port
        in_port = match_pattern.in_port
        kwargs = {'eth_type': 0x800}
        
        if src_mac:
            kwargs['eth_src'] = src_mac
        if dst_mac:
            kwargs['eth_dst'] = dst_mac
        if mac_proto:
            kwargs['eth_type'] = mac_proto
        if src_ip:
            kwargs['ipv4_src'] = src_ip
        if dst_ip:
            kwargs['ipv4_dst'] = dst_ip
        if in_port:
            kwargs['in_port'] = in_port
        if ip_proto:
            kwargs['ip_proto'] = ip_proto
            if ip_proto == 6:
                if src_port:
                    kwargs['tcp_src'] = src_port
                if dst_port:
                    kwargs['tcp_dst'] = dst_port
            elif ip_proto == 17:
                if src_port:
                    kwargs['udp_src'] = src_port
                if dst_port:
                    kwargs['udp_dst'] = dst_port

        of_match = ofp_parser.OFPMatch(**kwargs)
        if rule.action.action_type == ActionType.DROP:
            self.of_controller.add_flow(datapath, match=of_match, actions=[], priority=self.priority)
        elif rule.action.action_type == ActionType.CONTROLLER:
            of_actions = [ofp_parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)]
            self.of_controller.add_flow(datapath, match=of_match, actions=of_actions, priority=self.priority)
        elif rule.action.action_type == ActionType.FORWARD:
            of_actions = [ofp_parser.OFPActionOutput(rule.action.out_port)]
            self.of_controller.add_flow(datapath, match=of_match, actions=of_actions, priority=self.priority)
    
    # Send the OpenFlow rules in `self.rules` to corresponding switches
    def send_openflow_rules(self):
        for rule in self.rules:
            dpid = rule.switch_id
            if self.of_controller:
                datapath = self.of_controller.datapaths.get(dpid, None)
                if datapath:
                    self.send_openflow_rules_to_dp(rule, datapath)
    
    # Given a `path` and a `match_pattern` for every switch along the path:
    # Calculate the list of OpenFlow rules representing this path
    # If include_in_port=True, then the `match_pattern` should include the in_port from `find_ports_per_switch`
    def calculate_rules_for_path(self, path, match_pattern, include_in_port=True):
        rules = []
        segments = find_ports_per_switch(self.topo, path) 
        for path_seg in segments:
            switch_id = path_seg[0]
            in_port = path_seg[1]
            out_port = path_seg[2]
            if include_in_port:
                match_pattern.in_port = in_port
            pattern = MatchPattern(**match_pattern.__dict__)
            action = Action(ActionType.FORWARD, out_port=out_port)
            rule = Rule(switch_id=int(switch_id), match_pattern=pattern, action=action)
            rules.append(rule)
        return rules

    def add_rule(self, rule):
        self.rules.append(rule)
    
    @abstractmethod
    def to_json(self, json_file):
        pass
    
    @abstractmethod
    def from_json(self, json_file):
        pass

    # Used to react to changes in the network (the controller notifies the App)
    @abstractmethod
    def on_notified(self, **kwargs):
        pass