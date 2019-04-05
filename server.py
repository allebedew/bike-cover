from bottle import route, run, template, static_file, auth_basic
import sqlite3, json
from datetime import datetime

def check(user, pw):
    with open('conf.json') as creds_file:
        conf = json.load(creds_file)
    users = conf['users']
    print('Trying to log in as {}:{} ... '.format(user, pw), end='', flush=True)
    success = user in users and pw == users[user]
    if success:
        print('OK', flush=True)
    else:
        print('FAILED!', flush=True)
    return success

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static')

@route('/')
def index():
    return static_file('index.html', root='static')

@route('/days')
@auth_basic(check)
def days():
    db = sqlite3.connect('cover.sqlite', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cursor = db.cursor()

    db_days = cursor.execute('SELECT id, date, dist FROM days WHERE dist > 0 ORDER BY date DESC').fetchall()
    days = []
    for db_day in db_days:
        day_id = db_day[0]
        date = db_day[1]
        date_str = date.strftime("%d %b %Y")
        dist = db_day[2]

        # fetching points for a day
        db_points = cursor.execute('SELECT lat, lon FROM points WHERE day_id == {} ORDER BY ts ASC'.format(day_id)).fetchall()
        points = list(map((lambda x: {'lat':x[0], 'lng':x[1]}), db_points))
        days.append({'id': day_id, 'date': date_str, 'dist': dist, 'points': points})

        # fetching all points
        # db_points = cursor.execute('SELECT lat, lon FROM points ORDER BY ts ASC').fetchall()
        # points = list(map((lambda x: {'lat':x[0], 'lng':x[1]}), db_points))
    db.close()
    return {'days':days}

@route('/points')
def points():
    return {'points': 123}

run(host='0.0.0.0', port=8000, debug=False)
print('Bike-Cover started!', flush=True)
