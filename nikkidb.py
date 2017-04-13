import sqlite3
import requests
import json
import queue
import functools

from threading import Thread


class MultiThreadOK(Thread):
    def __init__(self):
        super(MultiThreadOK, self).__init__()
        self.reqs = queue.Queue()
        self.start()

    def run(self):
        cnx = sqlite3.connect("./nikki.db", isolation_level=None, )
        cursor = cnx.cursor()
        while True:
            req, arg, res = self.reqs.get()
            if req == '--close--': break
            cursor.execute(req, arg)
            if res:
                for rec in cursor:
                    res.put(rec)
                res.put('--no more--')
        cnx.close()

    def execute(self, req, arg=None, res=None):
        self.reqs.put((req, arg or tuple(), res))

    def select(self, req, arg=None):
        res = queue.Queue()
        self.execute(req, arg, res)
        while True:
            rec = res.get()
            if rec == '--no more--': break
            yield rec

    def close(self):
        self.execute('--close--')


sql = MultiThreadOK()


def check(discord_id, vatsim_id):
    result = sql.select('''SELECT * FROM users WHERE discord_id = ?''', (discord_id,))
    row_count = functools.reduce(lambda x, y: x + 1, result, 0)

    if row_count != 0:
        print(
            'I rejected DiscordID: ' + discord_id + ' who called me to add him to DB with VatsimID: ' + vatsim_id + '. This discord ID is already in DB')
        return "USER_DUPLICATE"

    result = sql.select('''SELECT * FROM users WHERE vatsim_id = ?''', (vatsim_id,))
    row_count = functools.reduce(lambda x, y: x + 1, result, 0)

    if row_count != 0:
        print(
            'I rejected DiscordID: ' + discord_id + ' who called me to add him to DB with VatsimID: ' + vatsim_id + '. This vatsim ID is already in DB')
        return "USER_DUPLICATE"

    answer = requests.get('http://api.vateud.net/members/id/' + vatsim_id + '.json').text
    try:
        member_info = json.loads(answer)
    except json.JSONDecodeError:
        print(
            'I rejected DiscordID: ' + discord_id + ' who called me to add him to DB with VatsimID: ' + vatsim_id + '. Member with this vatsim ID not found')
        return "INVALID_CID"

    if 'active' not in member_info:
        print(
            'I rejected DiscordID: ' + discord_id + ' who called me to add him to DB with VatsimID: ' + vatsim_id + '. This vatsim ID seems invalid')
        return "INVALID_CID"
    elif not member_info['active']:
        print(
            'I rejected DiscordID: ' + discord_id + ' who called me to add him to DB with VatsimID: ' + vatsim_id + '. This vatsim ID is inactive')
        return "INVALID_CID"

    return "OK"


def insert(discord_id, vatsim_id):
    answer = requests.get('http://api.vateud.net/members/id/' + vatsim_id + '.json').text
    member_info = json.loads(answer)
    sql.execute('''INSERT INTO users (discord_id, vatsim_id) VALUES (?, ?)''', (discord_id, vatsim_id,))
    print('I have just added a user DiscordID: ' + discord_id + ' with VatsimID: ' + vatsim_id)
    return member_info['firstname'] + ' ' + member_info['lastname']

def get_reg_list():
    result = sql.select('''SELECT discord_id, vatsim_id FROM users''')
    return tuple(result)