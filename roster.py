import re

from pdfminer.high_level import extract_text


def read_roster(file_name):
    text = extract_text(file_name)
    text_list = text.split('\n')
    numbers = []
    names = []
    positions = []
    state = None
    get_state = False

    for i, line in enumerate(text_list):
        if not line:
            get_state = True
            continue

        if get_state:
            get_state = False
            # Numbers
            if line == '#':
                state = 1
                continue
            # Names
            elif line == 'PLAYER':
                state = 2
                continue
            # Positions
            elif line == 'POSITION':
                state = 3
                continue

            else:
                state = None
                continue

        if state == 1:
            numbers.append(line)
        elif state == 2:
            names.append(line)
        elif state == 3:
            positions.append(line)

    numbers = numbers[:-8]
    full_names = []
    for name in names:
        last = re.search('^\w+', name).group()
        first = re.search('\w+$', name).group()
        full_names.append([first, last])
    players = [player for player in zip(numbers, full_names, positions)]

    return players