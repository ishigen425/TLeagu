from argparse import ArgumentParser
import sys
import requests
from bs4 import BeautifulSoup
import re
from game_data_func import get_game_recorde,get_link,get_match_recorde,get_point_record
import csv

BASIC_URL = "https://tleague.jp"
SEASON_2018_2019 = ["201810","201811","201812","201901","201902", "201903"]
SEASON_2019_2020 = ["201908", "201909"]

def parser():
    usage = "UIsage: python '2018 or 2019'"
    argparser = ArgumentParser(usage=usage)
    argparser.add_argument('season', type=str, help="2018 or 2019")
    args = argparser.parse_args()
    return args

def main(season):
    match_table, game_table, point_table = [], [], []
    if season == "2018":
        link = get_link(season, SEASON_2018_2019)
    else:
        link = get_link(season, SEASON_2019_2020)
    try:
        for i in link:
            url = BASIC_URL + i
            print(url)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            sex = 0 if i[-3] == "m" else 1
            date = i[-11:-3]
            match_id = i[7:]
            
            #match table
            all_match = get_match_recorde(soup)
            match_table.append([
                match_id, date, all_match[0], all_match[1], int(all_match[2]), int(all_match[3]), int(all_match[4]), int(sex)
            ])

            #game table
            all_match_game = get_game_recorde(soup)
            for a_game_index, a_game in enumerate(all_match_game):
                if a_game[1] != None:
                    game_table.append([
                        match_id, a_game_index, a_game[0], a_game[1], a_game[2], a_game[3], int(a_game[4]), int(a_game[5])
                    ])
                else:
                    game_table.append([
                        match_id, a_game_index, a_game[0], None, a_game[2], None, int(a_game[4]), int(a_game[5])
                    ])

            #point table
            all_match_point, all_match_timeout, all_match_serve = get_point_record(soup)
            for a_match_point_index, a_match_point in enumerate(all_match_point):
                for a_set_point_index, a_set_point in enumerate(a_match_point):
                    for a_point_index, a_point in enumerate(a_set_point):
                        point_table.append([
                            match_id, a_match_point_index, a_set_point_index, a_point_index,
                            int(a_point), int(all_match_serve[a_match_point_index][a_set_point_index][a_point_index]),
                            all_match_timeout[a_match_point_index][a_set_point_index][a_point_index][0],
                            all_match_timeout[a_match_point_index][a_set_point_index][a_point_index][1]
                        ])
    except:
        print("Error", sys.exc_info()[0])
    finally:
        match_header = ["match_id", "date", "home", "away", "home_point", "away_point", "visitors", "sex"]
        game_header = ["match_id", "game_id", "home_player1", "home_player2", "away_player1", "away_player2", "home_point", "away_point"]
        point_header = ["match_id", "game_id", "set_id", "point_id", "point", "serve", "home_timeout_flg", "away_timeout_flg"]

        # export csv
        with open('./data/match_table_{}.csv'.format(season), 'w', encoding='utf-8') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(match_header)
            writer.writerows(match_table)

        with open('./data/game_table_{}.csv'.format(season), 'w', encoding='utf-8') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(game_header)
            writer.writerows(game_table)

        with open('./data/point_table_{}.csv'.format(season) ,'w', encoding='utf-8') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(point_header)
            writer.writerows(point_table)


if __name__ == '__main__':
    parser()
    season = sys.argv[0]
    main(season)
