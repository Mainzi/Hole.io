def construct_player(id, x, y, r):
        player = Player(id, int(x), int(y), int(r))
        return player

class Player:

   

    def __init__(self, id, x, y, radius):
        self.id = id

        self.velocity = (0, 0)
        self.centre = (x, y)
        self.radius = radius
        self.score = 0

    def set_velocity(self, v_x, v_y):
        self.velocity = (v_x, v_y)

    def grow(self, add):
        if self.radius < 300:
            self.radius = self.radius + add
        

    def move(self):
        if self.velocity == (0, 0):
            return
        self.centre = (self.centre[0] + self.velocity[0], self.centre[1] + self.velocity[1])

    def eat_food(self):
        self.score += 10
        self.grow(10)
