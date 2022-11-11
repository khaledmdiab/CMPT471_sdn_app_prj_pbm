import json
from json import JSONEncoder

from rule import Rule, Action, MatchPattern
from te_objs import PassByPathObjective, MinLatencyObjective, MaxBandwidthObjective

class DefaultEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, PassByPathObjective) or \
            isinstance(object, MinLatencyObjective) or \
            isinstance(object, MaxBandwidthObjective) or \
            isinstance(object, Rule) or \
            isinstance(object, Action) or \
            isinstance(object, MatchPattern):
            return object.__dict__
        else:
            return json.JSONEncoder.default(self, object)