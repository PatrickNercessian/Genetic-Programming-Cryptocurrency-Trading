class Variable:
    def __init__(self, name: str, v_type, lower_bound, upper_bound):
        self.name = name
        self.v_type = v_type
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
