with open('ECodes.h', 'r') as file:
    lines = file.readlines()
    splited = [line.split() for line in lines]
    error_codes = {line[4]: line[2] for line in splited}