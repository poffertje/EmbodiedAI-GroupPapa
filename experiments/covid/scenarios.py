# Used in Simulation and Population classes

def scenario1():
    lockdown = False
    social_distancing_probability = 0.0
    masked_proportion = 0
    return [lockdown, social_distancing_probability, masked_proportion]


def scenario2():
    lockdown = True
    social_distancing_probability = 0.0
    masked_proportion = 0.3
    return [lockdown, social_distancing_probability, masked_proportion]


def scenario3():
    lockdown = True
    social_distancing_probability = 0.0
    masked_proportion = 0.9
    return [lockdown, social_distancing_probability, masked_proportion]
