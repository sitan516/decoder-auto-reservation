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


def get_albums(curs, start_date, end_date):
    start = time.time()
    print(f'[*] Loading data (album id FROM db) ...')

    curs.execute("SELECT album_id, song_list, release_date FROM album_info WHERE release_date BETWEEN '" + start_date
                 + "' AND '" + end_date + "' AND song_cnt > 0 AND album_id NOT IN (SELECT DISTINCT album_id FROM song_info) ORDER BY release_date DESC")
    album = curs.fetchall()

    s = time.time() - start
    m = s // 60
    print(f'[+] Done ({m:.0f}min {s - m:.3f}sec)\n')
    return album


def get_songs(start_date, end_date):
    # MySQL Connection
    conn = pymysql.connect(host='j5a504.p.ssafy.io', user='myplaylist', password='myplaylist504', db='maply', charset='utf8')
    # Cursor from Connection
    curs = conn.cursor()

    put_song_q = "INSERT IGNORE INTO song_info VALUES("

    base_url = 'https://www.melon.com/song/detail.htm?songId='

    albums = get_albums(curs, start_date, end_date)

    for album in albums:
        album_id = str(album[0])
        print(f'{album_id:>8}  {str(album[2])}')
        song_list = album[1].split(',')

        for song_id in song_list:
            print(base_url + song_id)
            soup = crawling(base_url + song_id)

            song_name = soup.find('div', attrs={'class': 'song_name'})
            if not song_name:
                wait_cycle = 2
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

            genre = soup.find_all('dd')[2].text

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

            values = song_id + ',\'' + song_name + '\',' + album_id + ',\'' + artists + '\',\'' + genre + '\',\'' + lyrics + '\',\'' + lyricists + '\',\'' + composers + '\',\'' + arrangers + '\', \'\')'

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
    # end_date에 크롤링 끝낼 날짜 넣기 (사실 끝낼 날짜부터 역순으로 진행 -> crawling 중단 시 마지막 출력된 날짜 넣으면 됨)
        song_info에 없는 album_id만 가져오니까 멈춘 시점에 출력된 날짜만 넣어주면 알아서 그 다음부터 돌아감 (앨범 중간에 멈추면 방법 없음)
    - 안석현 : '2018-01-01', '2018-12-31'
    - 나희승 : '2019-01-01', '2019-12-31'
    - 조규홍 : '2020-01-01', '2020-12-31'
    """
    get_songs('2020-01-01', '2020-12-31')


if __name__ == '__main__':
    main()
