import networkx as nx

from app import NetworkApp
from rule import Action, ActionType, Rule, MatchPattern
from utils_net import mn_get_host_mac

class L2ConnectivityApp(NetworkApp):
    def __init__(self, topo_file, of_controller=None, priority=1):
        super(L2ConnectivityApp, self).__init__(topo_file, None, of_controller, priority)

    # This function calculates the L2 connectivity rules based on the shortest path per each switch pair
    # The *shortest* refers to the minimum number of links between the switch pair
    # Notice that the rules need to handle pkts destined to hosts connected to switches as well
    # To calculate a shortest path, check the function `networkx.shortest_path` in the networkx package
    # The function should call `self.send_openflow_rules()` at the end
    def calculate_connectivity_rules(self):
        self.rules = []
        
        for n1 in self.topo.nodes():
            pattern = MatchPattern(dst_mac=mn_get_host_mac(n1))
            action = Action(action_type=ActionType.FORWARD, out_port=1)
            rule = Rule(switch_id=int(n1), match_pattern=pattern, action=action)
            self.add_rule(rule)

        for n1 in self.topo.nodes():
            for n2 in self.topo.nodes():
                if n1 != n2:
                    pattern = MatchPattern(dst_mac=mn_get_host_mac(n2))
                    path = nx.shortest_path(self.topo, source=n1, target=n2)
                    rules = self.calculate_rules_for_path(path, pattern, include_in_port=False)
                    self.add_rule(rules[0])
        
        self.send_openflow_rules()
    
    # This function has no implementation
    def from_json(self):
        pass
    
    # This function has no implementation
    def to_json(self, json_file):
        pass
    
    # BONUS: Used to react to changes in the network (the controller notifies the App)
    def on_notified(self, **kwargs):
        pass