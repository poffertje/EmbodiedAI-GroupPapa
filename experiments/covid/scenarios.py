# Used in Simulation and Population classes


def scenario1():
    lockdown = False
    social_distancing_probability = 0.0
    masked_proportion = 0
    name = "scenario1"
    lockdown_threshold = 0.0
    airport = False
    return [lockdown, social_distancing_probability, masked_proportion, name, lockdown_threshold, airport]


# Four Cities: No lockdown, no masks
def scenario2():
    lockdown = False
    social_distancing_probability = 0.0
    masked_proportion = 0
    name = "scenario2"
    lockdown_threshold = 0.0
    airport = False
    return [lockdown, social_distancing_probability, masked_proportion, name, lockdown_threshold, airport]


# Four Cities: Lockdown (threshold = 0.07), no masks
def scenario3():
    lockdown = True
    social_distancing_probability = 0.0  # original 0.2
    masked_proportion = 0.0
    name = "scenario3"
    lockdown_threshold = 0.07
    airport = False
    return [lockdown, social_distancing_probability, masked_proportion, name, lockdown_threshold, airport]


# Four Cities: Lockdown (threshold = 0.07), masks
def scenario4():
    lockdown = True
    social_distancing_probability = 0.0  # original 0.8
    masked_proportion = 0.9
    name = "scenario4"
    lockdown_threshold = 0.07
    airport = False
    return [lockdown, social_distancing_probability, masked_proportion, name, lockdown_threshold, airport]


# Strict Policy e.g. Singapore
def scenario5():
    lockdown = False
    social_distancing_probability = 0.0  # original 0.8
    masked_proportion = 0.9
    name = "scenario5"
    lockdown_threshold = 0.0
    airport = True
    quarantine_time = 1400
    return [lockdown, social_distancing_probability, masked_proportion, name, lockdown_threshold, airport,
            quarantine_time]


# Semi-enforced Policy e.g. Netherlands
def scenario6():
    lockdown = False
    social_distancing_probability = 0.0  # original 0.8
    masked_proportion = 0.3
    name = "scenario6"
    lockdown_threshold = 0.0
    airport = True
    quarantine_time = 1000
    return [lockdown, social_distancing_probability, masked_proportion, name, lockdown_threshold, airport,
            quarantine_time]


# Relaxed Policy
def scenario7():
    lockdown = False
    social_distancing_probability = 0.0  # original 0.8
    masked_proportion = 0.0
    name = "scenario7"
    lockdown_threshold = 0.0
    airport = True
    quarantine_time = 100
    return [lockdown, social_distancing_probability, masked_proportion, name, lockdown_threshold, airport,
            quarantine_time]
