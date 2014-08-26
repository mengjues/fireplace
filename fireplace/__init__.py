import random
from . import heroes
from .cards import Card, cardsForHero, THE_COIN

class Deck(object):
	MAX_CARDS = 30
	MAX_UNIQUE_CARDS = 2
	MAX_UNIQUE_LEGENDARIES = 1

	@classmethod
	def randomDraft(cls, hero):
		"""
		Return a deck of 30 random cards from the \a hero's collection
		"""
		deck = []
		collection = cardsForHero(hero)
		while len(deck) < cls.MAX_CARDS:
			card = random.choice(collection)
			if deck.count(card) < cls.MAX_UNIQUE_CARDS:
				# todo legendary check too
				deck.append(card)
		return Deck([Card.byId(card) for card in deck])

	def __init__(self, cards):
		self.cards = cards

	def shuffle(self):
		random.shuffle(self.cards)


class Player(object):
	MAX_HAND = 10
	MAX_MANA = 10

	def __init__(self, name, deck):
		self.name = name
		self.deck = deck
		self.hand = []
		self.field = []
		## Mana
		# total crystals
		self.manaCrystals = 0
		# additional crystals this turn
		self.additionalCrystals = 0
		# mana used this turn
		self.usedMana = 0
		# overloaded mana
		self.overload = 0
		# mana overload next turn
		self.nextOverload = 0

	@property
	def mana(self):
		return self.manaCrystals - self.usedMana - self.overload + self.additionalCrystals

	def addToHand(self, card):
		if len(self.hand) >= self.MAX_HAND:
			return
		card.owner = self # Cards are not necessarily from the deck
		self.hand.append(card)
		card.status = card.STATUS_HAND
		return card

	def draw(self, count=1):
		while count:
			card = self.deck.cards.pop()
			self.addToHand(card)
			count -= 1

	def gainMana(self, amount):
		self.manaCrystals = min(self.MAX_MANA, self.manaCrystals + amount)


class Game(object):
	def __init__(self, players):
		self.players = players
		self.turn = 0
		self.playerTurn = None

	def tossCoin(self):
		outcome = random.randint(0, 1)
		# player who wins the outcome is the index
		winner = self.players[outcome]
		# T_T
		loser = [p for p in self.players if p != winner][0]
		return winner, loser

	def start(self):
		for player in self.players:
			player.deck.shuffle()
			player.draw(3)
		self.player1, self.player2 = self.tossCoin()
		self.player2.draw()
		# TODO mulligan phase
		self.player2.addToHand(Card.byId(THE_COIN))
		self.beginTurn(self.player1)

	def beginTurn(self, player):
		self.turn += 1
		self.playerTurn = player
		player.gainMana(1)
		player.usedMana = 0
		player.overload = player.nextOverload
		player.nextOverload = 0
		player.draw()

	def endTurn(self):
		self.playerTurn.additionalCrystals = 0