# Used in Simulation and Population classes

def scenario1():
    lockdown = False
    social_distancing_probability = 0.0
    masked_proportion = 0
    name = "scenario1"
    return [lockdown, social_distancing_probability, masked_proportion, name]


def scenario2():
    lockdown = True
    social_distancing_probability = 0.0
    masked_proportion = 0.3
    name = "scenario2"
    return [lockdown, social_distancing_probability, masked_proportion, name]


def scenario3():
    lockdown = True
    social_distancing_probability = 0.0
    masked_proportion = 0.9
    name = "scenario3"
    return [lockdown, social_distancing_probability, masked_proportion, name]
