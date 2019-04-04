
#!/usr/local/bin/python3

#pip3 install git+https://github.com/webpy/webpy#egg=web.py

import web, sqlite3, json
from datetime import datetime

urls = (
    '/test', 'test',
    '/', 'index',
    '/days', 'days_list'
)

render = web.template.render('templates/')

class test:
    def GET(self):
        return render.test()

class index:
    def GET(self):
        return render.index()

class days_list:
    def GET(self):

        db = sqlite3.connect('cover.sqlite', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = db.cursor()

        # fetching days
        db_days = cursor.execute('SELECT id, date, dist FROM days WHERE dist > 0 ORDER BY date DESC').fetchall()
        days = []
        for db_day in db_days:
            day_id = db_day[0]
            date = db_day[1]
            date_str = date.strftime("%d %b %Y")
            dist = db_day[2]

            # fetching points for a day
            # db_points = cursor.execute('SELECT lat, lon FROM points WHERE day_id == {} ORDER BY ts ASC'.format(day_id)).fetchall()
            # points = list(map((lambda x: {'lat':x[0], 'lng':x[1]}), db_points))

            days.append({'id': day_id, 'date': date_str, 'dist': dist})

        # fetching all points
        # db_points = cursor.execute('SELECT lat, lon FROM points ORDER BY ts ASC').fetchall()
        # points = list(map((lambda x: {'lat':x[0], 'lng':x[1]}), db_points))

        db.close()
        web.header('Content-Type', 'application/json')
        return json.dumps(days)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
