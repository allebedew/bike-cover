
import requests, sqlite3
from datetime import datetime, timezone, timedelta

session_id = '5fhmt9p641ufb9cb4ia4iksas1'

def fetch_nodes(begin, end):
    begin_ts = begin.replace(tzinfo=timezone.utc).timestamp()
    end_ts = end.replace(tzinfo=timezone.utc).timestamp()
    print('fetching nodes {} ({}) .. {} ({})'.format(begin, begin_ts, end, end_ts))
    params = {'beginTime':begin_ts, 'endTime':end_ts, 'timezoneOffset':180, 'shortParkingTime':5, 'longParkingTime':3600}
    headers = {'Cookie': 'PHPSESSID='+session_id}
    d = requests.get('https://starline-online.ru/device/353173065843169/route?', params=params, headers=headers)

    if d.status_code != 200:
        print('error response: {}'.format(d.status_code))
        return None

    j = d.json()
    print('data count: {}'.format(len(j['data'])))

    nodes = list()
    for d in j['data']:
        d_dec = decode_node(d)
        if d_dec is not None:
            nodes.append(d_dec)
        if 'nodes' in d:
            for n in d['nodes']:
                n_dec = decode_node(n)
                if n_dec is not None:
                    nodes.append(n_dec)

    print('nodes: {}'.format(len(nodes)))
    return nodes

def decode_node(node):
    d = dict()
    if 't' in node and 'x' in node and 'y' in node:
        d['lat'] = node['x']
        d['lon'] = node['y']
        d['ts'] = node['t']
        d['z'] = node['z'] if 'z' in node else None
        d['speed'] = node['s'] if 's' in node else None
        d['sat'] = node['sat_qty'] if 'sat_qty' in node else None
        d['mil'] = node['mileage'] if 'mileage' in node else None
        return d
    else:
        return None

def insert_nodes(begin, end, nodes):
    begin_ts = begin.replace(tzinfo=timezone.utc).timestamp()
    end_ts = end.replace(tzinfo=timezone.utc).timestamp()
    begin_s = begin.strftime('%a, %d %b %Y')
    end_s = end.strftime('%a, %d %b %Y')
    print('inserting {} nodes in {} .. {}'.format(len(nodes), begin_s, end_s))
    try:
        db = sqlite3.connect('cover.sqlite')
        c = db.cursor()

        c.executemany('''insert into points(ts, lat, lon, speed, z, sat, mil)
                         values(:ts, :lat, :lon, :speed, :z, :sat, :mil)''', nodes)

        f_val = (begin_ts, begin_s, end_ts, end_s, len(nodes))
        c.execute('''insert into fetched(begin, begin_s, end, end_s, points)
                     values(?,?,?,?,?)''', f_val)

        db.commit()
        print('inseted')
    finally:
        db.close()

def grab(begin, end):
    b = begin
    delta = timedelta(days=1)
    while b <= end:
        e = b + delta
        print('grabbing {} -> {}'.format(b, e))
        n = fetch_nodes(b, e)
        insert_nodes(b, e, n)
        b += delta


begin = datetime(2018, 1, 1)
end = datetime(2018, 5, 1)

grab(begin, end)
