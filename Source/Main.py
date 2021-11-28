#This is my first experience working with Python.
#So there's 200% chance I wrote something wrong.
#I warned you!

from datetime import date
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
import math
import pygame.freetype
import random
import time

DANCE_FLOOR_HEIGHT = 244
DANCE_FLOOR_WIDTH = 600
DANCE_FLOOR_X = 20
DANCE_FLOOR_Y = 84
DAY_INTERVAL = 64
ENTER_INTERVAL = 4
#The coordinates of the entering door.
ENTER_X = 80
ENTER_Y = 56
#The coordinates of the exit door.
EXIT_X = 560
EXIT_Y = 56
#This is in microseconds.
FRAME_DURATION = 16667
#DJ me animation speed (The lower the value, the faster the animation).
ME_ANIMATION_SPEED = 8
SCREEN_HEIGHT = 360
SCREEN_RESIZE = 2
SCREEN_WIDTH = 640
SUBSCRIBER_ANIMATION_SPEED = 8
SUBSCRIBER_MOVE_SPEED = 1
TOTAL_SUBSCRIBER_DANCES = 4

#Don't change these 2 unless you know what you're doing.
API_SERVICE_NAME = "youtubeAnalytics"
API_VERSION = "v2"
#Download your own "Secrets.json" file from Google Cloud.
CLIENT_SECRETS_FILE = "Resources/Texts/Secrets.json"
#Did you notice that it took me EXACTLY 4 months to reach 1000 subscribers?
END_DATE = "2021-11-17"
START_DATE = "2021-07-17"

SCOPES = ["https://www.googleapis.com/auth/yt-analytics.readonly"]


class Animation:
	def __init__(self, i_animation_speed, i_frame_width, i_texture_height, i_texture_width):
		#I don't think this variable was useful. I used it only to add extra randomness for dancers.
		self.flipped = False

		self.animation_iterator = 0
		self.animation_speed = i_animation_speed
		self.current_frame = 0
		self.frame_height = i_texture_height
		self.frame_width = i_frame_width
		self.total_frames = i_texture_width / self.frame_width

		self.texture_rect = (0, 0, self.frame_width, self.frame_height)

	#I just realized that I should've just had 2 Animation object instead of this. Oh, well.
	def texture_reset(self, i_texture_width):
		self.flipped = False

		self.animation_iterator = 0
		self.current_frame = 0
		self.total_frames = i_texture_width / self.frame_width

		self.texture_rect = (0, 0, self.frame_width, self.frame_height)

	def update(self):
		self.animation_iterator += 1

		while self.animation_iterator >= self.animation_speed:
			self.animation_iterator -= self.animation_speed
			self.current_frame = (1 + self.current_frame) % self.total_frames

		#By the way, Pygame doesn't support reading the texture from right to left like SFML does so SFML: 1, Pygame: 0.
		self.texture_rect = (self.current_frame * self.frame_width, 0, self.frame_width, self.frame_height)


class Subscriber:
	def __init__(self, i_sprite_height, i_sprite_width, i_walk_texture_width, i_color, i_dance_textures, i_subscribers):
		self.dance_state = random.randrange(TOTAL_SUBSCRIBER_DANCES)
		self.dance_texture_width = i_dance_textures[self.dance_state].get_width()
		self.sprite_height = i_sprite_height
		self.sprite_width = i_sprite_width
		#0 - Subscriber just entered the party
		#1 - Subscriber is going to the dance floor
		#2 - Subscriber is dancing
		#3 - Subscriber is going to the exit door
		#4 - Subscriber is leaving
		#5 - Subscriber left
		self.state = 0
		self.walk_texture_width = i_walk_texture_width
		self.x = ENTER_X - self.sprite_width / 2
		self.y = ENTER_Y - self.sprite_height / 2

		self.color = i_color

		self.animation = Animation(SUBSCRIBER_ANIMATION_SPEED, self.sprite_width, self.sprite_height, self.walk_texture_width)

		while True:
			self.target_x = random.randrange(DANCE_FLOOR_X, DANCE_FLOOR_WIDTH + DANCE_FLOOR_X - self.sprite_width)
			self.target_y = random.randrange(DANCE_FLOOR_Y, DANCE_FLOOR_HEIGHT + DANCE_FLOOR_Y - self.sprite_height)

			#We don't want subscribers to stand in the same spot.
			for i_subscriber in i_subscribers:
				if self.target_x == i_subscriber.target_x and self.target_y == i_subscriber.target_y:
					continue
			break

	def leave(self):
		self.state = 3
		self.target_x = EXIT_X - self.sprite_width / 2
		self.target_y = EXIT_Y - self.sprite_height / 2

		#Change the sprite to walking.
		self.animation.texture_reset(self.walk_texture_width)

	def update(self):
		target_x = self.target_x
		target_y = self.target_y

		#This is to make sure subscribers don't go immediately to the dance floor.
		if 0 == self.state:
			target_x = ENTER_X - self.sprite_width / 2
			target_y = DANCE_FLOOR_Y
		elif 3 == self.state:
			target_x = EXIT_X - self.sprite_width / 2
			target_y = DANCE_FLOOR_Y

		#Look at me being smart and using trigonometry!
		move_direction = math.atan2(self.y - target_y, target_x - self.x)
		step_x = SUBSCRIBER_MOVE_SPEED * math.cos(move_direction)
		step_y = -SUBSCRIBER_MOVE_SPEED * math.sin(move_direction)

		if target_x > self.x:
			self.x = min(step_x + self.x, target_x)
		elif target_x < self.x:
			self.x = max(step_x + self.x, target_x)

		if target_y > self.y:
			self.y = min(step_y + self.y, target_y)
		elif target_y < self.y:
			self.y = max(step_y + self.y, target_y)

		if target_x == self.x and target_y == self.y:
			if 0 == self.state:
				self.state = 1
			elif 1 == self.state: #Here the subscriber starts dancing.
				self.state = 2

				self.animation.flipped = bool(random.getrandbits(1))

				self.animation.animation_iterator = random.randrange(self.animation.animation_speed)
				self.animation.current_frame = random.randrange(math.floor(self.animation.total_frames))

				self.animation.texture_reset(self.dance_texture_width)
			elif 3 == self.state:
				self.state = 4
			elif 4 == self.state:
				self.state = 5

		self.animation.update()


def draw_text(i_x, i_y, i_text, i_font_texture, i_screen):
	character_height = i_font_texture.get_height()
	#There are 96 characters in the font texture.
	character_width = i_font_texture.get_width() / 96
	character_x = i_x
	character_y = i_y

	for character in i_text:
		if '\n' == character:
			character_x = i_x
			character_y += character_height

			continue

		i_screen.blit(i_font_texture, (character_x, character_y), (character_width * (ord(character) - 32), 0, character_width, character_height))

		character_x += character_width


def get_service():
	#We're asking the permission to look at the analytics from the channel owner.
	flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
	flow.run_local_server()
	credentials = flow.credentials

	return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)


if "__main__" == __name__:
	service = get_service()
	#Requesting the data we need.
	data = service.reports().query(dimensions = "day",
	                               endDate = END_DATE,
	                               ids = "channel==MINE",
	                               metrics = "subscribersGained,subscribersLost",
	                               sort = "day",
	                               startDate = START_DATE).execute()

	#LIST COMPREHENSIONS! I LOVE YOU!
	subs_gained = [row[1] for row in data["rows"]]
	subs_lost = [row[2] for row in data["rows"]]

	service.close()

	running = True

	current_day = 0
	lag = 0
	subscribers_to_enter = subs_gained[0]
	subscribers_to_exit = subs_lost[0]
	timer = 0

	pygame.init()
	pygame.display.set_caption("Subscribers Visualization")

	background_texture = pygame.image.load("Resources/Images/Background.png")
	font_texture = pygame.image.load("Resources/Images/Font.png")
	me_texture = pygame.image.load("Resources/Images/Me.png")
	subscriber_walk_texture = pygame.image.load("Resources/Images/SubscriberWalk.png")

	#We're gonna resize this thing to fit our window to increase the pixel size.
	screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

	window = pygame.display.set_mode((SCREEN_RESIZE * SCREEN_WIDTH, SCREEN_HEIGHT * SCREEN_RESIZE))

	me_animation = Animation(ME_ANIMATION_SPEED, 80, me_texture.get_height(), me_texture.get_width())

	subscriber_colors = [pygame.Color(0, 73, 255),
	                     pygame.Color(0, 219, 0),
	                     pygame.Color(0, 219, 255),
	                     pygame.Color(109, 0, 255),
	                     pygame.Color(219, 0, 255),
	                     pygame.Color(255, 36, 0),
	                     pygame.Color(255, 219, 0),
	                     pygame.Color(255, 255, 255)]

	subscriber_dance_textures = [pygame.image.load("Resources/Images/SubscriberDance0.png"),
	                             pygame.image.load("Resources/Images/SubscriberDance1.png"),
	                             pygame.image.load("Resources/Images/SubscriberDance2.png"),
	                             pygame.image.load("Resources/Images/SubscriberDance3.png")]

	subscribers = []

	#I like being precise. So we're gonna use microseconds!
	previous_time = round(1000000 * time.perf_counter())

	while running:
		delta_time = round(1000000 * time.perf_counter()) - previous_time

		lag += delta_time
		previous_time += delta_time

		while FRAME_DURATION <= lag:
			lag -= FRAME_DURATION

			for event in pygame.event.get():
				if pygame.QUIT == event.type:
					running = False

			me_animation.update()

			if DAY_INTERVAL == timer:
				timer = 0

				if len(subs_gained) > 1 + current_day:
					current_day += 1

					subscribers_to_enter += subs_gained[current_day]
					subscribers_to_exit += subs_lost[current_day]
			else:
				timer += 1

			if 0 == timer % ENTER_INTERVAL:
				if 0 < subscribers_to_enter:
					subscribers_to_enter -= 1

					subscribers.append(Subscriber(subscriber_walk_texture.get_height(), 12, subscriber_walk_texture.get_width(), random.choice(subscriber_colors), subscriber_dance_textures, subscribers))

				#If there are no dancing subscribers we don't remove anyone.
				if 0 < subscribers_to_exit and any(2 == sub.state for sub in subscribers):
					subscribers_to_exit -= 1

					dancing_subscriber = random.choice(subscribers)

					#Making sure we only remove dancing subscribers.
					while True:
						if 2 == dancing_subscriber.state:
							break

						dancing_subscriber = random.choice(subscribers)

					dancing_subscriber.leave()

			for subscriber in subscribers:
				subscriber.update()

			#Deleting the subscribers that left.
			#Is this really deleting objects or just removing them from the array, but they're still in memory?
			#I couldn't find the answer anywhere!
			subscribers = [subscriber for subscriber in subscribers if 5 != subscriber.state]

			if FRAME_DURATION > lag:
				current_date = date.fromisoformat(START_DATE) + datetime.timedelta(days = current_day)

				screen.fill(pygame.Color(0, 0, 0))
				#By the way, "blit" stands for "Block transfer".
				#I just googled it.
				screen.blit(background_texture, (0, 0))
				screen.blit(me_texture, ((SCREEN_WIDTH - me_animation.frame_width) / 2, DANCE_FLOOR_Y - me_texture.get_height()), me_animation.texture_rect)

				#I still don't fully understand what a lambda is.
				subscribers.sort(key = lambda sub: sub.y)

				for subscriber in subscribers:
					#This may be too anti-optimization. Don't hate me for it.
					subscriber_texture = subscriber_walk_texture.copy()

					if 2 == subscriber.state:
						subscriber_texture = subscriber_dance_textures[subscriber.dance_state].copy()

					if subscriber.animation.flipped:
						subscriber_texture = pygame.transform.flip(subscriber_texture, True, False)

					subscriber_texture.fill(subscriber.color, special_flags = pygame.BLEND_RGB_MIN)

					screen.blit(subscriber_texture, (subscriber.x, subscriber.y), subscriber.animation.texture_rect)

				#I used brackets! Saw it in a video titled "Tips for Python beginners".
				draw_text(4, 4, f"Sub count: {len(subscribers)}\nDate: {current_date}", font_texture, screen)

				window.blit(pygame.transform.scale(screen, window.get_rect().size), (0, 0))
				pygame.display.update()

	pygame.quit()