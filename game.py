import time
from random import randint
import pygame
from pygame.locals import *
from player import Player
from render import Render


class Game:
    update_time = 0.2 #0.5
    frame_time = 0.1

    players = {}
    foods = []
    leaderboard = {}

    def __init__(self):
        pygame.init()
        self.step_num = 0
        self.width = 0
        self.height = 0
        self.size = 20

    def set_field_size(self, w, h):
        self.width = w
        self.height = h

    def add_player(self, id):
        x = randint(0, self.width  - 1)
        y = randint(0, self.height - 1)
        radius = 20
        self.players[id] = Player(id, x, y, radius)
        self.leaderboard[id] = 0
        print 'Player {0} in game'.format(id)

    def add_food(self):
        x = randint(0, self.width - 1)
        y = randint(0, self.height - 1)
        self.foods.append((x, y))

    def check_collisions(self):
        player_array = self.players.copy().items()

        for i, player in player_array:
            centre = (player.centre[0] *self.size + player.radius, player.centre[1]*self.size + player.radius)
    
            if (centre[0] < 0 or centre[0] >= self.width * self.size or
                    centre[1] < 0 or centre[1] >= self.height * self.size):
                self.leaderboard[self.players[i].id] = self.players[i].score
                del self.players[i]
                print 'Player {0} collide with bound'.format(i)

            for food in self.foods:
                critical_distance = abs(player.radius - 1)
                distance = ((centre[0] - food[0] * self.size) ** 2 + (centre[1] - food[1] * self.size) ** 2)**0.5
                if distance <= critical_distance:
                     self.players[i].eat_food()
                     self.players[i].grow(1)  # this may put tail on top of the head
                     self.foods.remove(food)
                     self.add_food()
                     self.leaderboard[i] = self.leaderboard[i] + 1


            for j, other in player_array:
                if j == i:
                    continue
                other_centre = (other.centre[0] *self.size + other.radius, other.centre[1]*self.size + other.radius)
                critical_distance = abs(player.radius - other.radius)
                distance = ((centre[0] - other_centre[0]) ** 2 + (centre[1] - other_centre[1]) ** 2)**0.5
                if player.radius > other.radius and distance < critical_distance:
                     del self.players[other.id]
                     self.players[i].grow(other.radius)
                     self.leaderboard[i] = self.leaderboard[i] + other.radius / 2
                     print '{0} kill {1}'.format(i, other.id)

                                    

    def update(self):
        for i, player in self.players.items():
            self.players[i].move()

    def handle_events(self, id, key):
        left, right, up, down = 1, 2, 3, 4

        if key == left:
            self.players[id].set_velocity(1, 0)

        if key == right:
            self.players[id].set_velocity(-1, 0)

        if key == up:
            self.players[id].set_velocity(0, -1)

        if key == down:
            self.players[id].set_velocity(0, 1)

    def run_step(self):
        self.step_num += 1

        if self.step_num * self.frame_time == self.update_time:
            self.step_num = 0
            self.update()
            self.check_collisions()

            if len(self.players) == 0:  # game is over when there are no players left
                return False

        return True
