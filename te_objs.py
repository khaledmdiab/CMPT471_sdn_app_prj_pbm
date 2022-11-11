class PassByPathObjective:
    def __init__(self, match_pattern, switches, symmetric=False):
        self.match_pattern = match_pattern
        self.switches = switches
        self.symmetric = symmetric

    def __str__(self):
        switches = ' -> '.join(str(sw) for sw in self.switches)
        if self.symmetric:
            switches_rev = ' -> '.join(reversed(str(sw) for sw in self.switches))
            return 'PassByPathObj: [%s] and [%s]\n\r\t%s' % (switches, switches_rev, self.match_pattern)
        return 'PassByPathObj: [%s]\n\r\t%s' % (switches, self.match_pattern)


class MinLatencyObjective:
    def __init__(self, match_pattern, src_switch, dst_switch, symmetric=False):
        self.match_pattern = match_pattern
        self.src_switch = src_switch
        self.dst_switch = dst_switch
        self.symmetric = symmetric

    def __str__(self):
        if self.symmetric:
            return 'MinLatencyObj: [%s->%s] and [%s->%s]\n\r\t%s' % (self.src_switch, self.dst_switch, self.dst_switch, self.src_switch, self.match_pattern)
        return 'MinLatencyObj: [%s->%s]\n\r\t%s' % (self.src_switch, self.dst_switch, self.match_pattern)


class MaxBandwidthObjective:
    def __init__(self, match_pattern, src_switch, dst_switch, symmetric=False):
        self.match_pattern = match_pattern
        self.src_switch = src_switch
        self.dst_switch = dst_switch
        self.symmetric = symmetric
    
    def __str__(self):
        if self.symmetric:
            return 'MaxBandwidthObj: [%s->%s] and [%s->%s]\n\r\t%s' % (self.src_switch, self.dst_switch, self.dst_switch, self.src_switch, self.match_pattern)
        return 'MaxBandwidthObj: [%s->%s]\n\r\t%s' % (self.src_switch, self.dst_switch, self.match_pattern)
