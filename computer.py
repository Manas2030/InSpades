import logging
from time import sleep

class Computer:
	"""Creates a virtual computer who plays the game with the player
	
	Properties of a `Computer` type object:
	- Keeps all it's cards as a list of different sets and lives (list of lists)
	- Capable of checking if the computer won
	- Can form relevant groups from the specified cards
	- Computer waits for 2 seconds before making a decision to give a realistic feel
	"""

	def __init__(self, computer_deck, card_joker):

		self.card_joker = card_joker
		self.grps = []
		self.jokers = []
		self.build_groups(computer_deck)
		self.cards_with_player = []


	def build_groups(self, computer_deck):
		"""Divides the deck in the argument into different most suitable groups."""

		computer_deck.sort()
		
		for card in computer_deck:
			self.add_card_to_grps(card)

		self.grps = sorted(self.grps, key = lambda x: -len(x))

		logger.info(f"In computer.py/build_groups: computer: {self}")


	def get_card(self, card):
		"""Recieves a card from a `Dealer` object and returns 1 card back to `Dealer`.
		Note: Currently it removes the card from group with least size."""

		self.add_card_to_grps(card)

		self.grps = sorted(self.grps, key = lambda x: -len(x))


		# check if # of cards forming sets is more than 5; if yes, then break the set to allow computer to form runs
		num_set_cards = 0
		pos = -1
		for i in range(len(self.grps)):
			if len(self.grps[i]) > 1 and self.grps[i][0] == self.grps[i][1]:
				num_set_cards += len(self.grps[i])
				pos = i

		if num_set_cards > 5:
			card = self.grps[pos][-1]
			self.grps[pos].remove(card)
			logger.info(f"In computer.py/get_card: computer returned {card} to break too many set, computer = {self}")
			return card


		# if # of sets is fine, then remove a card from the group with least size
		card = self.grps[-1][-1]

		
		if len(self.grps[-1]) == 1:
			self.grps.remove(self.grps[-1])
		else:
			self.grps[-1].remove(self.grps[-1][-1])

		logger.info(f"In computer.py/get_card: computer returned {card}, computer = {self}")

		return card


	def add_card_to_grps(self, card):
		"""Adds the card in the argument to most suitable group in self.grps
		Note: Currently, it adds to a valid group with smallest size."""

		if card.val == self.card_joker.val or card.val == 0:
			self.jokers.append(card)
		else:
			new_grp = True

			for grp in self.grps[::-1]:
				if len(grp) >= 4:
					continue
				is_a_set = True
				val = grp[0].val

				for grp_card in grp:
					if grp_card.val != val:
						is_a_set = False

				if is_a_set and card.val == val:
					new_grp = False
					grp.append(card)
					break

				if (not is_a_set or len(grp) == 1) and card.val == grp[-1].val+1:
					new_grp = False
					grp.append(card)
					break
			
			if new_grp:
				self.grps.append([card])


	def did_computer_win(self):
		"""Checks if the computer can win with the current lives and sets."""

		num_jokers = len(self.jokers)

		# check if pure run exists; try forming pure run from groups in range [1, len(self.grps)] so we can form an impure run from the largest group
		# in case we don't find pure groups then check for pure group at self.grps[0]
		is_pure_run = False
		pure_run_pos = -1
		
		if len(self.grps) < 2:
			return False

		for i in range(1, len(self.grps)):
			is_a_set = True
			for grp_card in self.grps[i]:
				if grp_card.val != self.grps[i][0].val:
					is_a_set = False
					break
			if not is_a_set and len(self.grps[i]) > 2:
				is_pure_run = True
				pure_run_pos = i
				break

		if not is_pure_run:
			if len(self.grps[0]) > 2 and self.grps[0][1].val == self.grps[0][0].val + 1:
				is_pure_run = True
				pure_run_pos = 0

		if not is_pure_run:
			logger.info(f"In computer.py/did_computer_win: computer: {self}, is_pure_run: {is_pure_run}")
			return False



		# check if second life exists; try forming second life with the largest run we have in the moment. 
		# If length of that life is less < 4, then try using as many jokers as possible.
		is_second_life = False
		second_life_pos = -1
		for i in range(len(self.grps)):
			if i == pure_run_pos: 
				continue

			# if self.grps[i] is a set then continue
			if len(self.grps[0]) > 1 and self.grps[i][0] == self.grps[i][1]:
				continue

			if len(self.grps[i]) + num_jokers >= 4:
				is_second_life = True
				second_life_pos = i
				if len(self.grps[i]) < 4:
					num_jokers -= 4 - len(self.grps[i])
			break

		if not is_second_life:
			logger.info(f"In computer.py/did_computer_win: computer: {self}, is_second_life: {is_second_life}")
			return False



		# use a joker card for every group smaller than 3; if # of jokers go negative then we can't form valid groups
		for i in range(len(self.grps)):
			if i == pure_run_pos or i == second_life_pos or len(self.grps[i])>2:
				continue
			num_jokers -= (3 - len(self.grps[i]))

		if num_jokers < 0:
			logger.info(f"In computer.py/did_computer_win: computer: {self}, num_jokers: {num_jokers}")
			return False

		logger.info(f"In computer.py/did_computer_win: valid group found for computer: {self}")
		return True



	def append_to_cards_with_player(self, card):
		self.cards_with_player.append(card)

	def remove_from_cards_with_player(self, card):
		try: 
			self.cards_with_player.remove(card)
		except:
			pass


	def make_move(self, dealer, discard_pile_card):
		"""Makes a decision to choose a card from main deck or the discard pile. 
		Returns True if computer chooses a card from discard_pile."""
		
		sleep(2)

		choose_from_discard = True

		# if discard pile is empty, choose from main deck
		if discard_pile_card is None:
			choose_from_discard = False
		else:

			# make a list of all the cards that I can use to make sets and lives
			cards_needed = []
			cards_needed_freq = []

			for grp in self.grps:
				if len(grp) >= 3:
					continue

				is_a_set = True
				for i in range(len(grp)):
					if grp[i].val != grp[0].val:
						is_a_set = False

				if is_a_set:
					cards_needed.append(grp[0].val)
				else:
					cards_needed.append(grp[-1].val+1)
				
				cards_needed_freq.append(4)

			# if the player or computer have some card that the computer needs, then reduce probability of getting that card.
			for grp in self.grps:
				for card in grp:
					try:
						ind = cards_needed.index(card.val)
						cards_needed_freq[ind] -= 1
					except:
						pass
			
			for card in self.cards_with_player:
				try:
					ind = cards_needed.index(card.val)
					cards_needed_freq[ind] -= 1
				except:
					pass

			# log the cards needed by computer
			string = "cards_needed: (val: freq) = "
			for i in range(len(cards_needed)):
				string += "(" + str(cards_needed[i]) + ": " + str(cards_needed_freq[i]) + "), "
			logger.info(f"In computer.py/make_move: discard_pile_card: {discard_pile_card}, {string}")


			# If we don't need the top card in Discard Pile then `choose_from_discard` = False
			flag = False
			for i in range(len(cards_needed)):
				if cards_needed_freq[i] > 0 and cards_needed[i] == discard_pile_card.val:
					flag = True
					break

			if not flag:
				choose_from_discard = False


		logger.info(f"In computer.py/make_move: choose_from_discard: {choose_from_discard}")
		return choose_from_discard


	def __str__(self):
		"""String overloading to display the current state of computer."""
		
		string = "{Jokers: "
		for card in self.jokers:
			string += str(card)+", "

		string += "}"

		for i in range(len(self.grps)):
			string += ", {group "+str(i+1)+": "
			for card in self.grps[i]:
				string += str(card)+", "
			string += "}"
		return string



if __name__ == '__main__':
	pass
else:
	logger = logging.getLogger('logger.main')
