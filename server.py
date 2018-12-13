import socket
import select
import time
import argparse
from contextlib import closing

from game import Game

def arg_parse():
    parser = argparse.ArgumentParser()
   
    parser.add_argument("--width", dest = 'width', help = "Field width", default = 40, type = int)
    parser.add_argument("--height", dest = 'height', help = "Field height", default = 20, type = int)
    parser.add_argument("--port", dest = 'port', help = "port", default = 9999, type = int)
    
    return parser.parse_args()

def disconnect_player(epoll, connections, game_paper, socket_to_id, fileno):
    epoll.unregister(fileno)
    connections[fileno].close()
    del connections[fileno]

    if socket_to_id[fileno] in game_paper.players:
        del game_paper.players[socket_to_id[fileno]]

    del socket_to_id[fileno]


with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as server_socket:
    args = arg_parse()
    
    host = '127.0.0.1'
    port = args.port
    #host = '192.168.0.103'
    #port = 6677

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(10)

    width, height = args.width, args.height

    game_paper = Game()
    game_paper.set_field_size(width, height)

    counter = 0

    epoll = select.epoll()
    epoll.register(server_socket.fileno(), select.EPOLLIN)
    connections = {}
    socket_to_id = {}
    while True:
        game_paper.run_step()
        events = epoll.poll(1)

        for fileno, event in events:
            if fileno == server_socket.fileno():
                connection, address = server_socket.accept()
                connection.setblocking(False)
                connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                epoll.register(connection.fileno(), select.EPOLLIN | select.EPOLLOUT)

                connections[connection.fileno()] = connection
                for i in range(2):
                    game_paper.add_food()
                game_paper.add_player(counter)

                socket_to_id[connection.fileno()] = counter

                connection.send("{0} {1} {2}".format(width, height, counter).encode('ascii'))

                counter = (counter + 1) % 10
            elif event & select.EPOLLIN:
                client_socket = connections[fileno]

                res = client_socket.recv(3).decode('ascii')

                if res == '':
                    disconnect_player(epoll, connections, game_paper, socket_to_id, fileno)
                else:
                    res = [int(item) for item in res.strip().split(' ')]

                    game_paper.handle_events(res[0], res[1])
            elif event & select.EPOLLOUT:
                client_socket = connections[fileno]

                id = socket_to_id[fileno]

                if id not in game_paper.players:  # Collided with self or bounds
                    # Telling client to disconnect, at next iteration we
                    # will delete its information
                    client_socket.send(' -1'.encode('ascii'))
                    client_socket.send(str(game_paper.leaderboard[id]).encode('ascii'))
                    continue

                # Sending food and player positions
                msg = "{0}!{1}".format(
                    '?'.join([str(food) for food in game_paper.foods]),
                    '?'.join(['{0}: {1}'.format(str(id), str((player.centre[0], player.centre[1], player.radius))) for id, player in game_paper.players.items()])
                    ).encode('ascii')
                length = str(len(msg)).zfill(3).encode('ascii')

                client_socket.send(length)
                client_socket.send(msg)

        time.sleep(game_paper.frame_time)
