import csv
import re
import requests
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scrape(teams=[], rr=False):
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

    # Stats button
    nav_stats = driver.find_element(
        By.XPATH,
        "/html/body/div[2]/nav/div/div[2]/ul/li[5]/a"
    )

    nav_stats.click()

    # Select stats by team
    team_stats_link = driver.find_element(
        By.XPATH,
        "/html/body/div[2]/nav/div/div[2]/ul/li[5]/ul/li[3]/a"
    )

    team_stats_link.click()
    time.sleep(5)

    for i in team_keys:
        print(f'Trabajando en {stats[i]["name"]}...')

        div_place = 4

        try:
            team_select = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    "/html/body/div[4]/div/div/div[2]/div[2]/div/form/div[2]/select"
                ))
            )
        except:
            team_select = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    "/html/body/div[3]/div/div/div[2]/div[2]/div/form/div[2]/select"
                ))
            )
            div_place = 3

        # team_select = driver.find_element(
        #     By.XPATH,
        #     "/html/body/div[4]/div/div/div[2]/div[2]/div/form/div[2]/select"
        # )

        team_select = Select(team_select)

        team_select.select_by_value(str(stats[i]['id']))

        time.sleep(2)

        stats[i]['hitting'] = get_stats('hit', driver, div_place, rr=False)
        time.sleep(5)
        stats[i]['pitching'] = get_stats('pit', driver, div_place, rr=False)
        time.sleep(5)
        
    return stats

def get_stats(stats_type, driver, div_place, rr=False):

    type_select = driver.find_element(
        By.XPATH,
        f"/html/body/div[{div_place}]/div/div/div[2]/div[2]/div/form/div[4]/select"
    )
    
    # try:
    #     type_select = WebDriverWait(driver, 10).until(
    #         EC.visibility_of_element_located((
    #             By.XPATH,
    #             "/html/body/div[4]/div/div/div[2]/div[2]/div/form/div[4]/select"
    #         ))
    #     )
    # except:
    #     type_select = WebDriverWait(driver, 10).until(
    #         EC.visibility_of_element_located((
    #             By.XPATH,
    #             "/html/body/div[3]/div/div/div[2]/div[2]/div/form/div[4]/select"
    #         ))
    #     )   

    type_select = Select(type_select)

    if stats_type == 'hit':
        print('Hitting')
        type_select.select_by_value('hittings')
    elif stats_type == 'pit':
        print('Pitching')
        type_select.select_by_value('pitchings')

    time.sleep(5)

    player_rows = driver.find_elements(
        By.XPATH,
        f"/html/body/div[{div_place}]/div/div/div[2]/div[2]/div/div/div[1]/div/table/tbody/tr"
    )

    stats_cols = driver.find_elements(
        By.XPATH,
        f"/html/body/div[{div_place}]/div/div/div[2]/div[2]/div/div/div[1]/div/table/thead/tr/th"
    )

    # print('Columns')
    # print(stats_cols)

    headers = []

    for el in stats_cols:
        inner_data = el.find_element(
            By.XPATH,
            ".//a"
        )

        current_header = re.sub('<i.+</i>', '', inner_data.get_attribute('innerHTML'))
        headers.append(current_header.strip())

    # headers = [el.get_attribute('innerHTML').strip() for el in stats_cols]
    headers.insert(1, 'id')
    if stats_type == 'hit':
        headers.insert(2, 'POS')

    print('Headers')
    print(headers)

    all_player_stats = []
    all_player_stats.append(headers)

    for i in range(1, len(player_rows)):
        current_stats = []
        try:
            player_link = driver.find_element(
                By.XPATH,
                f"/html/body/div[{div_place}]/div/div/div[2]/div[2]/div/div/div[1]/div/table/tbody/tr[{i}]/td[1]/a"
            )
        except NoSuchElementException:
            break

        if stats_type == 'hit':
            player_pos = driver.find_element(
                By.XPATH,
                f"/html/body/div[{div_place}]/div/div/div[2]/div[2]/div/div/div[1]/div/table/tbody/tr[{i}]/td[1]/span"
            )

            player_pos = player_pos.get_attribute('innerHTML').strip()

        player_name = player_link.get_attribute('innerHTML')
        player_name = re.sub('[\*#]', '', player_name).strip()
        player_link = player_link.get_attribute('href')
        player_id = re.search('\d+', player_link).group()

        

        current_stats.append(player_name)
        current_stats.append(player_id)
        if stats_type == 'hit':
            current_stats.append(player_pos)

        current_player_stats_els = driver.find_elements(
            By.XPATH,
            f"/html/body/div[{div_place}]/div/div/div[2]/div[2]/div/div/div[1]/div/table/tbody/tr[{i}]/td"
        )

        current_player_stats_els.pop(0)

        for j, element in enumerate(current_player_stats_els):
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
                'h': stats[key]['pitching'][i][11],
                'ip': stats[key]['pitching'][i][10],
                'strikes': stats[key]['pitching'][i][17],
                'bb': stats[key]['pitching'][i][15],
                'cl': stats[key]['pitching'][i][13],
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
                    'h': stats[key]['pitching'][i][11],
                    'ip': stats[key]['pitching'][i][10],
                    'strikes': stats[key]['pitching'][i][17],
                    'bb': stats[key]['pitching'][i][15],
                    'cl': stats[key]['pitching'][i][13],
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