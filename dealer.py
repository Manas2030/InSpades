from game_constants import *
import logging
import time

class Dealer:
	"""Creates the game dealer who distributes all cards and prevents computer and player from accessing the `main_deck` or `discard_pile`
	
	Properties of a `Dealer` type object:
	- Has reference to the current round being played and all the different players
	- Checks when the game ends
	- Converts `discard_pile` to `main_deck` when `main_deck` goes empty
	"""


	def __init__(self, main_deck, discard_pile, card_joker, player, computer, cur_round):
		self.card_joker = card_joker
		self.main_deck = main_deck
		self.discard_pile = discard_pile
		self.card_joker = card_joker
		self.player = player
		self.computer = computer
		self.round = cur_round


	def give_card_to_player(self):
		"""Gives a card to self.player based on which of discard_pile and main_deck is selected."""

		if not self.player.player_can_add_card:
			return
		
		if self.player.is_main_deck_selected and self.discard_pile[-1].clicked:
			self.round.update_event_info(f"Select one place to add card from!")
			time.sleep(2)
			logger.info(f"In dealer.py/give_card_to_player: main deck and discard pile both selected")
			return

		if not self.player.is_main_deck_selected and not self.discard_pile[-1].clicked:
			self.round.update_event_info(f"Select some place to add card from!")
			time.sleep(2)
			logger.info(f"In dealer.py/give_card_to_player: No piles / decks selected")
			return

		self.player.player_can_add_card = False

		if self.discard_pile[-1].clicked:
			self.player.add_card(self.discard_pile[-1])
			self.computer.append_to_cards_with_player(self.discard_pile[-1])
			self.discard_pile.remove(self.discard_pile[-1])
		else:
			self.player.add_card(self.main_deck[0])
			self.main_deck.remove(self.main_deck[0])
			
		self.player.player_can_remove_card = True


	def take_card_from_player(self):
		"""Receives a card from the player and adds it to self.discard_pile after adjusting it's image location."""

		card = self.player.remove_card()
		
		if isinstance(card, str):
			self.round.update_event_info(card)
			time.sleep(2)
			return

		logger.info(f"In dealer.py/take_card_from_player: Received card: {card}")
		card.rect.x, card.rect.y = BORDER_GAP * 22, MID_CARD_POS

		self.discard_pile.append(card)
		self.computer.remove_from_cards_with_player(card)
		self.round.computer_move = True


	def give_card_to_computer(self):
		"""Gives a card to the computer based on it's decision (self.computer.make_move()) and also takes a card from it."""

		discard_pile_card = None

		if len(self.discard_pile):
			discard_pile_card = self.discard_pile[-1]

		if self.computer.make_move(self, discard_pile_card):
			card = self.computer.get_card(self.discard_pile[-1])
			self.discard_pile.remove(self.discard_pile[-1])
		else:
			card = self.computer.get_card(self.main_deck[-1])
			self.main_deck.remove(self.main_deck[-1])

		self.discard_pile.append(card)

		logger.info(f"In dealer.py/give_card_to_computer: card received: {card}")

		if self.computer.did_computer_win():
			return True
		return False


	def shuffle_discard_pile(self):
		"""Shuffles the discard_pile and makes it the main_deck when (len(self.main_deck) == 0) is True.
		Also adds top-most card to self.discard_pile from self.main_deck."""

		if not len(self.main_deck):
			logger.error(f"In dealer.py/shuffle_discard_pile: ERROR: Assigning main_deck with len(self.main_deck) != 0")
			return None

		random.shuffle(self.discard_pile)
		self.main_deck = self.discard_pile
		self.discard_pile = []
		self.discard_pile.append(self.main_deck[-1])
		self.main_deck.remove(self.main_deck[-1])


	def show_player(self):
		"""Checks if the player has/had formed valid lifes and runs."""

		if self.player.pure_life and self.player.second_life and len(self.player.player_deck) == 0:
			end_screen_text = "You Win!!"
		else:
			end_screen_text = "You Lose."
			
		self.round.game_end_screen(end_screen_text)




if __name__ == '__main__':
	pass
else:
	logger = logging.getLogger('logger.main')

