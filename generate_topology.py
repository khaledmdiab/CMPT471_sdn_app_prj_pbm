from networkx import nx

# A node *may* have the following attributes:
#   udp_server and udp_port to create a UDP server
#   tcp_server and tcp_port to create a TCP server

# An edge *must* have the following attributes:
#   bw: link bandwidth (in Mbps)
#   delay: link delay in milliseconds

graph = nx.Graph()
graph.add_node(1)
# Used to test the given firewall policy
graph.add_node(3, udp_server=True, udp_port=80)

# Used to test the given pass-by-path objective
graph.add_node(5, tcp_server=True, tcp_port=5050)
# Used to test the given min-latency objective
graph.add_node(6, udp_server=True, udp_port=5050)

graph.add_edge(1, 2, delay=10, bw=100)
graph.add_edge(1, 4, delay=5, bw=50)

graph.add_edge(2, 3, delay=10, bw=100)
graph.add_edge(2, 4, delay=3, bw=50)
graph.add_edge(2, 5, delay=3, bw=50)

graph.add_edge(3, 5, delay=5, bw=10)
graph.add_edge(3, 6, delay=10, bw=100)

graph.add_edge(4, 5, delay=1, bw=10)

graph.add_edge(5, 6, delay=3, bw=100)

nx.write_graphml(graph, './test_case/isp.graphml')