import socket
import select
import time
import argparse
from contextlib import closing

def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", dest = 'port', help = "port", default = 50123, type = int)
    
    return parser.parse_args()

def disconnect_player(epoll, connections, game_paper, socket_to_id, fileno):
    epoll.unregister(fileno)
    connections[fileno].close()
    del connections[fileno]

    if socket_to_id[fileno] in game_paper.players:
        del game_paper.players[socket_to_id[fileno]]

    del socket_to_id[fileno]

def for_sort(player):
    return player[1]

with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as server_socket:
    args = arg_parse()
    leaderboard = []

    host = '127.0.0.1'
    port = args.port
    #host = '192.168.0.103'
    #port = 6677

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(10)

    epoll = select.epoll()
    epoll.register(server_socket.fileno(), select.EPOLLIN)
    connections = {}
    socket_to_id = {}
    counter = 0
    while True:
        events = epoll.poll(1)
        for fileno, event in events:
            if fileno == server_socket.fileno():
                connection, address = server_socket.accept()
                connection.setblocking(False)
                connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                epoll.register(connection.fileno(), select.EPOLLIN | select.EPOLLOUT)

                connections[connection.fileno()] = connection
                socket_to_id[connection.fileno()] = counter


                length = int(connection.recv(2).decode('ascii'))

                res = connection.recv(length).decode('ascii')
                if res == '':
                    disconnect_player(epoll, connections, game_paper, socket_to_id, fileno)
                else:
                    res = [item for item in res.strip().split(' ')]
                    leaderboard.append((res[0], int(res[-1])))
                    leaderboard = sorted(leaderboard, key = for_sort, reverse = True)
                    leaderboard = leaderboard[0: min(3,len(leaderboard))]

                    msg = str(['{0}: {1}'.format(player[0], player[1]) for player in leaderboard]).encode('ascii')
                    length = str(len(msg)).zfill(3).encode('ascii')

                    connection.send(length)
                    connection.send(msg)

                counter += 1
                
        print leaderboard
        time.sleep(0.5)
