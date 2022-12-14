import pygame, random, sys, re

# FPS and clock
FPS = 60
clock = pygame.time.Clock()
# Define Colors
GREEN = (13, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 3, 3)

# Create Display Surface(SCALE = 16 / 9)
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 675

display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))


class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.pos_unhover = (x, y)
		self.pos_hover = (x, y - 3)
	
	def draw(self, surface):
		surface.blit(self.image, self.rect)
		pos = pygame.mouse.get_pos()
		if self.rect.collidepoint(pos):
			self.rect.center = self.pos_hover
		else:
			self.rect.center = self.pos_unhover


class Thumb_nail():
	def __init__(self, x, y, image):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (width, height))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.pos_unhover = (x, y)
		self.pos_hover = (x, y - 10)
		self.click = False
	
	def draw(self, surface):
		surface.blit(self.image, self.rect)
		pos = pygame.mouse.get_pos()
		if self.rect.collidepoint(pos) or self.click:
			self.rect.center = self.pos_hover
		else:
			self.rect.center = self.pos_unhover


class Item_skill(pygame.sprite.Sprite):
	def __init__(self, type, index, image, group, player):
		super().__init__()
		self.index = index
		self.type = type
		self.image = image
		self.item_group = group
		self.rect = self.image.get_rect()
		self.player = player
		self.rect.topleft = player.rect.topright
		distance = my_game.map_rects[my_game.map_length - 1].right - player.rect.right
		if player.running == False:
			self.remove(group)
		if distance > 200:
			self.rect.x += random.randint(100
			                              , min(500, int(distance - self.image.get_width())))
	
	def update(self):
		if my_game.scroll_map_bool:
			self.rect.x -= 2
		if pygame.sprite.collide_rect(self, self.player):
			# Set timeskill
			if self.type == 1:
				self.player.speed_up_time += FPS  # one second
			elif self.type == 2:
				self.player.slow_down_time += FPS  # three seconds
			elif self.type == 4:
				self.player.reverse_time += FPS
			elif self.type == 3:
				self.player.positionx += 300  # tele300 pixel
			elif self.type == 5:
				self.player.rect.right = my_game.map_rects[my_game.map_length - 1].right
				self.win_absolute = True
			elif self.type == 6:
				self.player.positionx = my_game.map_rects[0].left
			self.remove(self.item_group)
			my_game.collect_sound.play()


class Game():
	def __init__(self):
		self.scroll = 0
		self.direction_scroll = 1
		self.time = 0
		self.frame_count = 0
		# Get BACKGROUND
		image = pygame.image.load("./asset/image/back.webp").convert()
		scale = int(image.get_width() / image.get_height())
		self.back_ground_image = pygame.transform.scale(image, (int(WINDOW_HEIGHT * scale), WINDOW_HEIGHT))
		
		# Font
		self.font32 = pygame.font.Font("./asset/font/font1.ttf", 32)
		
		# sound
		self.collect_sound = pygame.mixer.Sound("./asset/music/collect_music.mp3")
		self.race_music = pygame.mixer.Sound("./asset/music/race_music.mp3")
		
		# Item image
		self.item_image = []
		for i in range(6):
			image = pygame.image.load(f"./asset/skill/{i + 1}.png")
			scale = image.get_width() / image.get_height()
			self.item_image.append(
				pygame.transform.scale(image, (int(scale * WINDOW_HEIGHT * 0.15), int(WINDOW_HEIGHT * 0.15))))
		
		# Game Value, SET in TEXT file
		self.gold = 1000
		self.map = 1
		self.set = 1
		self.bet = 1
		self.rank = []
		self.history = []
	
	def main(self):
		running = True
		while running:
			# Check close
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				self.show_main_menu()
			clock.tick(FPS)
	
	def show_main_menu(self):
		# Music
		self.menu_music = pygame.mixer.Sound("./asset/music/menu_music.mp3")
		self.menu_music.set_volume(.2)
		# Button menu
		start_button = Button(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3,
		                      pygame.image.load("./asset/button/start_button.png"), 0.2)
		setting_button = Button(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3 + 130,
		                        pygame.image.load("./asset/button/setting_button.png"), 0.2)
		
		self.menu_music.stop()
		self.menu_music.play(-1)
		
		main_menu_run = True
		while main_menu_run:
			self.show_back_ground()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				# CHECK CLICK BUTTON
				if event.type == pygame.MOUSEBUTTONDOWN:
					pos = pygame.mouse.get_pos()
					if start_button.rect.collidepoint(pos):
						self.start_new_round()
					
					if setting_button.rect.collidepoint(pos):
						self.show_setting()
			
			start_button.draw(display_surface)
			setting_button.draw(display_surface)
			pygame.display.update()
			clock.tick(FPS)
	
	def show_back_ground(self):
		if self.scroll <= 0:
			self.direction_scroll = 1
		if self.scroll >= self.back_ground_image.get_width() - WINDOW_WIDTH:
			self.direction_scroll = -1
		self.scroll += self.direction_scroll * .5
		display_surface.blit(self.back_ground_image, (-self.scroll, 0))
	
	def start_new_round(self):
		self.show_map()
	
	def show_setting(self):
		# Set button
		image = pygame.image.load("./asset/button/go_back_button.png")
		scale = image.get_width() / image.get_height()
		image = pygame.transform.scale(image, (int(0.0688 * WINDOW_HEIGHT * scale), int(0.0688 * WINDOW_HEIGHT)))
		# GO BACK BUTTON
		go_back_button = Button(int(0.051 * WINDOW_WIDTH + image.get_width() / 2), int(0.075 * WINDOW_HEIGHT), image, 1)
		setting = True
		while setting:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					pos = pygame.mouse.get_pos()
					# Check click Map
					if go_back_button.rect.collidepoint(pos):
						setting = False
			
			self.show_back_ground()
			# DRAW BUTTON
			go_back_button.draw(display_surface)
			pygame.display.update()
			clock.tick(FPS)
	
	def show_bet(self):
		# Load Text
		gold_text = self.font32.render(f'Gold:  {self.gold}', True, YELLOW)
		gold_text_rect = gold_text.get_rect()
		gold_text_rect.topleft = (0.15 * WINDOW_WIDTH, int(0.62 * WINDOW_HEIGHT))
		
		user_text = "100"
		
		bet_text = self.font32.render(f' BET: {user_text}', True, YELLOW)
		bet_text_rect = bet_text.get_rect()
		bet_text_rect.topleft = (int(0.15 * WINDOW_WIDTH), int(0.7 * WINDOW_HEIGHT))
		
		text_box = pygame.Rect(int(0.15 * WINDOW_WIDTH), int(0.7 * WINDOW_HEIGHT), WINDOW_WIDTH // 3,
		                       WINDOW_HEIGHT // 10)
		color = YELLOW
		active = False
		error = False
		
		bet_text_rect.centery = 0.7 * WINDOW_HEIGHT + text_box.h / 2
		
		# Play button
		image = pygame.image.load("./asset/button/play_now_button.png")
		scale = image.get_height() / image.get_width()
		image = pygame.transform.scale(image, (int(0.33 * WINDOW_WIDTH), int(scale * 0.33 * WINDOW_WIDTH)))
		play_button = Button(int(0.8 * WINDOW_WIDTH), int(0.72 * WINDOW_HEIGHT), image, 1)
		
		# Load thumbnail
		self.bet_thumbnail_images = []
		for i in range(5):
			image = pygame.image.load(f'./asset/set/set_avt/1{i + 1}.png')
			scale = image.get_height() / image.get_width()
			image = pygame.transform.scale(image, (int(0.1525 * WINDOW_WIDTH), int(0.1525 * WINDOW_WIDTH * scale)))
			self.bet_thumbnail_images.append(image)
		
		self.bet_thumbnails = []
		for i in range(5):
			thumbnail = Thumb_nail(int(((0.15 + i * (0.1525 + 0.063 / 2)) * WINDOW_WIDTH))
			                       , int(0.195 * WINDOW_HEIGHT), self.bet_thumbnail_images[i])
			self.bet_thumbnails.append(thumbnail)
		
		# Go back button
		image = pygame.image.load("./asset/button/go_back_button.png")
		scale = image.get_width() / image.get_height()
		image = pygame.transform.scale(image, (int(0.0688 * WINDOW_HEIGHT * scale), int(0.0688 * WINDOW_HEIGHT)))
		go_back_button = Button(int(0.051 * WINDOW_WIDTH + image.get_width() / 2), int(0.075 * WINDOW_HEIGHT), image, 1)
		
		# User click the thumnail
		have_click = False
		betting = True
		while betting:
			if have_click == False:
				for i in range(5):
					if self.bet_thumbnails[i].click:
						have_click = True
						break
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					pos = pygame.mouse.get_pos()
					# Check click GO BaCK
					if go_back_button.rect.collidepoint(pos):
						betting = False
					# CHeck click thumbnail
					for i in range(5):
						if self.bet_thumbnails[i].rect.collidepoint(pos):
							self.bet_thumbnails[i].click = True
							for j in range(5):
								if j == i:
									continue
								self.bet_thumbnails[j].click = False
					# Check Click Box
					if text_box.collidepoint(pos):
						active = True
					else:
						active = False
					
					# CHeck click play_now
					if play_button.rect.collidepoint(pos):
						if not error and have_click:
							self.race()
				
				if event.type == pygame.KEYDOWN:
					if active:
						if event.key == pygame.K_BACKSPACE:
							user_text = user_text[0: -1]
						else:
							if len(user_text) <= 12:
								user_text += event.unicode
			
			# Check error
			error = (len(user_text) >= 13) or (not user_text.isdigit()) or (int(user_text) <= 0) or (
				int(user_text) > self.gold)
			self.show_back_ground()
			# Draw character
			for i in range(5):
				self.bet_thumbnails[i].draw(display_surface)
			# DRAW BUTTON
			go_back_button.draw(display_surface)
			play_button.draw(display_surface)
			
			# CHECK COLORS OF THE BOX
			if active:
				if error:
					color = RED
				else:
					color = GREEN
			else:
				color = YELLOW
			
			gold_text = self.font32.render(f'Gold:  {self.gold}', True, YELLOW)  # Update HUD
			bet_text = self.font32.render(f' BET: {user_text}', True, color)  # Update HUD
			display_surface.blit(gold_text, gold_text_rect)
			display_surface.blit(bet_text, bet_text_rect)
			pygame.draw.rect(display_surface, color, text_box, 3)
			
			pygame.display.update()
			clock.tick(FPS)
	
	def show_map(self):
		# SET BUTTON
		self.map_thumbnail_images = []
		for i in range(1, 7):
			image = pygame.image.load(f"./asset/map/showmap{i}.png")
			image = pygame.transform.scale(image, (int(0.271 * WINDOW_WIDTH), int(0.271 * WINDOW_HEIGHT)))
			self.map_thumbnail_images.append(image)
		
		self.map_thumbnail = []
		# Chua te hard code
		for i in range(6):
			if i <= 2:
				self.map_thumbnail.append(
					Button(int(i * (self.map_thumbnail_images[i].get_width() + 0.040 * WINDOW_WIDTH)
					           + 0.051 * WINDOW_WIDTH + self.map_thumbnail_images[i].get_width() / 2),
					       int(0.314 * WINDOW_HEIGHT)
					       , self.map_thumbnail_images[i], 1))
			else:
				self.map_thumbnail.append(
					Button(int((i - 3) * (self.map_thumbnail_images[i].get_width() + 0.040 * WINDOW_WIDTH)
					           + 0.051 * WINDOW_WIDTH + self.map_thumbnail_images[i].get_width() / 2),
					       int((0.314 + 0.377) * WINDOW_HEIGHT), self.map_thumbnail_images[i], 1))
		# GO BACK BUTTON
		image = pygame.image.load("./asset/button/go_back_button.png")
		scale = image.get_width() / image.get_height()
		image = pygame.transform.scale(image, (int(0.0688 * WINDOW_HEIGHT * scale), int(0.0688 * WINDOW_HEIGHT)))
		go_back_button = Button(int(0.051 * WINDOW_WIDTH + image.get_width() / 2), int(0.075 * WINDOW_HEIGHT), image, 1)
		mapping = True
		while mapping:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					pos = pygame.mouse.get_pos()
					# Check click Map
					for i in range(6):
						if self.map_thumbnail[i].rect.collidepoint(pos):
							self.map = i + 1
							self.show_set()
					if go_back_button.rect.collidepoint(pos):
						mapping = False
			
			self.show_back_ground()
			# DRAW BUTTON
			for i in range(6):
				self.map_thumbnail[i].draw(display_surface)
			
			go_back_button.draw(display_surface)
			pygame.display.update()
			clock.tick(FPS)
	
	def show_set(self):
		# Lay ra anh thumbnail
		image = pygame.image.load(f"./asset/set/set_avt/all_set1.png")
		image = pygame.transform.scale(image, (int(0.286 * WINDOW_HEIGHT), int(0.286 * WINDOW_HEIGHT)))
		images = [image, image, image, image, image]
		self.sets_thumbnail = []
		# Chua te hard code
		for i in range(5):
			if i <= 2:
				self.sets_thumbnail.append(Button(int(0.192 * WINDOW_WIDTH + i * (0.16 + 0.146) * WINDOW_WIDTH)
				                                  , int(0.317 * WINDOW_HEIGHT), images[i], 1))
			else:
				self.sets_thumbnail.append(Button(int(0.192 * WINDOW_WIDTH + (i - 3) * (0.16 + 0.146) * WINDOW_WIDTH)
				                                  , int(0.7196 * WINDOW_HEIGHT), images[i], 1))
		# Set button
		image = pygame.image.load("./asset/button/go_back_button.png")
		scale = image.get_width() / image.get_height()
		image = pygame.transform.scale(image, (int(0.0688 * WINDOW_HEIGHT * scale), int(0.0688 * WINDOW_HEIGHT)))
		# GO BACK BUTTON
		
		go_back_button = Button(int(0.051 * WINDOW_WIDTH + image.get_width() / 2), int(0.075 * WINDOW_HEIGHT), image, 1)
		chosing_set = True
		while chosing_set:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					pos = pygame.mouse.get_pos()
					# Check click GO BaCK
					if go_back_button.rect.collidepoint(pos):
						chosing_set = False
					# Check chosing set
					for i in range(5):
						if self.sets_thumbnail[i].rect.collidepoint(pos):
							self.set = i + 1
							self.show_bet()
			self.show_back_ground()
			# DRAW BUTTON
			for i in range(5):
				self.sets_thumbnail[i].draw(display_surface)
			go_back_button.draw(display_surface)
			pygame.display.update()
			clock.tick(FPS)
	
	def show_victory(self):
		pass
	
	def show_HUD(self):
		pass
	
	def count_down(self):
		num3_image = pygame.transform.scale(pygame.image.load("./asset/image/num3.png"),
		                                    (WINDOW_WIDTH // 2, WINDOW_WIDTH // 2))
		num2_image = pygame.transform.scale(pygame.image.load("./asset/image/num2.png"),
		                                    (WINDOW_WIDTH // 2, WINDOW_WIDTH // 2))
		num1_image = pygame.transform.scale(pygame.image.load("./asset/image/num1.png"),
		                                    (WINDOW_WIDTH // 2, WINDOW_WIDTH // 2))
		rect = num3_image.get_rect()
		rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
		
		music = pygame.mixer.Sound("./asset/music/count_down_music.mp3")
		
		frame_count = 0
		time = 3
		music.play()
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
			frame_count += 1
			if frame_count == FPS / 10:
				frame_count = 0
				time -= 0.1
			display_surface.fill(BLACK)
			if time > 2:
				display_surface.blit(num3_image, rect)
			if time <= 2 and time > 1:
				display_surface.blit(num2_image, rect)
			if time <= 1 and time > 0:
				display_surface.blit(num1_image, rect)
			if time <= 0:
				break
			clock.tick(FPS)
			pygame.display.update()
	
	def race(self):
		self.menu_music.stop()
		self.map_length = 3
		racing = True
		# Set n road continous
		map = pygame.transform.scale(pygame.image.load(f"./asset/map/map{self.map}.png"), (WINDOW_WIDTH, WINDOW_HEIGHT))
		self.map_rects = []
		for i in range(self.map_length):
			rect = map.get_rect()
			if i > 0:
				rect.topleft = self.map_rects[i - 1].topright
			else:
				rect.topleft = (0, 0)
			self.map_rects.append(rect)
		
		# Set back map
		backmap = pygame.image.load(f"./asset/map/backmap{self.map}.jpg")
		scale = backmap.get_width() / backmap.get_height()
		backmap = pygame.transform.scale(backmap, (WINDOW_HEIGHT * scale, WINDOW_HEIGHT))
		self.player_group = pygame.sprite.Group()
		
		# Item
		item_group = pygame.sprite.Group()
		
		# Add Character
		for i in range(1, 6):
			player = Player(i, 0, WINDOW_HEIGHT * 0.263 + (i - 1) * WINDOW_HEIGHT * 0.174, self.player_group)
			self.player_group.add(player)
		
		# scroll variables
		self.scroll_map = 2
		scroll_backmap = 0
		self.scroll_map_bool = True
		
		# count down
		self.count_down()
		self.race_music.play()
		
		# Main loop
		while racing:
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					pos = pygame.mouse.get_pos()
			# time getting
			self.frame_count += 1
			if self.frame_count == FPS:
				self.time += 1
			
			# Scroll the back_ground behide
			display_surface.blit(backmap, (0, 0))
			
			
			display_surface.blit(map, self.map_rects[0])
			
			# Run the player
			self.player_group.update()
			self.player_group.draw(display_surface)
			
			
			
			pygame.display.update()
			clock.tick(FPS)


class Player(pygame.sprite.Sprite):
	def __init__(self, index, x, y, group):
		super().__init__()
		self.index = index
		self.origin_speed = random.uniform(2,4)
		self.animate_fps = .3
		self.running = True
		self.win_absolute = False
		self.has_boost = False
		self.group = group
		self.speed = self.origin_speed
		self.origin_frame = []
		self.speed_up_time = self.reverse_time = self.slow_down_time = 0
		
		for i in range(9):
			image = pygame.image.load(f"./asset/set/set{my_game.set}/{self.index}/{i + 1}.png")
			scale = image.get_width() / image.get_height()
			self.origin_frame.append(
				pygame.transform.scale(image, (int(WINDOW_HEIGHT * 0.15 * scale), int(WINDOW_HEIGHT * 0.15))))
		
		self.flip_frame = []
		for i in range(9):
			self.flip_frame.append(pygame.transform.flip(self.origin_frame[i], True, False))
		
		self.frame = self.origin_frame
		self.current_frame = 0
		self.image = self.frame[self.current_frame]
		self.rect = self.image.get_rect()
		self.rect.bottomleft = (x, y)
		self.positionx = x
	
	def skill(self):
		if self.reverse_time > 0:
			self.speed_up_time = self.slow_down_time = 0
			self.reverse_time -= 1
			self.speed = -2
			self.frame = self.flip_frame
		else:
			self.speed = self.origin_speed
			self.frame = self.origin_frame
		
		if self.speed_up_time + self.slow_down_time == 0:
			if self.reverse_time == 0:
				self.speed = self.origin_speed
		
		elif self.speed_up_time > self.slow_down_time and self.speed_up_time > 0:
			self.speed = self.origin_speed + 2
			self.slow_down_time = 0
			self.speed_up_time -= 1
		
		elif self.speed_up_time < self.slow_down_time and self.slow_down_time > 0:
			self.speed = self.origin_speed - 2
			self.slow_down_time -= 1
			self.speed_up_time = 0
	
	def update(self):
		self.skill()
		if self.running:
			self.positionx += self.speed
			self.rect.x = int(self.positionx)
			self.animate(self.animate_fps)
		if self.rect.right >= my_game.map_rects[my_game.map_length - 1].right:
			self.rect.right = my_game.map_rects[my_game.map_length - 1].right
			self.get_race()
			my_game.scroll_map = 0
			my_game.scroll_map_bool = False
		
		'''if self.rect.right >= WINDOW_WIDTH:
			for player in self.group.sprites():
				player.positionx -= WINDOW_WIDTH - self.image.get_width()
			my_game.map_rects[0].left -= WINDOW_WIDTH - self.image.get_width()
			for i in range(1,my_game.map_length - 1):
				my_game.map_rects[i].left = my_game.map_rects[i-1].right'''
	
	def get_race(self):
		if not self.win_absolute:
			self.running = False
			my_game.rank.append(self)
			for player in self.group.sprites():
				if player == self:
					continue
				if not player.has_boost:
					player.origin_speed += 2
					player.has_boost = True
	
	def animate(self, fps):
		self.current_frame += fps
		if self.current_frame >= 8:
			self.current_frame = 0
		self.image = self.frame[int(self.current_frame)]


pygame.init()
my_game = Game()
my_game.main()
