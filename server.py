from bottle import route, run, template, static_file, auth_basic, install, request, response
import sqlite3, json
from datetime import datetime
import logging

def check(user, pw):
    with open('conf.json') as creds_file:
        conf = json.load(creds_file)
    users = conf['users']
    success = user in users and pw == users[user]
    if success:
        logging.info('Logged in as {}'.format(user))
    else:
        logging.error('Error logging in as {} {}'.format(user, pw))
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

logging.basicConfig(filename="access.log", level=logging.INFO, format='%(asctime)s %(message)s')
logging.info('Bike Cover started!')

def logger(func):
    def wrapper(*args, **kwargs):
        req = func(*args, **kwargs)
        logging.info('%s %s %s' % (request.remote_addr, request.method, request.path))
        return req
    return wrapper

install(logger)

run(host='0.0.0.0', port=8000, debug=False, quiet=True)
