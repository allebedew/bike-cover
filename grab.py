#!/usr/local/bin/python3

from datetime import date, datetime, timezone, timedelta
import os
import os.path
import requests
import pickle
import sqlite3
import json
import shutil

conf = None
db = None
url = 'https://starline-online.ru'
session = requests.Session()
headers = {'X-Requested-With': 'XMLHttpRequest', 
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0'}
t_days = 0
t_bike_days = 0
t_dist = 0

def login():
    """Returns true/false"""

    print('Logging in as {}'.format(conf['login']))
    payload = {'LoginForm[login]': conf['login'], 'LoginForm[pass]': conf['pass']}
    r = session.post(url + '/user/login', data=payload, headers=headers, allow_redirects=False)
    if r.status_code != 200:
        print('Error response: {}\n{}'.format(r.status_code, r.text))
        return False
    print('Logged in!')
    return True
    
def restore_session():
    if os.path.isfile('session') == False:
        print("No session file")
        return False
    with open('session', 'rb') as f:
        session.cookies.update(pickle.load(f))
    r = session.get(url + '/device', headers=headers, allow_redirects=False)
    if r.status_code != 200:
        print('Error response: {}\n{}'.format(r.status_code, r.text))
        print('Restored session expired')
        return False
    print('Session restored')
    return True

def save_session():
    if os.path.isfile('session'):
        print('Deleting old session file')
        os.remove('session')
    with open('session', 'wb') as f:
        pickle.dump(session.cookies, f)
    print('Session saved')

def fetch_nodes(begin, end):
    """Gets begin, end as datetime, returns nodes [] or None"""

    begin_ts = int(begin.replace(tzinfo=timezone.utc).timestamp())
    end_ts = int(end.replace(tzinfo=timezone.utc).timestamp())
    print('Fetching nodes {} ({}) .. {} ({})'.format(begin, begin_ts, end, end_ts))
    params = {'beginTime':begin_ts, 'endTime':end_ts, 'timezoneOffset':180, 'shortParkingTime':5, 'longParkingTime':30}
    req = session.get(url + '/device/' + conf['device'] + '/route', params=params, headers=headers, allow_redirects=False)

    if req.status_code != 200:
        print('Error response: {}\n{}'.format(req.status_code, req.text))
        return None

    json = req.json()
    return json

def prepare_db():
    """Creates DB if needed and opens it"""

    global db
    db = sqlite3.connect('cover.sqlite', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    db.execute('''CREATE TABLE IF NOT EXISTS "days" (
        "id" INTEGER PRIMARY KEY,
        "date" DATE NOT NULL UNIQUE,
        "dist" INTEGER NOT NULL DEFAULT 0,
        "comment" TEXT
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS "tracks" (
        "id" INTEGER PRIMARY KEY,
        "date_id" timestamp NOT NULL,
        "dist" INTEGER NOT NULL DEFAULT 0
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS "points" (
        "ts" INTEGER UNIQUE ON CONFLICT IGNORE,
        "day_id" INTEGER,
        "track_id" INTEGER,
        "lat" REAL,
        "lon" REAL,
        "speed" INTEGER,
        "sat" INTEGER,
        "dist" INTEGER
    )''')

def get_last_record():
    """Returns date of lats record or None"""

    rec = db.execute('SELECT date FROM days ORDER BY date DESC LIMIT 1').fetchone()
    if rec is None:
        print('Database is empty')
        return None
    else:
        date = rec[0]
        print('Last day is {}'.format(date))
        return date

def insert_nodes(date, json):
    '''Parses json data and inserts to db'''
    distance = json['meta']['mileage']
    data = json['data']
    tracks = list(filter(lambda x: x['type'] == 'TRACK', data))

    print('Inserting {} tracks, {} km total ({})'.format(len(tracks), distance / 1000.0, date))
    
    if db.execute('SELECT 1 FROM days WHERE date == ?', (date,)).fetchone() is not None:
        print('This day is already in database')
        return
    
    c = db.cursor()
    c.execute('INSERT INTO days(date, dist) VALUES (?,?)', (date, distance))
    day_id = c.lastrowid
    for track in tracks:
        c.execute('INSERT INTO tracks(date_id, dist) VALUES (?,?)', (day_id, track['mileage']))
        track_id = c.lastrowid
        for node in track['nodes']:
            c.execute('INSERT INTO points(ts, day_id, track_id, lat, lon, speed, sat, dist) VALUES (?,?,?,?,?,?,?,?)',
                (node['t'], day_id, track_id, node['x'], node['y'], 
                node['s'] if 's' in node else None,
                node['sat_qty'] if 'sat_qty' in node else None, 
                node['mileage'] if 'mileage' in node else None))
    db.commit()

    global t_days, t_bike_days, t_dist
    t_days += 1
    if distance > 0:
        t_bike_days += 1
        t_dist += distance


if __name__ == "__main__":
    print('=+=+=+= Starline Track Grabber =+=+=+=\n')

    with open('conf.json') as creds_file:
        conf = json.load(creds_file)

    if restore_session() == False:
        if login() == False:
            exit()
        save_session()

    prepare_db()

    try:
        last_date = get_last_record()
        date_from = last_date if last_date is not None else date(2016, 3, 1)
        date_to = date.today()
        print('Starting fetch from {} to {}'.format(date_from, date_to))

        date = date_from
        while date <= date_to:
            begin = datetime.combine(date, datetime.min.time())
            end = datetime.combine(date, datetime.max.time())
            json = fetch_nodes(begin, end)
            insert_nodes(date, json)
            date += timedelta(days = 1)
    
    finally:
        db.close()
        print('\n*** Grabbing complete, {} days, {} bike days, {} km added to database ***'.format(t_days, t_bike_days, t_dist/1000.0))

