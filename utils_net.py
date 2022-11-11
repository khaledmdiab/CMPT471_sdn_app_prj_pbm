from netaddr import *

IP_BASE = '10.0.0.0/24'

def get_mac(i, j=0):
    assert isinstance(i, int) and i > 0
    assert isinstance(j, int) and j >= 0
    mac_i = hex(i)
    mac_j = hex(j)
    non_zero_mac_i = mac_i[2:]
    non_zero_mac_j = mac_j[2:]
    assert 0 < len(non_zero_mac_i) <= 6
    assert 0 < len(non_zero_mac_j) <= 6
    if non_zero_mac_j == '0':
        mac_address = non_zero_mac_i.zfill(12)
    else:
        mac_address = non_zero_mac_i.zfill(6) + non_zero_mac_j.zfill(6)
    mac_address_list = [mac_address[i:i + 2] for i in range(0, len(mac_address), 2)]
    return ':'.join(mac_address_list)

def get_ip(i, base):
    assert isinstance(i, int) and i > 0
    ip_base = IPNetwork(base)
    return str(IPAddress(int(ip_base.ip) + i))

def mn_get_host_mac(i):
    """ Returns MAC address given a Mininet host id

    Args:
        i (int): node id, i > 0

    Returns:
        MAC address (str)
    """
    if isinstance(i, str):
        i = int(i)
    assert i > 0
    return get_mac(i)


def mn_get_host_ip(i, base=IP_BASE):
    """ Returns IPv4 address given a Mininet switch id

    Args:
        base (str): IP network address in CIDR format
        i (int): node id, i > 0

    Returns:
        IPv4 address (str)
    """
    if isinstance(i, str):
        i = int(i)
    assert i > 0
    return get_ip(i, base)
