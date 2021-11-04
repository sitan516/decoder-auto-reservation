from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import requests
import pymysql
import re
import time
from random import *


def crawling(url):
    ua = UserAgent()

    # change User-Agent to avoid bot
    headers = {'User-Agent': ua.random}
    res = requests.get(url, headers=headers).text

    return BeautifulSoup(res, 'lxml')


def get_song_ids(curs, start_date, end_date):
    song_ids = set()
    
    curs.execute("SELECT song_list FROM playlist_info WHERE last_update BETWEEN '" + start_date + "' AND '" + end_date + "'")
    
    for songs in curs.fetchall():
        song_ids.update(songs[0].split(','))
    song_ids.remove('')
    song_ids = list(song_ids)
    song_ids.sort()
    return song_ids


def get_song_info(start_date, end_date, start_elem):
    # MySQL Connection
    conn = pymysql.connect(host='j5a504.p.ssafy.io', user='myplaylist', password='myplaylist504', db='maply', charset='utf8')

    # Cursor from Connection
    curs = conn.cursor()

    put_song_q = "INSERT IGNORE INTO song_in_playlist VALUES("

    base_url = 'https://www.melon.com/song/detail.htm?songId='

    song_ids = get_song_ids(curs, start_date, end_date)
    if start_elem in song_ids:
        song_ids = song_ids[song_ids.index(start_elem):]

    for song_id in song_ids:
        print(base_url + song_id)
        soup = crawling(base_url + song_id)

        song_name = soup.find('div', attrs={'class': 'song_name'})
        if not song_name:
            wait_cycle = 2
            wait_t = 600

            while soup.find('div', attrs={'class': 'sys_error'}):
                print("wait ... " + str(wait_cycle-1))
                time.sleep(wait_cycle * 600)
                wait_cycle += 1
                if wait_cycle > 5:
                    break

            song_name = soup.find('div', attrs={'class': 'song_name'})
            if not song_name:
                continue

        artists = [artist['href'].split('\'')[1] for artist in song_name.find_next_sibling().find_all('a')]
        artists = ','.join(artists)

        song_name = re.sub('\'', '\\\'', song_name.text.strip()[2:].strip())

        meta_info = soup.find_all('dd')

        album_id = meta_info[0].find('a')['href'].split('\'')[1]

        genre = meta_info[2].text

        lyrics = soup.find('div', attrs={'class': 'lyric'})
        if lyrics:
            lyrics = re.sub('\'', '\\\'', lyrics.get_text('\n', strip=True))
        else:
            lyrics = ''

        lyricists = []
        composers = []
        arrangers = []

        makers_type = soup.find_all('span', attrs={'class': 'type'})

        for t in makers_type:
            makers_id = t.find_parent().find_previous_sibling().find('a')['href'].split('(')[1][:-1]
            if t.text == "작사":
                 lyricists.append(makers_id)
            elif t.text == "작곡":
                composers.append(makers_id)
            else:
                arrangers.append(makers_id)

        lyricists = ','.join(lyricists)
        composers = ','.join(composers)
        arrangers = ','.join(arrangers)

        values = song_id + ',\'' + song_name + '\',' + album_id + ',\'' + artists + '\',\'' + genre + '\',\'' + lyrics + '\',\'' + lyricists + '\',\'' + composers + '\',\'' + arrangers + '\')'
        print(put_song_q + values)

        try:
            curs.execute(put_song_q + values)
            conn.commit()
        except:
            print(put_song_q + values)

        time.sleep(randrange(2, 5))

    conn.close()


def main():
    """
    # param (start_date, end_date, song_id to start crawling)
    # str() 함수 내부에 crawling 시작할 song_id 넣기 (crawling 중단 되었을 때 마지막 출력된 song_id 넣으면 됨 / 첫 시작은 0 넣으면 알아서 처리)
    - 안석현 : '2021-01-01', '2021-12-31', str(0) => 29315 playlists
    - 나희승 : '2020-01-01', '2020-12-31', str(0) => 25838 playlists
    - 조규홍 : '2018-01-01', '2019-12-31', str(0) => 27734 playlists
    """
    get_song_info('2021-01-01', '2021-12-31', str(27734))

    """
    출력 형태
    https://www.melon.com/song/detail.htm?songId=100014077
    INSERT IGNORE INTO song_in_playlist VALUES(100014077,'Traveller',4941376,'2324308','월드뮤직','','','','')
    
    => url 에서 song_id = 100014077 (중단 시 이 부분 보고 다시 시작)
    => 가사, 작사가, 작곡가, 편곡자 등 데이터 없는 경우 있으므로 '', '', '' 처럼 나와도 문제 x
    """


if __name__ == '__main__':
    main()