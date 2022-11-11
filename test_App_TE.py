from rule import MatchPattern
from app_te import TEApp
from te_objs import PassByPathObjective, MinLatencyObjective

JSON_FILE = './test_case/te.json'
GRAPH_FILE = './test_case/isp.graphml'

app_te = TEApp(topo_file=GRAPH_FILE, json_file=JSON_FILE)

# Obj 1: All TCP traffic from '10.0.0.2' to '10.0.0.5' should go through switches 2->4->5
pattern = MatchPattern(ip_proto=6, src_ip='10.0.0.2', dst_ip='10.0.0.5')
pass_by_obj = PassByPathObjective(match_pattern=pattern, switches=[2, 4, 5])
app_te.add_pass_by_path_obj(pass_by_obj)

# Obj 2: All TCP traffic from '10.0.0.5' to '10.0.0.2' should go through switches 5->4->2
pattern = MatchPattern(ip_proto=6, src_ip='10.0.0.5', dst_ip='10.0.0.2')
pass_by_obj = PassByPathObjective(match_pattern=pattern, switches=[5, 4, 2])
app_te.add_pass_by_path_obj(pass_by_obj)

# Obj 3: All UDP traffic from switch 1 to switch 6 and in the reverse direction should go through min-latency paths
pattern = MatchPattern(ip_proto=17)
min_lat_obj = MinLatencyObjective(pattern, src_switch=1, dst_switch=6, symmetric=True)
app_te.add_min_latency_obj(min_lat_obj)

# Write the objectives (not the OpenFlow rules) to a JSON file
app_te.to_json(json_file=JSON_FILE)

# Write an existing objectives file to a new object `new_app_te`
new_app_te = TEApp(topo_file=GRAPH_FILE, json_file=JSON_FILE)
new_app_te.from_json()

# Calculate the OpenFlow rules for PassByPaths objectives
new_app_te.provision_pass_by_paths()
print('Pass By Paths Rules:')
for rule in new_app_te.rules:
    print(rule)

print()

# Calculate the OpenFlow rules for MinLatency objectives
new_app_te.provision_min_latency_paths()
print('Min-latency Paths Rules:')
for rule in new_app_te.rules:
    print(rule)