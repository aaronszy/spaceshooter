import pygame, sys, random

## GLOBAL VARS
pygame.init()  # Initiate pygame
screen = pygame.display.set_mode((600,1024))  # Init Display Surface. Pass in a tuple for the screen size
clock = pygame.time.Clock()  # init a clock that we will use to control the fps
FRAME_INTERVAL = 5 # ratio of game frames to animation frames

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
enemy_explode_anim = [pygame.image.load('assets/enemy-explode01.png').convert_alpha(),
					pygame.image.load('assets/enemy-explode02.png').convert_alpha(),
					pygame.image.load('assets/enemy-explode03.png').convert_alpha()]


class Laser():
	def __init__(self, x, y, damage = 10, velocity = -10):
		self.x = x
		self.y = y
		self.velocity = velocity
		self.damage = 10
		self.laser_rect = laser_surface.get_rect(center = (self.x, self.y))

	def draw(self):
		screen.blit(laser_surface, self.laser_rect)

	def move(self):
		self.y += self.velocity
		self.laser_rect = laser_surface.get_rect(center = (self.x, self.y))


class Enemy():
	def __init__(self, x, y, steer_behaviour= 'static', shoot_behaviour= 'inline'):
		self.x = x
		self.y = y
		self.velocity = 1
		self.x_velocity = 2
		self.health = 20

		self.enemy_surface = enemy_surface
		self.enemy_rect = enemy_surface.get_rect(center = (self.x, self.y))

		# behaviour
		self.steer_behaviour = steer_behaviour
		self.shoot_behaviour = shoot_behaviour
		self.countdown_timer_max = 60
		self.countdown_timer = 0

		# For death animation
		self.is_dead = False
		self.is_exploding = False
		self.frame_index = 0

	def draw(self):
		if self.is_exploding:  # exploding animation
			self.enemy_surface = enemy_explode_anim[self.frame_index // FRAME_INTERVAL]
			self.enemy_rect = enemy_surface.get_rect(center = (self.x, self.y))
			self.frame_index += 1

			if self.frame_index > (len(enemy_explode_anim) * FRAME_INTERVAL - 1):
				self.frame_index=0
				self.is_exploding = False
				self.is_dead = True
				print('Destroyed')

		else: # otherwise, draw enemy ship
			self.enemy_surface = enemy_surface
			self.enemy_rect = enemy_surface.get_rect(center = (self.x, self.y))

		screen.blit(self.enemy_surface, self.enemy_rect)

	def move(self): 
		if self.steer_behaviour == 'static':
			self.y += self.velocity
			self.enemy_rect = enemy_surface.get_rect(center = (self.x, self.y))

		elif self.steer_behaviour == 'weave':
			self.y += self.velocity
			self.x += self.x_velocity

			# if x is between 0 and 60, set X velocity to positive. If between 540 and 600, set it to negative
			if self.x <= 60:
				self.x_velocity = self.x_velocity * -1
			elif self.x >= 540:
				self.x_velocity = self.x_velocity * -1

	def shoot(self, player_x):  # shoot a laser
		if not self.is_dead or not self.is_exploding:
			
			if self.shoot_behaviour == 'inline' and self.countdown_timer <= 0:
				
				if self.x in range(player_x - 10, player_x + 10):
					shot = Laser(self.enemy_rect.centerx, self.enemy_rect.centery + 90, velocity = 5)
					laser_shots.append(shot)
					self.countdown_timer = self.countdown_timer_max # reset countdown

	def check_collisions(self, shots):  # check if being hit by lasers
		for shot in shots:
			if self.enemy_rect.colliderect(shot.laser_rect):
				shots.remove(shot)  # remove shot from list
				self.health -= shot.damage
				if self.health <= 0:
					self.is_exploding = True

	def update(self, shots, player_x):
		self.move()
		self.check_collisions(shots)
		self.shoot(player_x)
		self.draw()
		if self.countdown_timer <= self.countdown_timer_max and self.countdown_timer > 0:
			self.countdown_timer -= 1


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

		self.countdown_timer_max = 20
		self.countdown_timer = 0

	def draw(self):
		self.ship_surface = ship_states[self.state]
		self.ship_rect = self.ship_surface.get_rect(center = (self.x, self.y))
		screen.blit(self.ship_surface, self.ship_rect)
		self.healthbar()

	def move(self, x = 0, y = 0):  # basic move code
		self.x += x
		self.y += y

	def move_vector(self, direction='center'): # dont think this fancy code is doing very much right now
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
		if self.countdown_timer <= 0:
			shot = Laser(self.ship_rect.centerx, self.ship_rect.centery - 90)
			laser_shots.append(shot)
			self.countdown_timer = self.countdown_timer_max # reset countdown

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
		if self.health <= self.max_health:  # each frame, recharge some health
			self.health += self.recharge_rate
		
		self.draw()

		if self.countdown_timer <= self.countdown_timer_max and self.countdown_timer > 0:
			self.countdown_timer -= 1

	def healthbar(self):  # draw healthbar based on current vs max health
		pygame.draw.rect(screen, (0,0,0), (self.x-25, self.y+50, self.ship_surface.get_width(), 4))
		pygame.draw.rect(screen, (171,195,254), (self.x-25, self.y+50, self.ship_surface.get_width() * (self.health/self.max_health), 4))



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

def collide(obj1, obj2):  # Check if two objects collide (not used right now, needs sprite bitmasks)
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


## SPAWN FUNCTIONS
def spawn_row(ship_count):
	x_spacing = 600 // (ship_count)
	x = x_spacing
	ship_list = []

	for i in range(0, ship_count-1):
		new_enemy = Enemy(x, -70)
		ship_list.append(new_enemy)
		x += x_spacing

	return ship_list

def spawn_v(ship_count, y_spacing = 40):  # enter odd number
	x_spacing = 600 // (ship_count)
	x = x_spacing
	y = y_spacing
	depth = ship_count // 2 + 1
	ship_list = []

	# for first row, add 1 ship at 300, then for each depth add 2 ships 300 x, 300 + x, then increment x by x_space. Same for y, y_spacing
	# First ship - point
	new_enemy = Enemy(300, -70)
	ship_list.append(new_enemy)

	for i in range(depth):
		new_enemy = Enemy(300 + x, -70 - y)
		ship_list.append(new_enemy)

		new_enemy = Enemy(300 - x, -70 - y)
		ship_list.insert(0,new_enemy)

		y += y_spacing
		x += x_spacing

	return ship_list



# EVENT TIMERS
ENEMYSPAWN = pygame.USEREVENT # create a pygame user event. the +1 is to differentiate it from the first uservent - SPAWNPIPE
pygame.time.set_timer(ENEMYSPAWN, 2000)


# GAME LOOP
while True:

	# EVENTS
	for event in pygame.event.get():  # start event loop. Pygame watches for a number of events, and for each event, do something

		if event.type == pygame.QUIT:  # if user clicks X in top right of window
			pygame.quit()  # quits the pygame window
			sys.exit()  # stops all running processes. Otherwise, the rest of the While loop runs even though you closed the pygame window and it will give you an error.

		if event.type == pygame.KEYDOWN: # if any key has been pressed..
			if event.key == pygame.K_SPACE:
				player.shoot()

			if event.key == pygame.K_r: 
				print('row')
				enemy_ships.extend(spawn_row(5))

			if event.key == pygame.K_v: 
				print('V')
				enemy_ships.extend(spawn_v(5, 100))

			if event.key == pygame.K_s: 
				new_enemy = Enemy(300, -70, steer_behaviour='weave', shoot_behaviour='inline')
				enemy_ships.append(new_enemy)


		if event.type == ENEMYSPAWN:
			# enemy = Enemy(random.randrange(50, 550), -50)
			# enemy_ships.append(enemy)
			pass

	# PLAYER MOVEMENT
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

	if keys[pygame.K_SPACE]:
		player.shoot()

	# DRAW STUFF
	# Draw background, move dust
	screen.blit(bg_surface, (0,0))
	dust_y_position = dust_y_position + 8
	draw_dust(dust_y_position)

	if dust_y_position >= 1024:
		dust_y_position = 0

	# Draw lasers
	draw_laser_shots(laser_shots)

	# Draw all enemies, check for collisions
	for enemy_ship in enemy_ships:
		enemy_ship.update(laser_shots, player.x)

		if enemy_ship.is_dead == True:
			enemy_ships.remove(enemy_ship)

		elif enemy_ship.y >= 1100:
			enemy_ships.remove(enemy_ship)
			print("enemy clipped")

		# elif random.randrange(0, 2*60) == 1:
		# 	enemy_ship.shoot()


	for laser in laser_shots:
		if laser.y <= -5 or laser.y >= 1040:
			laser_shots.remove(laser)

	# Draw player ship, check collisions
	player.update()

	pygame.display.update()
	clock.tick(120) # limit the loop to a maximum of 120 fps

## Debug spawn function
# Try with spawning lasers instead. Or move the code right into the event instead of in the function

## Next steps
# Build in a start and game over state
# Spawn functions - row, V, etc. Movement flags for enemies (straight, sweep,  weave)
# Basic shooting AI - random, shoot when inline with player
# Implement shooting cooldown timers for both enemies and player
# Cull enemy laser shots.. not doing this right now

# Later..
# Switch hardcoded size values for size attributes, so that we can swap assets and change window sizes at will
# Switch to using Sprites?, implement bitmask collision detection. Note: May not want to use Sprite Groups though.
# Create a more generic "Ship" class and wrap Player and Enemy classes around it, to reduce duplicate code


# To animate:
# Create an array with each frame we will iterate over. eg. 10 frames.
# Determine how many animation frames you want per second
# Create a global function that gets the current time (CURRENT_TIME_MILLI = int(time.time() * 1000)
# Then, when animation starts record the current time in a var. Then every 200ms (or w/e) iterate through the list.