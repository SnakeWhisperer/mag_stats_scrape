import csv
import re
import requests
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


def scrape(teams=[], rr=True):
    """_summary_

    Zulia: https://lvbp.com/equipo.php?team=692, 0
    Margarita: https://lvbp.com/equipo.php?team=697, 1
    Lara: https://lvbp.com/equipo.php?team=693, 2
    Anzoátegui: https://lvbp.com/equipo.php?team=694, 3
    Caracas: https://lvbp.com/equipo.php?team=695, 4
    Magallanes: https://lvbp.com/equipo.php?team=696, 5
    La Guaira: https://lvbp.com/equipo.php?team=698, 6
    Aragua: https://lvbp.com/equipo.php?team=699, 7
    """

    if not teams:
        print('No se seleccionó ningún equipo.')
        return

    teams_dict = {
        'zul': 0,
        'mar': 1,
        'lar': 2,
        'anz': 3,
        'car': 4,
        'mag': 5,
        'lag': 6,
        'ara': 7
    }

    team_keys = [teams_dict.get(team, None) for team in teams]

    stats = {
        0: {'name': 'Aguilas', 'hitting': [], 'pitching': [], 'id': 692},
        1: {'name': 'Bravos', 'hitting': [], 'pitching': [], 'id': 697},
        2: {'name': 'Cardenales', 'hitting': [], 'pitching': [], 'id': 693},
        3: {'name': 'Caribes', 'hitting': [], 'pitching': [], 'id': 694},
        4: {'name': 'Leones', 'hitting': [], 'pitching': [], 'id': 695},
        5: {'name': 'Navegantes', 'hitting': [], 'pitching': [], 'id': 696},
        6: {'name': 'Tiburones', 'hitting': [], 'pitching': [], 'id': 698},
        7: {'name': 'Tigres', 'hitting': [], 'pitching': [], 'id': 699}
    }

    DRIVER_PATH = 'C:/chromedriver.exe'
    options = Options()
    options.headless = False
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    driver.get('https://lvbp.com/')

    time.sleep(2)

    print(team_keys)
    # There are only 8 teams. Iterate from 0 to 7.
    for i in team_keys:
        print(i)
        # Click on the stats dropdown, then wait,
        # then click on the team name.
        nav_stats = driver.find_element(
            By.XPATH,
            # "//div[@id ='navbar']/ul/li[5]"
            "/html/body/div[2]/nav/div/div[2]/ul/li[5]/a"
        )
        nav_stats.click()
        time.sleep(1)

        # print('Current team: ', i)
        # team_link = driver.find_element(
        #     By.XPATH,
        #     # "//div[@id ='navbar']/ul/li[5]/ul/li[" + f"{12+i}" + "]"
        #     "/html/body/div[2]/nav/div/div[2]/ul/li[12]/ul/li[" + f"{1+i}" + "]"
        # )

        team_stats_link = driver.find_element(
            By.XPATH,
            "/html/body/div[2]/nav/div/div[2]/ul/li[5]/ul/li[3]/a"
        )

        # team_link.click()

        team_stats_link.click()
        time.sleep(1)
        print(f'Trabajando en {stats[i]["name"]}...')
        stats[i]['hitting'] = get_stats('bat', driver, stats[i]['id'], rr=rr)
        stats[i]['pitching'] = get_stats('pit', driver, stats[i]['id'], rr=rr)

    return stats






def scrape_team(team):
    teams_dict = {
        'zul': (0, 'https://lvbp.com/equipo.php?team=692'),
        'mar': (1, 'https://lvbp.com/equipo.php?team=697'),
        'lar': (2, 'https://lvbp.com/equipo.php?team=693'),
        'anz': (3, 'https://lvbp.com/equipo.php?team=694'),
        'car': (4, 'https://lvbp.com/equipo.php?team=695'),
        'mag': (5, 'https://lvbp.com/equipo.php?team=696'),
        'lag': (6, 'https://lvbp.com/equipo.php?team=698'),
        'ara': (7, 'https://lvbp.com/equipo.php?team=699')
    }

    DRIVER_PATH = 'C:/chromedriver.exe'
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    driver.get(teams_dict[team][1])

    print(f'Working on {team}')

    hitting_stats = get_stats('bat', driver)
    pitching_stats = get_stats('pit', driver)

    return hitting_stats, pitching_stats


def get_stats(stats_type, driver, team_id, rr=True):
    if rr:
        stats_type += '_l'

    team_select = driver.find_element(
        By.XPATH,
        "/html/body/div[4]/div/div/div[2]/div[2]/div/form/div[2]/select"
    )

    team_select = Select(team_select)

    team_select.select_by_value(str(team_id))

    player_rows = driver.find_elements(
        By.XPATH,
        # f"//div[@id='{stats_type}']/table/tbody/tr"
        "/html/body/div[4]/div/div/div[2]/div[2]/div/div/div[1]/div/table/tbody/tr"
    )

    print('Player rows')
    print(player_rows)

    stats_cols = driver.find_elements(
        By.XPATH,
        # f"//div[@id='{stats_type}']/table/thead/tr/th"
        "/html/body/div[4]/div/div/div[2]/div[2]/div/div/div[1]/div/table/thead/tr/th[1]"
    )

    headers = [el.get_attribute('innerHTML') for el in stats_cols]
    headers.insert(1, 'id')

    all_player_stats = []
    all_player_stats.append(headers)
    for i in range(1, len(player_rows)):
        current_stats = []
        try:
            player_link = driver.find_element(
                By.XPATH,
                f"//div[@id='{stats_type}']/table/tbody/tr[{i}]/td[1]/a"
            )
        except NoSuchElementException:
            break

        player_name = player_link.get_attribute('innerHTML')
        player_name = re.sub('[\*#]', '', player_name).strip()
        player_link = player_link.get_attribute('href')
        player_id = re.search('\d+', player_link).group()

        current_stats.append(player_name)
        current_stats.append(player_id)

        current_player_stats_els = driver.find_elements(
            By.XPATH,
            f"//div[@id='{stats_type}']/table/tbody/tr[{i}]/td"
        )

        current_player_stats_els.pop(0)

        for j, element in enumerate(current_player_stats_els):
            if stats_type == 'bat':
                current_val = re.sub(
                    '[^\w]',
                    '',
                    element.get_attribute('innerHTML')
                )
            else:
                current_val = element.get_attribute('innerHTML')

            current_stats.append(current_val)
        all_player_stats.append(current_stats)

    return all_player_stats


def dump_stats(stats):
    url = 'http://192.168.4.100/pizarra/scrapping/estadisticas.php'

    responses = ''

    for key in stats.keys():
        for i in range(1, len(stats[key]['hitting'])):
            responses += '\n' + stats[key]['hitting'][i][0]
            cleansed_hit_stats = {
                'proceso': 2,
                'posicion': stats[key]['hitting'][i][2],
                'ci': stats[key]['hitting'][i][10],
                'hr': stats[key]['hitting'][i][9],
                'peb': stats[key]['hitting'][i][18].replace('.', ''),
                'h': stats[key]['hitting'][i][6],
                'bb': stats[key]['hitting'][i][12],
                'vb': stats[key]['hitting'][i][4],
                'gp': stats[key]['hitting'][i][21],
                'dosb': stats[key]['hitting'][i][7],
                'tresb': stats[key]['hitting'][i][8],
                'sf': stats[key]['hitting'][i][16],
                'ave': stats[key]['hitting'][i][17].replace('.', ''),
                'slg': stats[key]['hitting'][i][19].replace('.', ''),
                'id': stats[key]['hitting'][i][1],
            }

            response = requests.post(url, data=cleansed_hit_stats)
            responses += '\n' + str(response) + '\n' + response.text + '\n\n'

            print(response.text)
            print(f'Jugador {stats[key]["hitting"][i][0]}.')
            print('\n')

        for i in range(1, len(stats[key]['pitching'])):
            responses += '\n' + stats[key]['pitching'][i][0]
            cleansed_pit_stats = {
                'proceso': 3,
                'posicion': 'P',
                'ganados': stats[key]['pitching'][i][2],
                'perdidos': stats[key]['pitching'][i][3],
                'salvados': stats[key]['pitching'][i][8],
                'ip': stats[key]['pitching'][i][9],
                'strikes': stats[key]['pitching'][i][17],
                'bb': stats[key]['pitching'][i][14],
                'cl': stats[key]['pitching'][i][12],
                'efe': stats[key]['pitching'][i][4],
                'id': stats[key]['pitching'][i][1]
            }

            response = requests.post(url, data=cleansed_pit_stats)
            responses += '\n' + str(response) + '\n' + response.text + '\n\n'

            print(response.text)
            print(f'Jugador {stats[key]["pitching"][i][0]}.')
            print('\n')

    all_stats = [cleansed_hit_stats, cleansed_pit_stats]
    return responses


def pre_dump_stats(stats):
    all_stats = []
    for key in stats.keys():
        for i in range(1, len(stats[key]['hitting'])):
            cleansed_hit_stats = {
                'proceso': 2,
                'posicion': stats[key]['hitting'][i][2],
                'ci': stats[key]['hitting'][i][10],
                'hr': stats[key]['hitting'][i][9],
                'peb': stats[key]['hitting'][i][18],
                'h': stats[key]['hitting'][i][6],
                'bb': stats[key]['hitting'][i][12],
                'vb': stats[key]['hitting'][i][4],
                'gp': stats[key]['hitting'][i][21],
                'dosb': stats[key]['hitting'][i][7],
                'tresb': stats[key]['hitting'][i][8],
                'sf': stats[key]['hitting'][i][16],
                'ave': stats[key]['hitting'][i][17],
                'slg': stats[key]['hitting'][i][19],
                'id': stats[key]['hitting'][i][1],
            }

            all_stats.append(cleansed_hit_stats)

            # response = requests.post(url, data=cleansed_hit_stats)

            # print(response.text)
            # print(f'Jugador {stats[key]["hitting"][i][0]}.')
            # print('\n')

        for i in range(1, len(stats[key]['pitching'])):
            cleansed_pit_stats = {
                'proceso': 3,
                'posicion': 'P',
                'ganados': stats[key]['pitching'][i][2],
                'perdidos': stats[key]['pitching'][i][3],
                'salvados': stats[key]['pitching'][i][8],
                'ip': stats[key]['pitching'][i][9],
                'strikes': stats[key]['pitching'][i][17],
                'bb': stats[key]['pitching'][i][14],
                'cl': stats[key]['pitching'][i][12],
                'efe': stats[key]['pitching'][i][4],
                'id': stats[key]['pitching'][i][1]
            }

            all_stats.append(cleansed_pit_stats)

            # response = requests.post(url, data=cleansed_pit_stats)

            # print(response.text)
            # print(f'Jugador {stats[key]["pitching"][i][0]}.')
            # print('\n')

    # all_stats = [cleansed_hit_stats, cleansed_pit_stats]

    return all_stats


def dump_player(stats, id):
    url = 'http://192.168.4.100/pizarra/scrapping/estadisticas.php'

    for key in stats.keys():
        for i in range(1, len(stats[key]['hitting'])):
            if id in stats[key]['hitting'][i]:
                cleansed_hit_stats = {
                    'proceso': 2,
                    'posicion': stats[key]['hitting'][i][2],
                    'ci': stats[key]['hitting'][i][10],
                    'hr': stats[key]['hitting'][i][9],
                    'peb': stats[key]['hitting'][i][18],
                    'h': stats[key]['hitting'][i][6],
                    'bb': stats[key]['hitting'][i][12],
                    'vb': stats[key]['hitting'][i][4],
                    'gp': stats[key]['hitting'][i][21],
                    'dosb': stats[key]['hitting'][i][7],
                    'tresb': stats[key]['hitting'][i][8],
                    'sf': stats[key]['hitting'][i][16],
                    'ave': stats[key]['hitting'][i][17],
                    'slg': stats[key]['hitting'][i][19],
                    'id': stats[key]['hitting'][i][1],
                }

                print(cleansed_hit_stats)
                response = requests.post(url, data=cleansed_hit_stats)
                print(response.text)
                break

        for i in range(1, len(stats[key]['pitching'])):
            if id in stats[key]['pitching'][i]:
                cleansed_pit_stats = {
                    'proceso': 3,
                    'posicion': 'P',
                    'ganados': stats[key]['pitching'][i][2],
                    'perdidos': stats[key]['pitching'][i][3],
                    'salvados': stats[key]['pitching'][i][8],
                    'ip': stats[key]['pitching'][i][9],
                    'strikes': stats[key]['pitching'][i][17],
                    'bb': stats[key]['pitching'][i][14],
                    'cl': stats[key]['pitching'][i][12],
                    'efe': stats[key]['pitching'][i][4],
                    'id': stats[key]['pitching'][i][1]
                }

                print(cleansed_pit_stats)
                response = requests.post(url, data=cleansed_pit_stats)
                print(response.text)
                break


def csv_dump(stats):
    for key in stats.keys():
        team_name = stats[key]['name']
        file_name = f'{team_name}_hitting.csv'

        with open(file_name, 'w+', newline='') as new_file:
            csv_writer = csv.writer(new_file)
            csv_writer.writerows(stats[key]['hitting'])

        file_name = f'{team_name}_pitching.csv'

        with open(file_name, 'w+', newline='') as new_file:
            csv_writer = csv.writer(new_file)
            csv_writer.writerows(stats[key]['pitching'])


def update_stats(teams=[]):
    stats = scrape(teams=teams)

    if stats is not None:
        log = dump_stats(stats)
    else:
        print('No se seleccionó ningún equipo.')

    return log


def check_stats(stats, teams=[]):

    teams_dict = {
        'zul': 0,
        'mar': 1,
        'lar': 2,
        'anz': 3,
        'car': 4,
        'mag': 5,
        'lag': 6,
        'ara': 7
    }

    for team in teams:
        team_pos = teams_dict[team]
        hitters_len = len(stats[team_pos]['hitting'])
        pitchers_len = len(stats[team_pos]['pitching'])

        for i in range(1, hitters_len):
            print(stats[team_pos]['hitting'][i][1])

        for i in range(1, pitchers_len):
            print(stats[team_pos]['pitching'][i][1])
