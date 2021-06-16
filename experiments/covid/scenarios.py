# Used in Simulation and Population classes

def scenario1():
    lockdown = False
    social_distancing_probability = 0.0
    masked_proportion = 0
    name = "scenario1"
    lockdown_threshold = 0.0
    airport = False
    return [lockdown, social_distancing_probability, masked_proportion, name, airport]


def scenario2():
    lockdown = True
    social_distancing_probability = 0.0 # original 0.2
    masked_proportion = 0.3
    name = "scenario2"
    lockdown_threshold = 0.1
    airport = False
    return [lockdown, social_distancing_probability, masked_proportion, name, lockdown_threshold, airport]


def scenario3():
    lockdown = True
    social_distancing_probability = 0.0 # original 0.8
    masked_proportion = 0.9
    name = "scenario3"
    lockdown_threshold = 0.05
    airport = False
    return [lockdown, social_distancing_probability, masked_proportion, name, lockdown_threshold, airport]

def scenario4():
    lockdown = False
    social_distancing_probability = 0.0 # original 0.8
    masked_proportion = 0.0
    name = "scenario4"
    lockdown_threshold = 0.0
    airport = True
    return [lockdown, social_distancing_probability, masked_proportion, name, lockdown_threshold, airport]