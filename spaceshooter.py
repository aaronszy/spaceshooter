import pygame, sys, random

## VARS
pygame.init()  # Initiate pygame
screen = pygame.display.set_mode((600,1024))  # Init Display Surface. Pass in a tuple for the screen size
clock = pygame.time.Clock()  # init a clock that we will use to control the fps

dust_y_position = 0
player_velocity = 5

# Object lists
laser_shots = []
enemy_ships = []

# ASSETS
bg_surface = pygame.image.load('assets/background.png').convert()
bg_dust_surface = pygame.image.load('assets/background-dust.png').convert_alpha()

ship_left = pygame.image.load('assets/ship-left.png').convert_alpha()
ship_center = pygame.image.load('assets/ship-center.png').convert_alpha()
ship_right = pygame.image.load('assets/ship-right.png').convert_alpha()
ship_states = {'left': ship_left, 'center': ship_center, 'right': ship_right}

laser_surface = pygame.image.load('assets/laser.png').convert_alpha()

enemy_surface = pygame.image.load('assets/enemy-center.png').convert_alpha()


class Laser:
	def __init__(self, x, y, damage = 10, velocity = -10):
		self.x = x
		self.y = y
		self.velocity = velocity
		self.damage = 10
		self.laser_rect = laser_surface.get_rect(center = (self.x, self.y))
		self.mask = pygame.mask.from_surface(laser_surface)

	def draw(self):
		screen.blit(laser_surface, self.laser_rect)

	def move(self):
		self.y += self.velocity
		self.laser_rect = laser_surface.get_rect(center = (self.x, self.y))


class Enemy:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.velocity = 2
		self.health = 20
		self.enemy_rect = enemy_surface.get_rect(center = (self.x, self.y))
		self.mask = pygame.mask.from_surface(enemy_surface)

	def draw(self):
		screen.blit(enemy_surface, self.enemy_rect)

	def move(self):
		self.y += self.velocity
		self.enemy_rect = enemy_surface.get_rect(center = (self.x, self.y))

	def shoot(self):
		shot = Laser(self.enemy_rect.centerx, self.enemy_rect.centery + 90, velocity = 10)
		laser_shots.append(shot)

	def check_collisions(self, shots):
		for shot in shots:
			# if collide(self, shot):
			# 	shots.remove(shot) # remove shot from list
			# 	self.health -= shot.damage
			# 	return True

			if self.enemy_rect.colliderect(shot.laser_rect):
				shots.remove(shot) # remove shot from list
				self.health -= shot.damage
				return True

class Player:
	def __init__(self, x, y, state='center'):
		self.x = x
		self.y = y
		self.state = state
		self.health = 100
		self.max_health = 100
		self.recharge_rate = 0.02
		self.accel, self.decel = 2, -1
		self.movement_vector = [0, 0]

	def draw(self):
		self.ship_surface = ship_states[self.state]
		self.ship_rect = self.ship_surface.get_rect(center = (self.x, self.y))
		screen.blit(self.ship_surface, self.ship_rect)
		self.healthbar()

	def move(self, x = 0, y = 0):
		self.x += x
		self.y += y

	def move_vector(self, direction='center'):
		if direction == 'left':
			self.state = 'left'
			if self.movement_vector[0] >= -player_velocity:
				self.movement_vector[0] -= self.accel
			else:
				self.movement_vector[0] = -player_velocity

		elif direction == 'right':
			self.state = 'right'
			if self.movement_vector[0] <= player_velocity:
				self.movement_vector[0] += self.accel
			else:
				self.movement_vector[0] = player_velocity

		self.x += self.movement_vector[0]

	def shoot(self):
		shot = Laser(self.ship_rect.centerx, self.ship_rect.centery - 90)
		laser_shots.append(shot)

	def check_collisions(self):
		for shot in laser_shots:
			if self.ship_rect.colliderect(shot.laser_rect):
				laser_shots.remove(shot) # remove shot from list
				print("OUCH!")
				self.health -= shot.damage
		# for enemy in enemy_ships:
		# 	if self.ship_rect.colliderect(enemy.enemy_rect):
		# 		print("CRASH!")
		# 		self.health -= 5

	def update(self):
		self.check_collisions()
		if self.health <= self.max_health:
			self.health += self.recharge_rate
		self.draw()

	def healthbar(self):
		pygame.draw.rect(screen, (0,0,0), (self.x-25, self.y+50, self.ship_surface.get_width(), 4))
		pygame.draw.rect(screen, (171,195,254), (self.x-25, self.y+50, self.ship_surface.get_width() * (self.health/self.max_health), 4))


def collide(obj1, obj2):  # Check if two objects collide
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


## INITS
player = Player(300, 860, state='center')

## HELPER FUNCTIONS
def draw_dust(pos = 0):
	screen.blit(bg_dust_surface, (0, pos))
	screen.blit(bg_dust_surface, (0, pos - 1024))

def draw_laser_shots(Shots):
	for Shot in Shots: 
		Shot.draw()
		Shot.move()


# TIMERS
ENEMYSPAWN = pygame.USEREVENT # create a pygame user event. the +1 is to differentiate it from the first uservent - SPAWNPIPE
pygame.time.set_timer(ENEMYSPAWN, 2000)

while True:

	for event in pygame.event.get():  # start event loop. Pygame watches for a number of events, and for each event, do something

		if event.type == pygame.QUIT:  # if user clicks X in top right of window
			pygame.quit()  # quits the pygame window
			sys.exit()  # stops all running processes. Otherwise, the rest of the While loop runs even though you closed the pygame window and it will give you an error.

		if event.type == pygame.KEYDOWN: # if any key has been pressed..
			if event.key == pygame.K_SPACE:
				player.shoot()

		if event.type == ENEMYSPAWN:
			enemy = Enemy(random.randrange(50, 550), -50)
			enemy_ships.append(enemy)

	player.state = 'center' # if no keys pressed, bring ship state back to center

	keys = pygame.key.get_pressed() # Check for all pressed keys
	if keys[pygame.K_DOWN]:
		player.state = 'center'
		player.move(y = player_velocity)

	if keys[pygame.K_UP]:
		player.state = 'center'
		player.move(y = -player_velocity)

	if keys[pygame.K_LEFT]:
		# player.state = 'left'
		# player.move(x = -player_velocity)
		player.move_vector('left')


	if keys[pygame.K_RIGHT]:
		# player.state = 'right'
		# player.move(x = player_velocity)
		player.move_vector('right')


	# Draw bg, move dust
	screen.blit(bg_surface, (0,0))
	dust_y_position = dust_y_position + 8
	draw_dust(dust_y_position)

	if dust_y_position >= 1024:
		dust_y_position = 0

	# Draw objects
	draw_laser_shots(laser_shots)

	# Draw enemies, check for collisions
	for enemy_ship in enemy_ships:
		enemy_ship.draw()
		enemy_ship.move()

		if enemy_ship.check_collisions(laser_shots):
			if enemy_ship.health <= 0:
				enemy_ships.remove(enemy_ship)
				print("Destroyed")

		elif enemy_ship.y >= 1100:
			enemy_ships.remove(enemy_ship)
			print("enemy clipped")

		elif random.randrange(0, 2*60) == 1:
			enemy.shoot()

	for laser in laser_shots:
		if laser.y <= -5:
			laser_shots.remove(laser)

	# Draw ship, check collisions
	player.update()

	pygame.display.update()
	clock.tick(120) # limit the loop to a maximum of 120 fps

## Next steps
# Build in a start and game over state
# Switch to using Sprites, and implement bitmask collision detection
# Implement some animation
# Implement shooting cooldown timers for both enemies and player
# Create a more generic "Ship" class and wrap Player and Enemy classes around it, to reduce duplicate code
# Switch hardcoded size values for size attributes, so that we can swap assets and change window sizes at will


# To animate:
# Create an array with each frame we will iterate over. eg. 10 frames.
# Determine how many animation frames you want per second
# Create a global function that gets the current time (CURRENT_TIME_MILLI = int(time.time() * 1000)
# Then, when animation starts record the current time in a var. Then every 200ms (or w/e) iterate through the list.