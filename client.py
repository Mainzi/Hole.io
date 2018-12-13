import socket
import argparse
import player as pl
import pygame
from pygame.locals import *
from player import Player
from render import Render
from contextlib import closing

def arg_parse():
    parser = argparse.ArgumentParser()
   
    parser.add_argument("--host", dest = 'host', help = "Host IP", default = 'localhost', type = str)
    parser.add_argument("--port", dest = 'port', help = "port", default = 9999, type = int)    
    return parser.parse_args()

def handle_input():
    global running

    pygame.event.pump()
    keys = pygame.key.get_pressed()
    v = 0

    if keys[K_RIGHT]:
        v = 1

    if keys[K_LEFT]:
        v = 2

    if keys[K_UP]:
        v = 3

    if keys[K_DOWN]:
        v = 4

    if keys[K_ESCAPE]:
        running = False

    return v


with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as server_socket:
    global running
    args = arg_parse()
    
    host = args.host
    port = args.port
    #host = '192.168.0.103'
    #port = 6677

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.connect((host, port))

    arr = server_socket.recv(7).decode('ascii').strip().split(' ')
    arr = [int(item) for item in arr]

    print(arr)

    render = Render()
    render.set_window_size(arr[0], arr[1])

    id = arr[2]

    input_result = 0
    running = True
    player_score = 0
    while running:
        input_result, prev_result = handle_input(), input_result

        if input_result and input_result != prev_result:
            server_socket.send('{id} {state}'.format(id=id, state=input_result).encode('ascii'))

        length = int(server_socket.recv(3).decode('ascii'))

        if length == -1:
            running = False
            player_score = int(server_socket.recv(3).decode('ascii'))
            break

        r = server_socket.recv(length).decode('ascii')

        # ! splits foods and players arrays

        r = r.split('!')
        food_strings = r[0].split('?')
        players_strings = r[1].split('?')

        # Splitting tuple-strings into two integers
        food_strings = [food.strip('()').split(',') for food in food_strings]
        foods = [(int(food[0]), int(food[1])) for food in food_strings]

        players_strings = [player.split(': ') for player in players_strings]

        players_strings = {int(player[0]): player[1][1:-1] for player in players_strings}

        players_strings = {key: value.split(', ') for key, value in players_strings.items()}
        #print players_strings
  
        players = {id: pl.construct_player(id, info[0],info[1], info[2]) for id, info in players_strings.items()}

        render.draw(players, foods)


with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as server_socket:
    print 'Game over! Your score = {0}'.format(player_score)
    print 'Enter your nickname:'
    player_name = str(raw_input())
    
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.connect((host, 50123))
    
    msg = '{0} {1}'.format(player_name, player_score).encode('ascii')
    length = str(len(msg)).zfill(2).encode('ascii')

    server_socket.send(length)
    server_socket.send(msg)

    length = int(server_socket.recv(3).decode('ascii'))
    if length > 0:
        r = server_socket.recv(length).decode('ascii')
        print ''
        print '     TOP 3:'
        r = r[1:-1].split(', ')
        for t in r:
            print '         ', t[1:-1]
