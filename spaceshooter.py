import pygame, sys, random

## GLOBAL VARS
pygame.init()  # Initiate pygame
screen = pygame.display.set_mode((600,1024))  # Init Display Surface. Pass in a tuple for the screen size
clock = pygame.time.Clock()  # init a clock that we will use to control the fps
FRAME_INTERVAL = 3 # ratio of game frames to animation frames

dust_y_position = 0
player_velocity = 5

# Object lists
player_laser_shots = []
enemy_laser_shots = []
enemy_ships = []

# ASSETS
bg_surface = pygame.image.load('assets/background.png').convert()
bg_dust_surface = pygame.image.load('assets/background-dust.png').convert_alpha()

ship_left = pygame.image.load('assets/ship-left.png').convert_alpha()
ship_center = pygame.image.load('assets/ship-center.png').convert_alpha()
ship_right = pygame.image.load('assets/ship-right.png').convert_alpha()
ship_states = {'left': ship_left, 'center': ship_center, 'right': ship_right}

laser_surface_asset = pygame.image.load('assets/laser.png').convert_alpha()
laser_explode_anim = [pygame.image.load('assets/laser-hit01.png').convert_alpha(),
					pygame.image.load('assets/laser-hit02.png').convert_alpha(),
					pygame.image.load('assets/laser-hit03.png').convert_alpha(),
					pygame.image.load('assets/laser-hit04.png').convert_alpha(),
					pygame.image.load('assets/laser-hit05.png').convert_alpha(),
					pygame.image.load('assets/laser-hit06.png').convert_alpha()]

enemy_surface_asset = pygame.image.load('assets/enemy-center.png').convert_alpha()
enemy_explode_anim = [pygame.image.load('assets/explosion01.png').convert_alpha(),
					pygame.image.load('assets/explosion02.png').convert_alpha(),
					pygame.image.load('assets/explosion03.png').convert_alpha(),
					pygame.image.load('assets/explosion04.png').convert_alpha(),
					pygame.image.load('assets/explosion05.png').convert_alpha(),
					pygame.image.load('assets/explosion06.png').convert_alpha(),
					pygame.image.load('assets/explosion07.png').convert_alpha(),
					pygame.image.load('assets/explosion08.png').convert_alpha()]


class Laser():
	def __init__(self, x, y, set_damage = 10, set_velocity = -10):
		self.x = x
		self.y = y
		self.velocity = set_velocity
		self.damage = set_damage
		self.laser_surface = laser_surface_asset
		self.laser_rect = self.laser_surface.get_rect(center = (self.x, self.y))

		# for hit animation
		self.can_cull= False
		self.is_exploding = False
		self.frame_index = 0

	def draw(self):
		if self.is_exploding:
			self.velocity = 0 # stop moving
			self.laser_surface = laser_explode_anim[self.frame_index // FRAME_INTERVAL]
			self.laser_rect = self.laser_surface.get_rect(center = (self.x, self.y))
			self.frame_index += 1

			if self.frame_index > (len(laser_explode_anim) * FRAME_INTERVAL - 1):
				self.can_cull= True
				self.frame_index=0
		
		else:
			self.laser_surface = laser_surface_asset
			self.laser_rect = self.laser_surface.get_rect(center = (self.x, self.y))

		screen.blit(self.laser_surface, self.laser_rect)

	def move(self):
		self.y += self.velocity
		self.laser_rect = self.laser_surface.get_rect(center = (self.x, self.y))

	def check_out_of_range(self):
		if self.y <= -5 or self.y >= 1040:
			self.can_cull = True

	def update(self):
		self.check_out_of_range()
		self.move()
		self.draw()


class Enemy():
	def __init__(self, x, y, steer_behaviour= 'static', shoot_behaviour= 'inline'):
		self.x = x
		self.y = y
		self.velocity = 1
		self.x_velocity = 2
		self.health = 20

		self.enemy_surface = enemy_surface_asset
		self.enemy_rect = self.enemy_surface.get_rect(center = (self.x, self.y))

		# behaviour
		self.steer_behaviour = steer_behaviour
		self.shoot_behaviour = shoot_behaviour
		self.countdown_timer_max = 60
		self.countdown_timer = random.randint(0, self.countdown_timer_max)

		# For death animation
		self.is_dead = False
		self.is_exploding = False
		self.frame_index = 0

	def draw(self):
		if self.is_exploding:  # exploding animation
			self.enemy_surface = enemy_explode_anim[self.frame_index // FRAME_INTERVAL]
			self.enemy_rect = self.enemy_surface.get_rect(center = (self.x, self.y))
			self.frame_index += 1

			if self.frame_index > (len(enemy_explode_anim) * FRAME_INTERVAL - 1):
				self.frame_index=0
				self.is_exploding = False
				self.is_dead = True
				print('Destroyed')

		else: # otherwise, draw enemy ship
			self.enemy_surface = enemy_surface_asset
			self.enemy_rect = self.enemy_surface.get_rect(center = (self.x, self.y))

		screen.blit(self.enemy_surface, self.enemy_rect)

	def move(self): 
		if self.steer_behaviour == 'static': # move in a straight line
			self.y += self.velocity
			self.enemy_rect = self.enemy_surface.get_rect(center = (self.x, self.y))

		elif self.steer_behaviour == 'weave': # weave back and forth across screen
			self.y += self.velocity
			self.x += self.x_velocity

			# if x is between 540 and 600, progressively subtract 0.1 until it reaches -1, and vice versa on the other side
			if self.x <= 60 and self.y > 0:
				self.x_velocity = self.x_velocity + 0.1

			elif self.x >= 540  and self.y > 0:
				self.x_velocity = self.x_velocity - 0.1

	def shoot(self, player_x):  # shoot a laser
		if not self.is_dead or not self.is_exploding:
			
			if self.shoot_behaviour == 'inline' and self.countdown_timer <= 0:
				
				if self.x in range(player_x - 10, player_x + 10):
					shot = Laser(self.enemy_rect.centerx, self.enemy_rect.centery + 90, set_velocity = 5)
					enemy_laser_shots.append(shot)
					self.countdown_timer = self.countdown_timer_max # reset countdown

	def check_collisions(self, shots):  # check if being hit by lasers
		if not self.is_exploding:
			for shot in shots:
				if shot.is_exploding == False and self.enemy_rect.colliderect(shot.laser_rect): # if colliding with a shot
					
					print(shot.is_exploding)
					shot.is_exploding = True  # trigger the shot hit animation
					shot.y = shot.y - random.randint(5, 25) # offset the laser, want the hit animation to trigger a bit on the ship itself
					self.health -= shot.damage

					if self.health <= 0:
						self.is_exploding = True
						self.velocity = 0
						self.x_velocity = 0

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

		self.countdown_timer_max = 25
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
			player_laser_shots.append(shot)
			self.countdown_timer = self.countdown_timer_max # reset countdown

	def check_collisions(self):
		for shot in enemy_laser_shots:
			if self.ship_rect.colliderect(shot.laser_rect):
				enemy_laser_shots.remove(shot) # remove shot from list
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

	# takes in a schedule containing time:event
	# takes in a list of enemy ships and does stuff to it

	# within its update function it:
	# calls their update functions (containing move, shoot, collide)
	# culls them when they are out of view
	# spawns new enemies using spawn functions according to a schedule based on incrementing game time
		# self.ships = ship_list

class EnemyManager():
	def __init__(self, ship_list):
		self.ships = ship_list


	def spawn_single(self, x):
		new_enemy = Enemy(x, -70)
		self.ships.append(new_enemy)




## INITS
player = Player(300, 860, state='center')
enemies = EnemyManager(ship_list=enemy_ships)

## HELPER FUNCTIONS
def draw_dust(pos = 0):
	screen.blit(bg_dust_surface, (0, pos))
	screen.blit(bg_dust_surface, (0, pos - 1024))

def update_laser_shots(shots):
	for shot in shots:
		if shot.can_cull:
			shots.remove(shot) 
		
		shot.update()

def collide(obj1, obj2):  # Check if two objects collide (not used right now, needs sprite bitmasks)
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


## SPAWN FUNCTIONS
def spawn_single(x):
	ship_list = []
	new_enemy = Enemy(x, -70)
	ship_list.append(new_enemy)
	return ship_list

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

def spawn_weave(ship_count, direction="right", y_spacing = 60):
	x_spacing = 600 // (ship_count)
	y_spacing *= -1
	y = -40
	ship_list = []

	if direction is 'right':
		x_velocity = 2
		x_spacing *= -1
		x = 0

	elif direction is 'left':
		x_velocity = -2
		x = 600


	for i in range(ship_count):
		new_enemy = Enemy(x, y, steer_behaviour='weave', shoot_behaviour='inline')
		new_enemy.x_velocity = x_velocity
		ship_list.append(new_enemy)
		y += y_spacing
		x += x_spacing
		print(x)

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
				print('single')
				enemies.spawn_single(300)

			if event.key == pygame.K_f: 
				print('S - right')
				enemy_ships.extend(spawn_weave(5, direction='right'))

			if event.key == pygame.K_d:
				print('S - left')
				enemy_ships.extend(spawn_weave(5, direction='left'))


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


	# Draw all enemies, check for collisions
	for enemy_ship in enemy_ships:
		enemy_ship.update(player_laser_shots, player.x)

		if enemy_ship.is_dead == True:
			enemy_ships.remove(enemy_ship)

		elif enemy_ship.y >= 1100:
			enemy_ships.remove(enemy_ship)
			print("enemy clipped")

		# elif random.randrange(0, 2*60) == 1:
		# 	enemy_ship.shoot()


	for laser in player_laser_shots:
		if laser.can_cull:
			player_laser_shots.remove(laser)

	# for laser in enemy_laser_shots:
	# 	if laser.y <= -5 or laser.y >= 1040:
	# 		enemy_laser_shots.remove(laser)

	# Draw lasers
	update_laser_shots(player_laser_shots)
	update_laser_shots(enemy_laser_shots)

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