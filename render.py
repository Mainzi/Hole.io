from pygame.locals import *
import pygame


class Render:
    unit_size = 20
    windowWidth = 600
    windowHeight = 400
    
    def __init__(self):
        self.display = pygame.display.set_mode((self.windowWidth,self.windowHeight), pygame.HWSURFACE)
        pygame.display.set_caption('Hole')
        self.bound_circle = 3
        self.colors = [pygame.Color('red'), pygame.Color('blue'), pygame.Color('green'), pygame.Color('black'), pygame.Color('purple'), pygame.Color('orange')] 
        self.food_image = pygame.Surface((self.unit_size, self.unit_size))
        self.food_image.fill((255, 0, 0))


    def set_window_size(self, w, h):
        #self.unit_size = unit_size
        self.windowWidth = w*self.unit_size
        self.windowHeight = h*self.unit_size
        self.display = pygame.display.set_mode((self.windowWidth,self.windowHeight), pygame.HWSURFACE)
    
    def draw_menu(self):
        pass
    
    def draw(self, players, foods):
        self.display.fill((255,255,255))
        for player in players.values():
            #print player.centre
            coord = (player.centre[0] *self.unit_size + player.radius, player.centre[1]*self.unit_size + player.radius)
            
            pygame.draw.circle(self.display, self.colors[player.id % len(self.colors)], coord, player.radius, self.bound_circle + 2)
            pygame.draw.circle(self.display, pygame.Color('black'), coord, player.radius - self.bound_circle)
               
        for food in foods:
            self.display.blit(self.food_image, (food[0]*self.unit_size, food[1]*self.unit_size))

        pygame.display.update()
