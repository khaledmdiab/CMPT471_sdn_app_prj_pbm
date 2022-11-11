from app_l2 import L2ConnectivityApp

GRAPH_FILE = './test_case/isp.graphml'

app_l2 = L2ConnectivityApp(topo_file=GRAPH_FILE)
app_l2.calculate_connectivity_rules()

for rule in app_l2.rules:
    print(rule)
