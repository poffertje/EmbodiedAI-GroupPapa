# Used in Simulation and Population classes


def scenario1():
    lockdown = False
    social_distancing_probability = 0.0
    masked_proportion = 0
    name = "scenario 1"
    lockdown_threshold = 0.0
    airport = False
    return [lockdown, social_distancing_probability, masked_proportion, name, lockdown_threshold, airport]


# Four Cities: No lockdown, no masks
def scenario2():
    lockdown = False
    social_distancing_probability = 0.0
    masked_proportion = 0
    name = "scenario 2"
    lockdown_threshold = 0.0
    airport = False
    return [lockdown, social_distancing_probability, masked_proportion, name, lockdown_threshold, airport]


# Four Cities: Lockdown (threshold = 0.07), no masks
def scenario3():
    lockdown = True
    social_distancing_probability = 0.0  # original 0.2
    masked_proportion = 0.0
    name = "scenario 3"
    lockdown_threshold = 0.07
    airport = False
    return [lockdown, social_distancing_probability, masked_proportion, name, lockdown_threshold, airport]


# Four Cities: Lockdown (threshold = 0.07), masks
def scenario4():
    lockdown = True
    social_distancing_probability = 0.0  # original 0.8
    masked_proportion = 0.9
    name = "scenario 4"
    lockdown_threshold = 0.07
    airport = False
    return [lockdown, social_distancing_probability, masked_proportion, name, lockdown_threshold, airport]


# Strict Policy e.g. Singapore
def scenario5():
    lockdown = False
    social_distancing_probability = 0.0  # original 0.8
    masked_proportion = 0.9
    name = "scenario 5"
    lockdown_threshold = 0.0
    airport = True
    quarantine_time = 1400
    return [lockdown, social_distancing_probability, masked_proportion, name, lockdown_threshold, airport,
            quarantine_time]


# Semi-enforced Policy e.g. Netherlands
def scenario6():
    border = True
    lockdown = False
    social_distancing_probability = 0.0  # original 0.8
    masked_proportion = 0.3
    name = "scenario 6"
    lockdown_threshold = 0.0
    airport = False
    quarantine_time = 1000
    vaccine_type = "Sinovac"
    hospital = True
    return [lockdown, social_distancing_probability, masked_proportion, name, lockdown_threshold, airport,
            quarantine_time, vaccine_type, border, hospital]


# Relaxed Policy
def scenario7():
    lockdown = False
    social_distancing_probability = 0.0  # original 0.8
    masked_proportion = 0.0
    name = "scenario 7"
    lockdown_threshold = 0.0
    airport = True
    quarantine_time = 100
    return [lockdown, masked_proportion, name, lockdown_threshold, airport,
            quarantine_time]

#---------------------------------------------
# FINAL EXPERIMENTS
# ---------------------------------------------

# Base case:
def scenario8():
    border = True
    lockdown = False
    masked_proportion = 0.60
    name = "scenario 8"
    lockdown_threshold = 0.0
    airport = False
    quarantine_time = 1000
    vaccine_type = None
    hospital = True
    hospital_policy = False
    return [lockdown, masked_proportion, name, lockdown_threshold, airport,
            quarantine_time, vaccine_type, border, hospital, hospital_policy]

# Hospital Policy without vaccination
def scenario9():
    border = True
    lockdown = False
    masked_proportion = 0.60
    name = "scenario 9"
    lockdown_threshold = 0.0
    airport = False
    quarantine_time = 1000
    vaccine_type = None
    hospital = True
    hospital_policy = True
    return [lockdown, masked_proportion, name, lockdown_threshold, airport,
            quarantine_time, vaccine_type, border, hospital, hospital_policy]

# Hospital Policy with Sinovac
def scenario10():
    border = True
    lockdown = False
    masked_proportion = 0.60
    name = "scenario 10"
    lockdown_threshold = 0.0
    airport = False
    quarantine_time = 1000
    vaccine_type = "Sinovac"
    hospital = True
    hospital_policy = True
    return [lockdown, masked_proportion, name, lockdown_threshold, airport,
            quarantine_time, vaccine_type, border, hospital, hospital_policy]

# Hospital Policy with Pfizer
def scenario11():
    border = True
    lockdown = False
    masked_proportion = 0.60
    name = "scenario 11"
    lockdown_threshold = 0.0
    airport = False
    quarantine_time = 1000
    vaccine_type = 'Pfizer'
    hospital = True
    hospital_policy = True
    return [lockdown, masked_proportion, name, lockdown_threshold, airport,
            quarantine_time, vaccine_type, border, hospital, hospital_policy]


# Hospital Policy with Janssen
def scenario12():
    border = True
    lockdown = False
    masked_proportion = 0.60
    name = "scenario 12"
    lockdown_threshold = 0.0
    airport = False
    quarantine_time = 1000
    vaccine_type = 'Janssen'
    hospital = True
    hospital_policy = True
    return [lockdown, masked_proportion, name, lockdown_threshold, airport,
            quarantine_time, vaccine_type, border, hospital, hospital_policy]