
#pip3 install git+https://github.com/webpy/webpy#egg=web.py

import web, sqlite3, json
from datetime import datetime

urls = (
    '/', 'index',
    '/data', 'data'
)
render = web.template.render('templates/')

class index:
    def GET(self):
        return render.index()

class data:
    def GET(self):
        data = fetch_data()
        web.header('Content-Type', 'application/json')
        return json.dumps(data)

def fetch_data():
    db = sqlite3.connect('cover.sqlite')
    cursor = db.cursor()

    # fetching days
    cursor.execute('SELECT begin, end, points FROM fetched WHERE points > 0 ORDER BY begin DESC')
    fetched = cursor.fetchall()
    days = []
    for fetch in fetched:
        begin_t = fetch[0]
        end_t = fetch[1]
        begin = datetime.fromtimestamp(begin_t)
        begin_s = begin.strftime('%a, %d %b %Y')

        # fetching points for a day
        q = 'SELECT lat, lon FROM points WHERE ts >= {} AND ts <= {} ORDER BY ts ASC'.format(begin_t, end_t)
        cursor.execute(q)
        points = cursor.fetchall()
        points_m = list(map((lambda x: {'lat':x[0], 'lng':x[1]}), points))

        days.append({'date': begin_s, 'points_count': fetch[2], 'points': points_m})

    # fetching all points
    cursor.execute('SELECT lat, lon FROM points ORDER BY ts ASC')
    points = cursor.fetchall()
    points_m = list(map((lambda x: {'lat':x[0], 'lng':x[1]}), points))

    db.close()
    return {'all_points': points_m, 'days': days}

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
