import pygame

class cPal:
	"""The 'stick' class.. the player"""
	__MOV_SPEED = 3;
	__ROT_SPEED = 3;
	__BACK_TICKS = 12;
	__JUMP_LENGTH = 5;
	__TURBO_MULTIPLIER = 2;
	
	def __init__(self,x,y,rot,stickpath="sticks/stick.png"):
		
		self.image      = pygame.image.load(stickpath).convert_alpha()
		self.baseImage  = pygame.image.load(stickpath).convert_alpha()
		self.mask       = pygame.mask.from_surface(self.image);
		
		self.rect = self.image.get_rect();
		
		self.movx = 0;
		self.movy = 0;

		#Rotation Direction
		self.rot = rot;
		self.clockwise = False
		
		#Backwards move
		self.tbackwards = False
		self.tbackwards_ticks = self.__BACK_TICKS

		self.rect.x,self.rect.y = x,y

		#Movement Flags
		self.fmove = True
		self.turbo = False

        #Loads a new stick Image
	def load_stick_image(self,imagepath):
                self.image      = pygame.image.load(imagepath).convert_alpha()
		self.baseImage  = pygame.image.load(imagepath).convert_alpha()
		self.mask       = pygame.mask.from_surface(self.image);
		self.rect = self.image.get_rect();

                
	#Rotate function. Called continuously
	def rotate(self,amount=__ROT_SPEED):
		"""
			rotate an image while keeping its center in the specified
			amount attribute in degrees.

			self.tbackwards defines a temporal inverse rotation
		"""
		if self.clockwise: self.clockwise_rotation(amount)
		else: self.counterclockwise_rotation(amount)
		
	def clockwise_rotation(self,amount):
		if self.tbackwards:             	#Check if temporal backwards rotation is set
			self.rot -= amount + 2  	#When rotating back has to be faster
			self.tbackwards_ticks -= 1
		else:
			self.rot -= amount

		if self.tbackwards_ticks == 0:
			self.tbackwards = False
			self.tbackwards_ticks = self.__BACK_TICKS
			self.flip_rotation()

		if self.rot <= 0: self.rot = 360;

		self.image = pygame.transform.rotate(self.baseImage, self.rot)
		self.rect = self.image.get_rect(center=self.rect.center)
		self.mask = pygame.mask.from_surface(self.image)

	def counterclockwise_rotation(self,amount):
		if self.tbackwards:             	#Check if temporal backwards rotation is set
			self.rot += amount + 2  	#When rotating back has to be faster
			self.tbackwards_ticks -= 1
		else:
			self.rot += amount

		if self.tbackwards_ticks == 0:
			self.tbackwards = False
			self.tbackwards_ticks = self.__BACK_TICKS
			self.flip_rotation()

		if self.rot >= 360: self.rot = 0;

		self.image = pygame.transform.rotate(self.baseImage, self.rot)
		self.rect = self.image.get_rect(center=self.rect.center)
		self.mask = pygame.mask.from_surface(self.image)

	#
	# Moving Functions
	#
	def move_left(self):
		if self.fmove: self.movx -= cPal.__MOV_SPEED;
	def move_right(self):
		if self.fmove: self.movx += cPal.__MOV_SPEED;
	def move_up(self):
		if self.fmove: self.movy -= cPal.__MOV_SPEED;
	def move_down(self):
		if self.fmove: self.movy += cPal.__MOV_SPEED;
	

	def movement(self):
		"""Move the Stick Rectangle"""
		if self.fmove:
			if self.turbo: self.rect = self.rect.move(self.movx*cPal.__TURBO_MULTIPLIER,self.movy*cPal.__TURBO_MULTIPLIER);
			else: self.rect = self.rect.move(self.movx,self.movy);

	def enable_disable_movement(self):
		"""sets the movement flag"""
		if self.fmove: self.fmove = False
		else: self.fmove = True

	#
	# Colision Back Rotation and jump back
	#
	def flip_rotation_tmp(self,nframes=__BACK_TICKS):
		"""
			Flips the rotation temporally for a specified number
			of frames
		"""
		if self.clockwise: self.clockwise = False
		else: self.clockwise = True
		
		if self.tbackwards: self.tbackwards = False
		else: self.tbackwards = True


		self.tbackwards_ticks = nframes
		#self.tbackwards = True

	def flip_rotation(self):
		"""
			Flips the rotation
		"""
		if self.clockwise: self.clockwise = False
		else: self.clockwise = True

	#
	# @TODO: This function NEEDS REVISION.. Seems that some cases don't work properly
	def jump_back(self,cx,cy):
		"""
			The stick Jumps Back to avoid further colisions
			cx and xy are the MAP points of collision.

			The jump back is decided by quadrants of stick collision
			To decide which direction to jump
			Q1|Q3
			------
			Q2|Q4
			
		"""
		#JUMP directions
		#jx = 0
		#jy = 0
		#Check colision position of stick (which quadrant)
		#sx = cx - self.rect.x
		#sy = cy - self.rect.y
		#sxc = self.rect.width/2
		#syc = self.rect.height/2

		#if self.clockwise:
		#	if sx < sxc and sy < syc :     #Q1
		#		jx = 0
		#		jy = +cPal.__JUMP_LENGTH
		#	elif sx < sxc and sy > syc:     #Q2
		#		jx = cPal.__JUMP_LENGTH
		#		jy = -cPal.__JUMP_LENGTH
		#	elif sx > sxc and sy < syc:     #Q3
		#		jx = cPal.__JUMP_LENGTH
		#		jy = cPal.__JUMP_LENGTH
		#	else:                           #Q4
		#		jx = 0
		#		jy = -cPal.__JUMP_LENGTH
		#else:
		#	if sx < sxc and sy < syc :      #Q1
		#		jx = cPal.__JUMP_LENGTH
		#		jy = 0
		#	elif sx < sxc and sy > syc:     #Q2
		#		jx = 0
		#		jy = -cPal.__JUMP_LENGTH
		#	elif sx > sxc and sy < syc:     #Q3
		#		jx = cPal.__JUMP_LENGTH
		#		jy = cPal.__JUMP_LENGTH
		#	else:                           #Q4
		#		jx = -cPal.__JUMP_LENGTH
		#		jy = -cPal.__JUMP_LENGTH
			
		#New easy jumpbacj
		# @TODO: If you move counter direction when bashing a wall you can get past it
		# The idea is that with the time penalty, even with that situation there's no 
		# clear wining
		jx = cPal.__JUMP_LENGTH * -(self.movx)
		jy = cPal.__JUMP_LENGTH * -(self.movy)
		self.rect = self.rect.move(jx,jy);

	#Movement to reproduce when death
	def fancy_rotation_death(self,amount,scale):
		self.rot += amount

		if self.rot >= 360: self.rot = 0;

		self.image = pygame.transform.rotozoom(self.baseImage, self.rot,scale)
		self.rect = self.image.get_rect(center=self.rect.center)

	def move_towards_position(self,ox,oy):
		"""
			ox,oy is the position to reach
		"""
		
		if (self.rect.x <= ox+5 and self.rect.x >= ox-5) \
		   and (self.rect.y <= oy+5 and self.rect.y >= oy-5):
			return True
		
		if self.rect.x > ox:
			self.movx = -1
		else:
			self.movx = 1

		if self.rect.y > oy:
			self.movy = -1
		else:
			self.movy = 1


		return False

	def turbo_on(self):
		self.turbo = True

	def turbo_off(self):
		self.turbo = False
	
	def collides(self,monster):
		"""
			Checks if the stick collides with a specific monster
		"""
		if self.rect.colliderect(monster.rect): 
			#Here need to pix perfect collision
 			trectmonst = self.rect.clip(monster.rect).move(-monster.rect.x,-monster.rect.y)
 			trectstick = self.rect.clip(monster.rect).move(-self.rect.x,-self.rect.y)
			
			tmonstmask = pygame.mask.from_surface(monster.image.subsurface(trectmonst))
 			tstickmask = pygame.mask.from_surface(self.image.subsurface(trectstick))
                	
			col = tstickmask.overlap(tmonstmask,(0,0))
                	if col == None: return False
                	else: return True
			return True
		
		else: return False
