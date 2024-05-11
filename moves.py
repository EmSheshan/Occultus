class Move:
    def __init__(self, name, hp_cost, mp_cost, power, critrate, type, element, target):
        self.name = name
        self.hp_cost = hp_cost
        self.mp_cost = mp_cost
        self.power = power
        self.critrate = critrate
        self.type = type
        self.element = element
        self.target = target
