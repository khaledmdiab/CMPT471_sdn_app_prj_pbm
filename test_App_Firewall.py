from rule import Rule, Action, ActionType, MatchPattern
from app_fw import FirewallApp

JSON_FILE = './test_case/firewall.json'

app_fw = FirewallApp(json_file=JSON_FILE)

# Rule 1: Drop all UDP traffic destined to port 80
pattern = MatchPattern(ip_proto=17, dst_port=80)
action = Action(action_type=ActionType.DROP)
rule = Rule(switch_id=1, match_pattern=pattern, action=action)
app_fw.add_rule(rule)

# Write the firewall policy to a file
app_fw.to_json(json_file=JSON_FILE)

# Read an existing policy file to a new object `new_app_fw`
new_app_fw = FirewallApp(json_file=JSON_FILE)
new_app_fw.from_json()
new_app_fw.calculate_firewall_rules()
for rule in new_app_fw.rules:
    print(rule)