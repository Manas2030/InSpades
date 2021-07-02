import pygame
import random
import time
import logging

from game_constants import *
import computer
import player
import dealer



class Button:
	"""Creates a button for interacting with user
	
	Properties of a `Button` type object:
	- Has a graphical image
	- Has x and y co-ordinates within the display screen
	- Has a linked function which performs a specific task in the function
	"""

	def __init__(self,task,image_name,x,y):
		self.image = pygame.transform.scale(pygame.image.load(f"game_icons/buttons/{image_name}.png"),(BUTTON_WIDTH,BUTTON_HEIGHT))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.task = task




class Card:
	"""Creates the game object Card
	
	Properties of a `Card` type object:
	- Has a graphical image
	- Has x and y co-ordinates within the display screen
	- Has a bool value representing if the card is selected by `Player`
	"""

	def __init__(self,suit,val):
		self.suit = suit
		self.val = val
		self.image = pygame.transform.scale(pygame.image.load(f"game_icons/cards/{val}-{suit}.jpg"),(CARD_WIDTH,CARD_HEIGHT))
		self.rect = self.image.get_rect()
		self.clicked = False


	def __str__(self):
		return str(self.val)+"-of-"+ str(self.suit)


	def __lt__(self, other):
		return self.val < other.val




class Round:
	"""Creates and initializes all the game objects, player, the computer and the dealer and runs the whole deal/round

	Properties of a `Round` type object:
	- Has a reference to a `Player`, `Computer` and `Dealer`
	- Builds and stores references to all different card decks and in-game buttons
	- Displays all the events that are occuring 
	- Handles all the events occuring by calling respective objects and their methods
	"""

	def __init__(self, player_points, computer_points):
		self.player_points = player_points
		self.computer_points = computer_points

		self.game_background = pygame.transform.scale(pygame.image.load(f"game_icons/in_game/game_bg.jpg"),(DISPLAY_WIDTH, DISPLAY_HEIGHT))

		player_deck, computer_deck, self.card_joker, self.main_deck, self.discard_pile = self.__initialize_distribute_cards()
		self.card_back = pygame.transform.scale(pygame.image.load(f"game_icons/cards/card_back.png"),(CARD_WIDTH, CARD_HEIGHT))

		logger.info(f"In main.py/Round/__init__: Card Joker chosen: {str(self.card_joker)}")

		self.computer = computer.Computer(computer_deck, self.card_joker)
		self.computer_move = False

		self.player = player.Player(player_deck, self.card_joker)
		
		self.dealer = dealer.Dealer(self.main_deck, self.discard_pile, self.card_joker, self.player, self.computer, self)

		self.running = False

		self.game_buttons = self.__initialize_game_buttons()

		self.exit_game = False

		self.event_text = ""


	def __initialize_distribute_cards(self):
		"""Builds all the `Card` objects and distributes them in various decks after shuffling."""

		# Build main_deck
		main_deck = []
		for suit in ["Diamonds","Hearts","Spades","Clubs"]:
		    for value in range(1,NUM_CARDS_WITH_PLAYER+1):
		        main_deck.append(Card(suit,value))

		random.shuffle(main_deck)

		# choose the card joker and remove it from deck
		card_joker = main_deck[0]
		card_joker.rect.x = BORDER_GAP
		card_joker.rect.y = MID_CARD_POS
		main_deck.remove(main_deck[0])

		# add the extra joker card to the deck and shuffle
		main_deck.append(Card("Joker",0))
		random.shuffle(main_deck)


		player_deck=[]
		for i in range(NUM_CARDS_WITH_PLAYER):
			player_deck.append(main_deck[i])
			main_deck.remove(main_deck[i])

		# Define co-ordinates for player_deck
		for i in range(NUM_CARDS_WITH_PLAYER):
			player_deck[i].rect.x = BORDER_GAP + i * CARD_GAP
			player_deck[i].rect.y = DISPLAY_HEIGHT - CARD_HEIGHT - BORDER_GAP

		computer_deck=[]
		for i in range(NUM_CARDS_WITH_PLAYER):
			computer_deck.append(main_deck[i])
			main_deck.remove(main_deck[i])


		discard_pile=[]
		discard_pile.append(main_deck[0])
		main_deck.remove(main_deck[0])

		return player_deck, computer_deck, card_joker, main_deck, discard_pile


	def __initialize_game_buttons(self):
		"""Builds a list of all the `Button` objects displayed during the gameplay."""

		swap_button = Button(self.player.swap_cards,'swap_button', DISPLAY_WIDTH - BUTTON_WIDTH - BORDER_GAP, BUTTON_VERTICAL_HEIGHT)
		
		remove_button = Button(self.dealer.take_card_from_player,'remove_button', DISPLAY_WIDTH - BUTTON_WIDTH - BORDER_GAP, BUTTON_VERTICAL_HEIGHT + 2*BUTTON_HEIGHT)
		
		show_button = Button(self.dealer.show_player,'show_button', DISPLAY_WIDTH - BUTTON_WIDTH - BORDER_GAP, BUTTON_VERTICAL_HEIGHT + 4*BUTTON_HEIGHT)
		
		add_button = Button(self.dealer.give_card_to_player,'add_button', DISPLAY_WIDTH - 2*BUTTON_WIDTH - 2*BORDER_GAP, BUTTON_VERTICAL_HEIGHT)
		
		check_button = Button(self.player.check_group,'check_button', DISPLAY_WIDTH - 2*BUTTON_WIDTH - 2*BORDER_GAP, BUTTON_VERTICAL_HEIGHT + 2*BUTTON_HEIGHT)
		
		go_back_button = Button(self.go_back,'go_back_button', DISPLAY_WIDTH - 2*BUTTON_WIDTH - 2*BORDER_GAP, BUTTON_VERTICAL_HEIGHT + 4*BUTTON_HEIGHT)

		game_buttons = [swap_button, add_button, remove_button, check_button, show_button, go_back_button]
		return game_buttons


	def go_back(self):
		"""Quits the indefinitely running, game-loop."""

		logger.info(f"In main.py/go_back: User pressed Go back button")
		self.running = False


	def __display_game_screen(self, update_flag = True):
		"""Generates the graphical game screen"""

		screen.blit(self.game_background,(0, 0))

		if not self.computer_move and update_flag:
			if self.player.player_can_add_card:
				self.event_text = "Select card you want to add."
			else:
				self.event_text = "Select card you want to remove."

		event_text = myfont.render(self.event_text, 10, FONT_COLOR)
		screen.blit(event_text, (BORDER_GAP, BORDER_GAP))

		# Display Computer's card deck
		for i in range(NUM_CARDS_WITH_PLAYER):
			screen.blit(self.card_back, (BORDER_GAP + i*CARD_GAP, 2*BORDER_GAP + FONT_SIZE))


		# Display Player's card deck
		for card in self.player.player_deck:
			screen.blit(card.image, (card.rect.x, card.rect.y))

		# Display Card Joker and Main Deck
		screen.blit(self.card_joker.image,(self.card_joker.rect.x,self.card_joker.rect.y))
		text = myfont.render("Card Joker", 10, FONT_COLOR)
		screen.blit(text, (BORDER_GAP/2 , MID_CARD_POS + CARD_HEIGHT))

		screen.blit(self.card_back, (BORDER_GAP * 11, MID_CARD_POS))
		text = myfont.render("Main Deck", 10, FONT_COLOR)
		screen.blit(text,(BORDER_GAP*11 - BORDER_GAP/4, MID_CARD_POS + CARD_HEIGHT))


		# display discard_pile if card is discarded, otherwise only display card_joker in some corner
		if len(self.discard_pile):
			self.discard_pile[-1].rect.x, self.discard_pile[-1].rect.y = BORDER_GAP * 22, MID_CARD_POS
			screen.blit(self.discard_pile[-1].image,(self.discard_pile[-1].rect.x, self.discard_pile[-1].rect.y))
			text = myfont.render("Discard Pile", 10, FONT_COLOR)
			screen.blit(text,(BORDER_GAP*22 - BORDER_GAP, MID_CARD_POS + CARD_HEIGHT))

		for button in self.game_buttons:
			screen.blit(button.image, (button.rect.x, button.rect.y))


	def game_end_screen(self, text):
		"""Displays the `text` on screen and ends the current round being played."""

		if "win" in text.lower():
			self.player_points += INITIAL_COMPUTER_POINTS
		else:
			self.player_points -= INITIAL_PLAYER_POINTS

		screen.blit(self.game_background,(0, 0))
		
		myfont = pygame.font.SysFont("castellar", 5*FONT_SIZE)

		text = myfont.render(text, 10, FONT_COLOR)
		text_pos = text.get_rect(center = (DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2))
		screen.blit(text, text_pos)

		click_anywhere_font = pygame.font.SysFont("calibri", FONT_SIZE)
		text = click_anywhere_font.render("Click anywhere to continue", 10, FONT_COLOR)
		text_pos = text.get_rect(center = (DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2 + 10*FONT_SIZE + BORDER_GAP))
		screen.blit(text, text_pos)

		pygame.display.update()
		
		
		end_screen_running = True
		while end_screen_running:
			for event in pygame.event.get():
				if(event.type == pygame.QUIT):
					self.exit_game = True
					end_screen_running = False
				if(event.type == pygame.MOUSEBUTTONDOWN):
					end_screen_running = False

		self.running = False


	def update_event_info(self, text):
		"""Updates the message for the player."""

		logger.info(f"In main.py/update_event_info: text: {text}")
		self.event_text = text
		self.__display_game_screen(False)
		pygame.display.update()


	def game_logic(self):
		"""This function is called from `game_loop` to check for any new events."""

		if not len(self.main_deck):
			self.dealer.shuffle_discard_pile()
		if self.computer_move:
			logger.info(f"In main.py/game_logic: Computer is making a move.")
			self.update_event_info(f"Computer is making a move")
			if self.dealer.give_card_to_computer():
				self.game_end_screen("Computer Won!")
			self.computer_move = False
		for event in pygame.event.get():
			if(event.type == pygame.QUIT):
				self.running = False
				self.exit_game = True
			if(event.type == pygame.MOUSEBUTTONDOWN):
				pos = pygame.mouse.get_pos()
				if(event.button == 1):
					for card in self.player.player_deck:
						if(card.rect.collidepoint(pos)):
							if(card.clicked):
								card.clicked=False
							else:
								card.clicked=True
					mouse = pygame.mouse.get_pos()

					for button in self.game_buttons:
						if button.rect.collidepoint(pos):
							button.task()

					if(BORDER_GAP * 11 <= mouse[0] <= BORDER_GAP * 11 + CARD_WIDTH and MID_CARD_POS <= mouse[1] <= MID_CARD_POS + CARD_HEIGHT):
						self.player.is_main_deck_selected = not self.player.is_main_deck_selected

						if(len(self.discard_pile)):
							self.discard_pile[-1].clicked=False
					elif(len(self.discard_pile)):
						if(self.discard_pile[-1].rect.collidepoint(pos)):
							self.discard_pile[-1].clicked=True
		self.__display_game_screen()


	def game_loop(self):
		"""The game_loop for self."""
		self.running = True

		while(self.running):
			self.game_logic()

			pygame.display.update()	

		logger.info(f"In main.py/Round/game_loop: Exiting loop")		
		
		return self.exit_game, self.player_points






class Game:
	"""Handles user interaction in the menu and instantiates different `Rounds` for user to play
	- Every new instance of game, loads the user with `game_constants.INITIAL_PLAYER_POINTS`
	"""

	def __init__(self, initial_player_points, initial_computer_points):

		pygame.mixer.music.load(MUSIC_NAME)
		pygame.mixer.music.play(loops = -1)
		pygame.mixer.music.set_volume(0.5)
		self.is_music_on = True

		self.player_points = initial_player_points
		self.computer_points = initial_computer_points

		self.menu_background = pygame.transform.scale(pygame.image.load(f"game_icons/in_game/start_menu_bg.jpg"),(DISPLAY_WIDTH, DISPLAY_HEIGHT))

		self.running = True

		self.menu_buttons = self.__initialize_menu_buttons()


	def __initialize_menu_buttons(self):
		"""Builds all the `Button` objects displayed when the user is in the menu screen."""

		start_game_button = Button(self.start_game, 'start_button', (DISPLAY_WIDTH - BUTTON_WIDTH)/2, 300)
		switch_music_button = Button(self.switch_music, 'switch_music_button', (DISPLAY_WIDTH - BUTTON_WIDTH)/2, 400)
		exit_game_button = Button(self.exit_game, 'exit_game_button', (DISPLAY_WIDTH - BUTTON_WIDTH)/2, 500)

		menu_buttons = [start_game_button, switch_music_button, exit_game_button]
		return menu_buttons


	def start_game(self):
		"""Initializes a `Round` object to start a new game round."""

		round = Round(self.player_points, self.computer_points)
		flag, self.player_points = round.game_loop()
		if flag:
			self.running = False


	def exit_game(self):
		"""Changes game-loop condition to False."""

		self.running = False


	def switch_music(self):
		"""Switches the music."""

		if self.is_music_on:
			self.is_music_on = False
			pygame.mixer.music.stop()
		else:
			self.is_music_on = True
			pygame.mixer.music.play(loops = -1)
		logger.info(f"In main.py/switch_music: is_music_on: {self.is_music_on}")


	def display_menu_screen(self):
		"""Generates the graphical menu screen."""

		screen.blit(self.menu_background,(0, 0))

		for button in self.menu_buttons:
			screen.blit(button.image,(button.rect.x,button.rect.y))

		myfont = pygame.font.SysFont("castellar", 5*FONT_SIZE)
		text = myfont.render("In Spades", 10, FONT_COLOR)
		text_pos = text.get_rect(center = (DISPLAY_WIDTH/2, 5*FONT_SIZE + BORDER_GAP))
		screen.blit(text, text_pos)

		myfont = pygame.font.SysFont("castellar", 30)
		text = myfont.render(f"Chips Owned: {self.player_points}", 10, FONT_COLOR)
		screen.blit(text, (DISPLAY_WIDTH-350, DISPLAY_HEIGHT-3*FONT_SIZE))


	def game_loop(self):
		"""Game-loop for the game."""

		while(self.running):
			pygame.time.delay(50)
			for event in pygame.event.get():
				if(event.type == pygame.QUIT):
					self.running = False
				if(event.type == pygame.MOUSEBUTTONDOWN):
					pos=pygame.mouse.get_pos()
					if(event.button == 1):
						for button in self.menu_buttons:
							if button.rect.collidepoint(pos):
								button.task()
			self.display_menu_screen()

			pygame.display.update()

		logger.info(f"In main.py/Game/game_loop: Exiting loop")






if __name__ == '__main__':

	pygame.init()
	pygame.mixer.init()
	logging.basicConfig(level = logging.INFO)

	logger = logging.getLogger('logger.main')
	handler = logging.FileHandler('GameLog.log')
	logger.addHandler(handler)

	# TODO: Make accessors and mutators
	# TODO: Write test code
	# TODO: Would this require docs?

	logger.info(f"In main.py/__'main'__: -------------NEW RUN-------------")

	screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
	pygame.display.set_caption("In Spades")
	myfont = pygame.font.SysFont("monospace", FONT_SIZE)

	logger.info(f"In main.py/__'main'__: initializing instance of `Game`")
	game = Game(INITIAL_PLAYER_POINTS, INITIAL_COMPUTER_POINTS)
	game.game_loop()

	pygame.quit()

	logger.info(f"In main.py/__'main'__: ---------------------------------")
