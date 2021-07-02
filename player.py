import logging
from game_constants import *

class Player:	
	"""Creates an object controlled by the user
	
	Properties of a `Player` type object:
	- Keeps track of all the cards and thereby if they have been selected by the player
	- Can check if current life/set is valid
	- Interacts with the dealer object to give / recieve cards
	"""

	def __init__(self, player_deck, card_joker):

		self.player_deck = player_deck
		self.card_joker = card_joker

		self.pure_life = False
		self.second_life = False

		self.player_can_add_card = True
		self.player_can_remove_card = False

		self.is_main_deck_selected = False


	def swap_cards(self):
		"""Swaps the positions of 2 cards selected by user.
		Returns in case of more/less selections. De-selects all the cards."""

		cards_clicked_pos = []
		for index in range(len(self.player_deck)):
			if self.player_deck[index].clicked:
				cards_clicked_pos.append(index)

		if len(cards_clicked_pos) != 2:
			logger.info(f"In player.py/swap_cards: Invalid number of cards selected: {len(cards_clicked_pos)}")
		else:
			logger.info(f"In player.py/swap_cards: Cards swapped: {self.player_deck[cards_clicked_pos[0]]}, {self.player_deck[cards_clicked_pos[1]]}")

			self.player_deck[cards_clicked_pos[0]].rect.x, self.player_deck[cards_clicked_pos[1]].rect.x = \
			self.player_deck[cards_clicked_pos[1]].rect.x, self.player_deck[cards_clicked_pos[0]].rect.x

			self.player_deck[cards_clicked_pos[0]].rect.y, self.player_deck[cards_clicked_pos[1]].rect.y = \
			self.player_deck[cards_clicked_pos[1]].rect.y, self.player_deck[cards_clicked_pos[0]].rect.y

			self.player_deck[cards_clicked_pos[0]], self.player_deck[cards_clicked_pos[1]] = \
			self.player_deck[cards_clicked_pos[1]], self.player_deck[cards_clicked_pos[0]]

		for index in cards_clicked_pos:
			self.player_deck[index].clicked = False


	def add_card(self, card):
		"""Appends the card to self.player_deck and updates it's x-y coordinates. """

		logger.info(f"In player.py/add_card: Adding card to self.player_deck {card}")
		self.is_main_deck_selected = False

		card.rect.x = BORDER_GAP + NUM_CARDS_WITH_PLAYER * CARD_GAP
		card.rect.y = DISPLAY_HEIGHT - CARD_HEIGHT - BORDER_GAP

		card.clicked = False
		self.player_deck.append(card)

		for card in self.player_deck:
			card.clicked = False


	def remove_card(self):
		"""Removes a single selected card from self.player_deck and shifts all the cards to the right of selected card to left."""

		if not self.player_can_remove_card:
			return f"Can't remove!"

		cards_clicked_pos = []
		for i in range(len(self.player_deck)):
			if self.player_deck[i].clicked:
				cards_clicked_pos.append(i)

		if len(cards_clicked_pos) > 1:
			logger.info(f"In player.py/remove_card: Multiple cards selected to remove!")
			for index in cards_clicked_pos:
				self.player_deck[index].clicked = False
			return f"Select only 1 card to remove!"

		if len(cards_clicked_pos) == 0:
			logger.info(f"In player.py/remove_card: No card selected to remove!")
			return f"Select a card to remove!"

		self.player_can_remove_card = False

		pos = cards_clicked_pos[0] + 1
		while(pos < len(self.player_deck)):
			self.player_deck[pos].rect.x -= CARD_GAP
			pos += 1

		card_not_needed = self.player_deck[cards_clicked_pos[0]]
		
		card_not_needed.clicked = False
		self.player_deck.remove(card_not_needed)

		logger.info(f"In player.py/remove_card: Card {card_not_needed} removed from self.player_deck")

		self.player_can_add_card = True

		return card_not_needed


	def __check_life(self, cards_clicked, jokers, min_life_size):
		"""Checks if the cards sent form a valid life of atleast `min_life_size`.
		Currently this is only a helper to self.check_group."""

		if len(cards_clicked)+len(jokers) < min_life_size:
			return False

		count = 0
		for i in range(len(cards_clicked)-1):
			if len(jokers) > 0 and jokers[-1].val == card_joker.val and cards_clicked[i].val + 1 == card_joker.val:
				jokers.remove(jokers[-1])
			elif cards_clicked[i+1].val != cards_clicked[i].val + 1:
				count += 1

		if count > len(jokers):
			return False

		return True


	def __check_set(self, cards_clicked, jokers):
		"""Checks if the cards sent form a valid set.
		Currently this is only a helper to self.check_group."""

		if len(cards_clicked)+len(jokers) < 3:
			return True

		# if the card_jokers are used to make a set, then it's a valid set
		if len(cards_clicked) == 0:
			return True

		if len(jokers) > 1:
			return False


		for i in range(len(cards_clicked)):
			if cards_clicked[i].val != cards_clicked[0].val:
				return False

		return True


	def check_group(self):
		"""Checks if the cards selected form a valid life or set.
		Pure life and Second life are automatically detected.
		If found valid, the cards are removed from self.player_deck."""

		cards_clicked = []
		jokers = []
		for card in self.player_deck:
			if card.clicked:
				if card.val == self.card_joker.val or card.val == 0:
					jokers.append(card)
				else:
					cards_clicked.append(card)
				card.clicked = False

		if len(cards_clicked) < 3:
			logger.info(f"In player.py/check_group: Too less cards selected.")
			return

		cards_clicked.sort()

		cards_string = ""
		for card in cards_clicked:
			cards_string += str(card) + ", "
		logger.info(f"In player.py/check_group: checking cards: {cards_string}.")


		# check for pure life
		if not self.pure_life and not len(jokers):
			flag = self.__check_life(cards_clicked, jokers, 3)
			if flag:
				self.pure_life = True
		else:
			flag = False

		# check for second life with atleast 4 cards
		if not self.second_life and not flag:
			flag = self.__check_life(cards_clicked, jokers, 4)
			if flag:
				self.second_life = True

		# check for other possible life
		if not flag:
			flag = self.__check_life(cards_clicked, jokers, 3)

		# check for sets
		if not flag:
			flag = self.__check_set(cards_clicked, jokers)

		if flag:
			for card in cards_clicked:
					self.player_deck.remove(card)
			logger.info(f"In player.py/check_group: Valid group formed.")
		else:
			logger.info(f"In player.py/check_group: Invalid group formed.")


if __name__ == '__main__':
	pass
else:
	logger = logging.getLogger('logger.main')
