

# For a link connected by a src-dst, return the output port at src from src to dst
def get_out_port_for_src(graph, src, dst):
    start_port = 2
    for n2 in sorted(graph.neighbors(src)):
        if n2 == dst:
            return start_port
        start_port += 1
    return None

# For a link connected by a src-dst, return the input port at dst from src to dst
def get_in_port_for_dst(graph, src, dst):
    start_port = 2
    for n2 in sorted(graph.neighbors(dst)):
        if n2 == src:
            return start_port
        start_port += 1
    return None

# Find the input and output ports for every switch along a `path`
# The output is a list of tuples of (switch_id, in_port, out_port).
def find_ports_per_switch(graph, path):
    path_with_ports = []
    pairs = []
    prev_node = None
    for node in path:
        if prev_node != None and prev_node != node:
            pairs.append((prev_node, node))
        prev_node = node

    in_port = 1
    for n1, n2 in pairs:
        out_port = get_out_port_for_src(graph, n1, n2)
        path_with_ports.append((n1, in_port, out_port))
        in_port = get_in_port_for_dst(graph, n1, n2)
    path_with_ports.append((pairs[-1][-1], in_port, 1))

    return path_with_ports