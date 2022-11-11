from enum import Enum
from utils_fmt import format_without_nones

def parse_action(d):
    if 'action_type' in d:
        return {
            'action_type': getattr(ActionType, d['action_type']),
            'out_port': d.get('out_port', None)
            }
    return d

class MatchPattern:
    """
    A class representing the OpenFlow matching pattern.
    For simplicity, our APIs support 9 header fields from the OpenFlow protocol.
    """
    def __init__(self, src_mac=None,
                        dst_mac=None,
                        mac_proto=0x800,
                        ip_proto=None, 
                        src_ip=None,
                        dst_ip=None,
                        src_port=None, 
                        dst_port=None,
                        in_port=None):
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.mac_proto = mac_proto
        self.ip_proto = ip_proto
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port 
        self.dst_port = dst_port
        self.in_port = in_port
    
    def __str__(self):
        return format_without_nones('src_mac={}, dst_mac={}, mac_proto={}, ip_proto={}, src_ip={}, dst_ip={}, src_port={}, dst_port={}, in_port={}', 
                                    self.src_mac, self.dst_mac, 
                                    self.mac_proto, self.ip_proto, 
                                    self.src_ip, self.dst_ip, 
                                    self.src_port, self.dst_port, 
                                    self.in_port)

class ActionType(str, Enum):
    FORWARD = 'FORWARD'
    DROP = 'DROP'
    CONTROLLER = 'CONTROLLER'

class Action:
    """
    Our APIs support three actions (check ActionType): 
    1. Forward a pkt to a specific `out_port`
    2. Drop a pkt
    3. Send the pkt to the controller for further processing
    if `action_type` is DROP or CONTROLLER, `out_port` is always None
    if `action_type` is FORWARD, `out_port` must be an integer value > 0
    """
    def __init__(self, action_type, out_port=None):
        self.action_type = action_type
        self.out_port = out_port

    def __str__(self):
        if self.out_port:
            return '%s, OutPort=%d' % (self.action_type, self.out_port) 
        return '%s' % self.action_type

class Rule:
    """
    A Rule object represents an OpenFlow flow rule. 
    If a pkt matches the `match_pattern`, the `action` will be executed at switch `switch_id`
    """
    def __init__(self, switch_id, match_pattern, action):
        self.switch_id = switch_id
        self.match_pattern = match_pattern
        self.action = action
    
    def __str__(self):
        return 'Switch: %s\n\r\tPattern: %s\n\r\tAction: %s' % (self.switch_id, self.match_pattern, self.action)
