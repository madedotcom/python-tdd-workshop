from expects import expect, be_above, be_below, equal



class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __gt__(self, other):
        return self.rank > other.rank

    def __eq__(self, other):
        return  (self.rank == other.rank) \
            and (self.suit == other.suit)

class Hand:

    def __init__(self, cards):
        self.cards = sorted(cards, reverse=True)

    def __gt__(self, other):

        if self.hand_value > other.hand_value:
            return True
        if self.hand_value < other.hand_value:
            return False

        for my_card, other_card in (zip(self.cards, other.cards)):
            if my_card > other_card:
                return True
        return False

    @property
    def hand_value(self):
        return 0


class Pair(Hand):

    def __init__(self, cards):
        Hand.__init__(self, cards)

    @property
    def hand_value(self):
        return 1


class When_comparing_two_highest_card_hands:

    def given_two_hands(self):
        self.white = Hand([
            Card(2, 'Hearts')
        ])
        self.black = Hand([
            Card(5, 'Clubs')
        ])

    def the_hand_with_the_highest_card_should_win(self):
        expect(self.black).to(be_above(self.white))


class When_comparing_cards_of_differing_rank:

    def given_two_cards_of_differing_ranks(self):
        self.first_card = Card(3, 'Hearts')
        self.second_card = Card(4, 'Hearts')

    def the_cards_should_not_be_equal(self):
        expect(self.first_card).to_not(equal(self.second_card))

    def the_cards_should_order_by_their_rank(self):
        expect(self.first_card).to(be_below(self.second_card))
        expect(self.second_card).to(be_above(self.first_card))


class When_comparing_two_cards_of_the_same_rank_and_suit:

    def given_two_cards_of_the_same_rank(self):
        self.first_card = Card(5, 'Clubs')
        self.second_card = Card(5, 'Clubs')

    def the_cards_should_be_equal(self):
        expect(self.first_card).to(equal(self.second_card))


class When_comparing_two_cards_of_differing_suit:

    def given_two_cards_of_the_same_rank_but_differing_suit(self):
        self.first_card = Card(5, 'Clubs')
        self.second_card = Card(5, 'Diamonds')

    def the_two_cards_should_be_neither_greater_nor_lesser_than_each_other(self):
        expect(self.first_card).to_not(be_above(self.second_card))
        expect(self.first_card).to_not(be_below(self.second_card))

    def the_two_cards_should_not_be_equal(self):
        expect(self.first_card).to_not(equal(self.second_card))



class When_two_hands_have_the_same_highest_card:

    def given_two_hands_with_the_same_highest_value(self):
        self.white = Hand([
            Card(13, 'Clubs'),
            Card(5, 'Diamonds')
        ])

        self.black = Hand([
            Card(13, 'Diamonds'),
            Card(2, 'Spades')
        ])

    def the_hand_with_the_highest_OTHER_card_should_win(self):
        expect(self.white).to(be_above(self.black))


class When_the_cards_of_a_hand_are_out_of_order:

    def given_two_hands(self):
        self.white = Hand([
            Card(13, 'Hearts'),
            Card(2, 'Hearts'),
            Card(5, 'Clubs')
        ])
        self.black = Hand([
            Card(2, 'Hearts'),
            Card(7, 'Diamonds'),
            Card(13, 'Spades')
        ])


    def the_hand_with_the_highest_other_card_should_win(self):
        expect(self.black).to(be_above(self.white))
        expect(self.black).to_not(be_below(self.white))


class When_comparing_a_pair_with_a_non_pair:

    def given_a_pair_and_a_non_pair(self):
        self.white = Pair([
            Card(2, 'Hearts'),
            Card(2, 'Diamonds'),
            Card(13, 'Spades')
        ])

        self.black = Hand([
            Card(13, 'Clubs'),
            Card(12, 'Diamonds'),
            Card(10, 'Hearts')
        ])

    def the_pair_should_be_higher_then_the_non_pair(self):
        expect(self.white).to(be_above(self.black))

    def the_non_pair_should_not_be_higher_than_the_pair(self):
        expect(self.black).to_not(be_above(self.white))




