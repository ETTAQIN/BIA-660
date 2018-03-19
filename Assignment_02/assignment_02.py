from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import pandas as pd
import time
import random
import bs4
import sys
import http.client, urllib.request, urllib.parse, urllib.error, base64
import selenium

'''
1. Which team had the most homeruns in the regular season of 2015? Print the full team name.

2. Which league (AL or NL) had the greatest average number of homeruns…
    a) in the regular season of 2015? Please give the league name and the average number of homeruns.
    b) in the regular season of 2015 in the first inning? Please give the league name and the average number of homeruns.
    
3. What is the name of the player with the best overall batting average in the 2017 regular season that played for the New York Yankees, who
    a) had at least 30 at bats? Please give his full name and position.
    b) played in the outfield (RF, CF, LF)? Please give his full name and position.
    
4. Which player in the American League had the most at bats in the 2015 regular season? Please give his full name, full team name, and position.

5. Which players from the 2014 All-star game were born in Latin America (google a country list)? Please give their full name and the full name of the team they play for.

6. Please print the 2016 regular season schedule for the Houston Astros in chronological order. Each line printed to the screen should be in the following format:
    <opponent Team Name> <game date> <stadium name> <city>, <state>
'''

driver = webdriver.Chrome(executable_path = './chromedriver')


def q1():
    data_div = driver.find_element_by_id('datagrid')
    data_html = data_div.get_attribute('innerHTML')
    soup = bs4.BeautifulSoup(data_html, 'html5lib')
    team_divs = soup.find_all('tr',attrs={'tabindex':'0'})
    data_set = []
    for a in team_divs:
        team_name = a.find('td', attrs={'class':'dg-team_full'}).text
        league = a.find('td', attrs={'class':'dg-league'}).text
        hr = a.find('td', attrs={'class':'dg-hr'}).text
        data_set.append((team_name, league, hr))
    df = pd.DataFrame(data=data_set, columns=['TeamName', 'League', 'HR'])
    df.to_csv('question1&2a.csv', index=False, header=False)
    print(data_set[0][0], 'had the most homeruns in the regular season of 2015.')


def q2a():
    df = pd.read_csv('question1&2a.csv', names=['TeamName', 'League', 'HR'])
    al = df['HR'][df['League'] == 'AL'].values
    al = sum(al)/len(al)
    nl = df['HR'][df['League'] == 'NL'].values
    nl = sum(nl)/len(nl)
    if al > nl:
        print('AL had the greatest average number of homeruns in the regular season of 2015. Their average is', al, "which is larger than their opponents'", nl)
    else:
        print('NL had the greatest average number of homeruns in the regular season of 2015. Their average is', nl, "which is larger than their opponents'", al)


def q2b():
    data_div = driver.find_element_by_id('datagrid')
    data_html = data_div.get_attribute('innerHTML')
    soup = bs4.BeautifulSoup(data_html, 'html5lib')
    team_divs = soup.find_all('tr', attrs={'tabindex': '0'})
    data_set = []
    for a in team_divs:
        team_name = a.find('td', attrs={'class': 'dg-team_full'}).text
        league = a.find('td', attrs={'class': 'dg-league'}).text
        hr = a.find('td', attrs={'class': 'dg-hr'}).text
        data_set.append((team_name, league, hr))
    df = pd.DataFrame(data=data_set, columns=['TeamName', 'League', 'HR'])
    df.to_csv('question2b.csv', index=False, header=False)
    al = df['HR'][df['League'] == 'AL'].values
    al = list(map(int, al))
    al = sum(al) / len(al)
    nl = df['HR'][df['League'] == 'NL'].values
    nl = list(map(int, nl))
    nl = sum(nl) / len(nl)
    if al > nl:
        print('AL had the greatest average number of homeruns in the regular season of 2015 in the first inning. Their average is', al,
              "which is larger than their opponents'", nl)
    else:
        print('NL had the greatest average number of homeruns in the regular season of 2015 in the first inning. Their average is', nl,
              "which is larger than their opponents'", al)


def q3a():
    data_div = driver.find_element_by_id('datagrid')
    data_html = data_div.get_attribute('innerHTML')
    soup = bs4.BeautifulSoup(data_html, 'html5lib')
    player_divs = soup.find_all('tr', attrs={'tabindex': '0'})
    data_set = []
    for a in player_divs:
        player_name = a.find('td', attrs={'class': 'dg-name_display_last_init'}).text
        pos = a.find('td', attrs={'class': 'dg-pos'}).text
        ab = a.find('td', attrs={'class': 'dg-ab'}).text
        avg = a.find('td', attrs={'class': 'dg-avg'}).text
        data_set.append((player_name[1:], pos, ab, avg))
    df = pd.DataFrame(data=data_set, columns=['PlayerName', 'Position', 'AtBats', 'OverallBattingAverage'])
    df.to_csv('question3a&3b.csv', index=False, header=False)
    df = pd.read_csv('question3a&3b.csv', names=['PlayerName', 'Position', 'AtBats', 'OverallBattingAverage'])
    playerName = df['PlayerName'][df['AtBats'] >= 30].values
    playerPos = df['Position'][df['AtBats'] >= 30].values
    player_link = driver.find_element_by_link_text(playerName[0])
    move_click(player_link)
    sleep()
    playerName = driver.find_element_by_class_name('player-bio')
    name_html = playerName.get_attribute('innerHTML')
    soup = bs4.BeautifulSoup(name_html, 'html5lib')
    playerName = soup.find('li').text.split(':')
    playerName = playerName[1]
    print(playerName[1:], 'had the best overall batting average in the 2017 regular season that played for the New York Yankees, who had at least 30 at bats. His position is', playerPos[0])
    driver.back()


def q3b():
    df = pd.read_csv('question3a&3b.csv', names=['PlayerName', 'Position', 'AtBats', 'OverallBattingAverage'])
    playerName = df['PlayerName'][(df['Position'] == 'RF') | (df['Position'] == 'CF') | (df['Position'] == 'LF')].values
    playerPos = df['Position'][(df['Position'] == 'RF') | (df['Position'] == 'CF') | (df['Position'] == 'LF')].values
    player_link = driver.find_element_by_link_text(playerName[0])
    move_click(player_link)
    sleep()
    playerName = driver.find_element_by_class_name('player-bio')
    name_html = playerName.get_attribute('innerHTML')
    soup = bs4.BeautifulSoup(name_html, 'html5lib')
    playerName = soup.find('li').text.split(':')
    playerName = playerName[1]
    print(playerName[1:], 'had the best overall batting average in the 2017 regular season that played for the New York Yankees, whose position is', playerPos[0])
    driver.back()


def q4():
    data_div = driver.find_element_by_id('datagrid')
    data_html = data_div.get_attribute('innerHTML')
    soup = bs4.BeautifulSoup(data_html, 'html5lib')
    player_divs = soup.find_all('tr', attrs={'tabindex': '0'})
    data_set = []
    for a in player_divs:
        player_name = a.find('td', attrs={'class': 'dg-name_display_last_init'}).text
        pos = a.find('td', attrs={'class': 'dg-pos'}).text
        ab = a.find('td', attrs={'class': 'dg-ab'}).text
        data_set.append((player_name[1:], pos, ab))
    while click_next_page_for_stats():
        data_div = driver.find_element_by_id('datagrid')
        data_html = data_div.get_attribute('innerHTML')
        soup = bs4.BeautifulSoup(data_html, 'html5lib')
        player_divs = soup.find_all('tr', attrs={'tabindex': '0'})
        for a in player_divs:
            player_name = a.find('td', attrs={'class': 'dg-name_display_last_init'}).text
            pos = a.find('td', attrs={'class': 'dg-pos'}).text
            ab = a.find('td', attrs={'class': 'dg-ab'}).text
            data_set.append((player_name[1:], pos, ab))
    df = pd.DataFrame(data=data_set, columns=['PlayerName', 'Position', 'AtBats'])
    df.to_csv('question4.csv', index=False, header=False)
    df = pd.read_csv('question4.csv', names=['PlayerName', 'Position', 'AtBats'])
    playerName = df['PlayerName'].values
    go_first = driver.find_element_by_class_name('paginationWidget-first')
    move_click(go_first)
    sleep()
    player_link = driver.find_element_by_link_text(playerName[0])
    move_click(player_link)
    sleep()

    player_vital = driver.find_element_by_class_name('player-vitals')
    data_html = player_vital.get_attribute('innerHTML')
    soup = bs4.BeautifulSoup(data_html, 'html5lib')
    playerPos = soup.find('li').text

    playerName = driver.find_element_by_class_name('player-bio')
    name_html = playerName.get_attribute('innerHTML')
    soup = bs4.BeautifulSoup(name_html, 'html5lib')
    playerName = soup.find('li').text.split(':')
    playerName = playerName[1]

    drop_down = driver.find_element_by_xpath("//div[contains(@class, 'dropdown') and contains(@class, 'team')]")
    team_html = drop_down.get_attribute('innerHTML')
    soup = bs4.BeautifulSoup(team_html, 'html5lib')
    playerTeam = soup.find('span', attrs={'data-bind': "text: selectedTeamLabel"}).text

    print(playerName[1:], 'had the most at bats in the American League in the 2015 regular season. His position is', playerPos, 'at', playerTeam)
    driver.back()


def q5():
    data_div = driver.find_element_by_id('datagrid')
    data_html = data_div.get_attribute('innerHTML')
    soup = bs4.BeautifulSoup(data_html, 'html5lib')
    player_divs = soup.find_all('tr', attrs={'tabindex': '0'})
    name_set = []
    data_set = []
    count = 0
    for a in player_divs:
        player_name = a.find('td', attrs={'class': 'dg-name_display_last_init'}).text
        name_set.append(player_name[1:])
    for a in name_set:
        count += 1
        player_link = driver.find_element_by_link_text(a)
        move_click(player_link)
        sleep()
        playerName = driver.find_element_by_class_name('player-bio')
        name_html = playerName.get_attribute('innerHTML')
        soup = bs4.BeautifulSoup(name_html, 'html5lib')
        playerName = soup.find('li').text.split(':')
        playerName = playerName[1]
        born = soup.find_all('li')
        location = ''
        for a in born:
            if a.find('span').text == 'Born:':
                location = a.text.split(',')
                location = location[1]
                break
        location = location[1:]
        location = location[:-1]
        if location in latinCountries:
            drop_down = driver.find_element_by_xpath(
                "//div[contains(@class, 'dropdown') and contains(@class, 'team')]")
            team_html = drop_down.get_attribute('innerHTML')
            soup = bs4.BeautifulSoup(team_html, 'html5lib')
            playerTeam = soup.find('span', attrs={'data-bind': "text: selectedTeamLabel"}).text
            data_set.append((playerName[1:], playerTeam))
        driver.back()
        progressBar(count, len(name_set))
        sleep()

    df = pd.DataFrame(data=data_set, columns=['PlayerName', 'Team'])
    df.to_csv('question5.csv', index=False, header=False)
    sys.stdout.write("\r\tHere are player in 2014 All-Star Game who are from Latin America:\n")
    sys.stdout.flush()
    for a in data_set:
        print('\t\t', a[0], 'played for', a[1])


def click_next_page_for_stats():
    pagination_div = driver.find_element_by_class_name('paginationWidget-next')

    if pagination_div.get_attribute('style') == 'display: none;':
        return False
    else:
        move_click(pagination_div)
        sleep()
        return True


def sleep():
    normal_delay = random.normalvariate(3, 0.5)
    time.sleep(normal_delay)


def move_click(a):
    ActionChains(driver).move_to_element(a).click().perform()


def progressBar(value, endvalue, bar_length=20):

    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rPercent: [{}] {}%".format(arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()


wait = WebDriverWait(driver, 10)
driver.get('http://www.mlb.com')
sleep()

#stats_header_bar = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "megamenu-navbar-overflow__menu-item-link--stats")))
stats_header_bar = driver.find_element_by_class_name('megamenu-navbar-overflow__menu-item-link--stats')
#move_click(stats_header_bar)
stats_header_bar.click()
stats_header_bar.click()
sleep()

teamButton = driver.find_element_by_id('st_parent')
move_click(teamButton)
sleep()

selectSeason = driver.find_element_by_id('st_hitting_season')
season_select = Select(selectSeason)
season_select.select_by_value('2015')
sleep()

selectGameType = driver.find_element_by_id('st_hitting_game_type')
gametype_select = Select(selectGameType)
gametype_select.select_by_value("'R'")
sleep()

selectTable = wait.until(EC.visibility_of_element_located((By.ID, 'datagrid')))
selectTable = selectTable.find_element_by_tag_name('table')
selectTable = selectTable.find_element_by_tag_name('thead')
selectTable = selectTable.find_element_by_tag_name('tr')
selectTable = selectTable.find_element_by_class_name('dg-hr')
move_click(selectTable)
sleep()

print('Q1:', end='\n\t')
q1()
print()
sleep()

print('Q2:','\ta) ', sep='\n', end='')
q2a()
print()
sleep()

selectHitSplits = driver.find_element_by_id('st_hitting_hitting_splits')
hitsplits_select = Select(selectHitSplits)
hitsplits_select.select_by_value('i01')
sleep()

print('\tb) ', end='')
q2b()
print()
sleep()

playerButton = wait.until(EC.visibility_of_element_located((By.ID, 'sp_parent')))
move_click(playerButton)
sleep()

selectSeason = driver.find_element_by_id('sp_hitting_season')
season_select = Select(selectSeason)
season_select.select_by_value('2017')
sleep()

selectTeam = driver.find_element_by_id('sp_hitting_team_id')
team_select = Select(selectTeam)
team_select.select_by_value('147')
sleep()

selectHitSplits = driver.find_element_by_id('sp_hitting_hitting_splits')
hitsplits_select = Select(selectHitSplits)
hitsplits_select.select_by_visible_text('Select Split')
sleep()

selectTable = wait.until(EC.visibility_of_element_located((By.ID, 'datagrid')))
selectTable = selectTable.find_element_by_tag_name('table')
selectTable = selectTable.find_element_by_tag_name('thead')
selectTable = selectTable.find_element_by_tag_name('tr')
selectTable = selectTable.find_element_by_class_name('dg-avg')
move_click(selectTable)
sleep()

print('Q3:', '\ta) ', sep='\n', end='')
q3a()
print()
sleep()

print('\tb) ', end='')
q3b()
print()
sleep()

selectSeason = driver.find_element_by_id('sp_hitting_season')
season_select = Select(selectSeason)
season_select.select_by_value('2015')
sleep()

selectTable = wait.until(EC.visibility_of_element_located((By.ID, 'sp_hitting-1')))
selectTable = selectTable.find_element_by_tag_name('fieldset')
selectTable = selectTable.find_element_by_xpath('//label[@for="sp_hitting_league_code_al"]')
move_click(selectTable)
sleep()

selectTeam = driver.find_element_by_id('sp_hitting_team_id')
team_select = Select(selectTeam)
team_select.select_by_visible_text('All Teams')
sleep()

selectTable = wait.until(EC.visibility_of_element_located((By.ID, 'datagrid')))
selectTable = selectTable.find_element_by_tag_name('table')
selectTable = selectTable.find_element_by_tag_name('thead')
selectTable = selectTable.find_element_by_tag_name('tr')
selectTable = selectTable.find_element_by_class_name('dg-ab')
move_click(selectTable)
sleep()

print('Q4:', end='\n\t')
q4()
print()
sleep()

selectSeason = driver.find_element_by_id('sp_hitting_season')
season_select = Select(selectSeason)
season_select.select_by_value('2014')
sleep()

selectGameType = driver.find_element_by_id('sp_hitting_game_type')
gametype_select = Select(selectGameType)
gametype_select.select_by_value("'A'")
sleep()

selectTable = wait.until(EC.visibility_of_element_located((By.ID, 'sp_hitting-1')))
selectTable = selectTable.find_element_by_tag_name('fieldset')
selectTable = selectTable.find_element_by_xpath('//label[@for="sp_hitting_league_code_mlb"]')
move_click(selectTable)
sleep()

latinCountries = ['Brazil', 'Mexico', 'Colombia', 'Argentina', 'Peru', 'Venezuela', 'Chile', 'Ecuador', 'Guatemala', 'Cuba', 'Haiti', 'Bolivia', 'Dominican Republic', 'Honduras', 'Paraguay', 'Nicaragua', 'El Salvador', 'Costa Rica', 'Panama', 'Puerto Rico', 'Uruguay', 'Guadeloupe', 'Martinique', 'French Guiana', 'Saint Martin', 'Saint Barthélemy']
sleep()

print('Q5:', end='\n\t')
q5()
print()
sleep()

driver.close()
'''
except selenium.common.exceptions.NoSuchElementException as e:
    print('Error', e)
'''


headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': '0bf50d984ec545a6a5374c0a7338ef68',
}

params = urllib.parse.urlencode({'format':'JSON','season':'2016'})

try:
    conn = http.client.HTTPSConnection('api.fantasydata.net')
    conn.request("GET", "/v3/mlb/scores/JSON/Games/2016", "{body}", headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))