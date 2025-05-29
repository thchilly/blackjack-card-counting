import random

class BlackjackEnv:
    """
    A simple Blackjack environment with card counting support.
    Actions: 0 = stick (stay), 1 = hit (draw a card).
    Observation/state: (player_sum, dealer_showing_card, usable_ace)
    Reward: +1 win, -1 lose, 0 draw.
    """

    # Hi-Lo bin thresholds
    LO_COUNT_THRESHOLD = -5
    HI_COUNT_THRESHOLD = +5

    def __init__(self, natural=False, num_decks=1, reshuffle_threshold=10):
        self.natural = natural  # Whether to give extra reward for natural blackjack
        self.num_decks = num_decks  # Number of decks to use (1, 2, 3, etc.)
        self.reshuffle_threshold = reshuffle_threshold  # Reshuffle when cards left <= this
        self.action_space = [0, 1]  # 0: stick, 1: hit
        
        # Internal state variables
        self.deck = []
        self.cards_dealt = []  # list of (suit,label) tuples
        self.player = []
        self.dealer = []
        self.game_over = False
        
        # Build and shuffle the shoe
        self.reset()
        self._init_new_deck()

    def _init_new_deck(self):   
        """Create and shuffle new deck(s), storing full (suit,label)."""
        suits = ['clubs','diamonds','hearts','spades']
        # Use real labels so GUI can pick 2–10,J,Q,K,A images:
        labels = ['A'] + [str(i) for i in range(2,11)] + ['J','Q','K']
        # Build a single 52-card deck:
        single_deck = [(suit, lab) for suit in suits for lab in labels]

        self.deck = single_deck * self.num_decks
        random.shuffle(self.deck)
        self.cards_dealt.clear()
        
    def draw_card(self):
        """Draw a tuple (suit,label) card; reshuffle shoe if needed."""
        if len(self.deck) <= self.reshuffle_threshold:
            self._init_new_deck()
        card = self.deck.pop()         # card is now (suit, label)
        self.cards_dealt.append(card)
        return card
    
    def draw_hand(self):
        return [self.draw_card(), self.draw_card()]
    
    def _card_value(self, label: str) -> int:
        """Numeric value: '2'–'10'→2–10, 'J','Q','K'→10, 'A'→1 (or 11 handled in sum_hand)."""
        if label in ('J','Q','K','10'):
            return 10
        if label == 'A':
            return 1
        return int(label)

    def usable_ace(self, hand):
        # values = [r for (_,r) in hand]
        # return (1 in values) and (sum(values) + 10 <= 21)
        vals = [self._card_value(lab) for (_,lab) in hand]
        return (1 in vals) and (sum(vals) + 10 <= 21)

    def usable_ace(self, hand):
        vals = [self._card_value(lab) for (_,lab) in hand]
        return (1 in vals) and (sum(vals) + 10 <= 21)

    def sum_hand(self, hand):
        vals = [self._card_value(lab) for (_,lab) in hand]
        total = sum(vals)
        # Count ace as 11 if it doesn't bust
        if 1 in vals and total + 10 <= 21:
            return total + 10
        return total

    def is_bust(self, hand):
        return self.sum_hand(hand) > 21

    def is_natural(self, hand):
        return len(hand) == 2 and self.sum_hand(hand) == 21

    def score(self, hand):
        return 0 if self.is_bust(hand) else self.sum_hand(hand)

    def reset(self):
        """Deal new hands to player & dealer (no reshuffle unless threshold reached)."""
        # Note: deck persists across games until reshuffle threshold
        self.player = self.draw_hand()
        self.dealer = self.draw_hand()
        self.game_over = False

        self._player_natural = self.is_natural(self.player)
        self._dealer_natural = self.is_natural(self.dealer)

        return self._get_obs()  # Always returns just observation

    def step(self, action):
        # Immediately resolve naturals on first step
        if not self.game_over and (self._player_natural or self._dealer_natural):
            self.game_over = True
            r = self._calculate_reward()
            return self._get_obs(), r, True, {}

        assert not self.game_over, "Game over: call reset() first."

        if action == 1:  # hit
            self.player.append(self.draw_card())
            if self.is_bust(self.player):
                self.game_over = True
                return self._get_obs(), -1, True, {}
            return self._get_obs(), 0, False, {}

        else:  # stick
            while self.sum_hand(self.dealer) < 17:
                self.dealer.append(self.draw_card())
            self.game_over = True
            r = self._calculate_reward()
            return self._get_obs(), r, True, {}
    
    def _calculate_reward(self):
        player_score = self.score(self.player)
        dealer_score = self.score(self.dealer)
        player_natural = self.is_natural(self.player)
        dealer_natural = self.is_natural(self.dealer)
        
        # Handle natural blackjacks
        if player_natural and dealer_natural:
            return 0  # Draw
        elif player_natural:
            return 1.5 if self.natural else 1  # Player natural wins
        elif dealer_natural:
            return -1  # Dealer natural wins
        
        # Regular scoring
        if dealer_score > 21 or player_score > dealer_score:
            return 1
        elif player_score == dealer_score:
            return 0
        else:
            return -1

    def get_hi_lo_count(self) -> int:
        """Compute running Hi–Lo count over all dealt cards."""
        count = 0
        # for (_, label) in self.cards_dealt:
        #     val = self._card_value(label)
        #     if 2 <= val <= 6:
        #         count += 1
        #     elif 7 <= val <= 9:
        #         pass
        #     else:  # 10,J,Q,K or Ace
        #         count -= 1
        # return count

        for _ , label in self.cards_dealt:
            val = self._card_value(label)
            # 2–6 → +1, 7–9 → 0, 10/J/Q/K or A → -1
            if 2 <= val <= 6:
                count += 1
            elif val == 1 or val == 10:
                count -= 1
        return count

    def _count_bin(self, count: int) -> str:
        """Discretize the running count into 'Low','Neutral','High'."""
        if count <= self.LO_COUNT_THRESHOLD:
            return "Low"
        if count >= self.HI_COUNT_THRESHOLD:
            return "High"
        return "Neutral"


    def _get_obs(self):
        """
        Return (player_sum:int, dealer_up:int, usable_ace:bool, count_bin:str).
        Exactly the same numeric + boolean first three as before,
        with a 4th element showing the Hi–Lo bin.
        """
        ps = self.sum_hand(self.player)
        du = self._card_value(self.dealer[0][1])  # dealer upcard numeric
        ua = self.usable_ace(self.player)
        cb = self._count_bin(self.get_hi_lo_count())
        return (ps, du, ua, cb)

    def get_deck_info(self):
        """Get information about current deck state"""
        return {
            'cards_remaining': len(self.deck),
            'cards_dealt': len(self.cards_dealt),
            'total_cards': len(self.deck) + len(self.cards_dealt),
            'num_decks': self.num_decks,
            'reshuffle_threshold': self.reshuffle_threshold
        }



    def render(self):
        print(f"Player hand: {self.player} (sum: {self.sum_hand(self.player)}) {'[Usable Ace]' if self.usable_ace(self.player) else ''}")
        if self.game_over:
            print(f"Dealer hand: {self.dealer} (sum: {self.sum_hand(self.dealer)}) {'[Usable Ace]' if self.usable_ace(self.dealer) else ''}")
        else:
            print(f"Dealer showing: {self.dealer[0]} (hidden card: ?)")
        
        # Show deck info
        deck_info = self.get_deck_info()
        hi_lo = self.get_hi_lo_count()
        print(f"Deck: {deck_info['cards_remaining']} cards left | Hi-Lo Count: {hi_lo}")
        print("-" * 40)