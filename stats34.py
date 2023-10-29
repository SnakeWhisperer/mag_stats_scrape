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

    print('Headers')
    print(headers)

    all_player_stats = []
    all_player_stats.append(headers)

    # for i in range(1, len(player_rows)):
    #     current_stats = []
    #     try:
    #         player_link = driver.find_element(
    #             By.XPATH,

    #         )