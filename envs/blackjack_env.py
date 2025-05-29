import random

class BlackjackEnv:
    """
    A simple Blackjack environment with card counting support.
    Actions: 0 = stick (stay), 1 = hit (draw a card).
    Observation/state: (player_sum, dealer_showing_card, usable_ace)
    Reward: +1 win, -1 lose, 0 draw.
    """
    def __init__(self, natural=False, num_decks=1, reshuffle_threshold=10):
        self.natural = natural  # Whether to give extra reward for natural blackjack
        self.num_decks = num_decks  # Number of decks to use (1, 2, 3, etc.)
        self.reshuffle_threshold = reshuffle_threshold  # Reshuffle when cards left <= this
        self.action_space = [0, 1]  # 0: stick, 1: hit
        
        # Initialize deck and game state
        self.deck = []
        self.cards_dealt = []  # Track all dealt cards for counting
        self.player = []
        self.dealer = []
        self.game_over = False
        
        # Initialize deck for first time
        self._init_new_deck()
        self.reset()

    def _init_new_deck(self):
        """Create and shuffle new deck(s)"""
        # Create single deck: A,2,3,4,5,6,7,8,9,10,J,Q,K (J,Q,K = 10)
        single_deck = [1,2,3,4,5,6,7,8,9,10,10,10,10] * 4
        
        # Multiply by number of decks
        self.deck = single_deck * self.num_decks
        random.shuffle(self.deck)
        
        # Reset dealt cards tracking
        self.cards_dealt = []
        
        #print(f"🔄 New deck initialized: {self.num_decks} deck(s), {len(self.deck)} cards total")

    def draw_card(self):
        """Draw a card, reshuffle if necessary"""
        # Check if we need to reshuffle
        if len(self.deck) <= self.reshuffle_threshold:
            #print(f"🔄 Reshuffling: Only {len(self.deck)} cards left (threshold: {self.reshuffle_threshold})")
            self._init_new_deck()
        
        card = self.deck.pop()
        self.cards_dealt.append(card)  # Track dealt cards
        return card

    def draw_hand(self):
        return [self.draw_card(), self.draw_card()]

    def usable_ace(self, hand):
        return (1 in hand) and (sum(hand) + 10 <= 21)

    def sum_hand(self, hand):
        total = sum(hand)
        if self.usable_ace(hand):
            return total + 10
        return total

    def is_bust(self, hand):
        return self.sum_hand(hand) > 21
    
    def is_natural(self, hand):
        return len(hand) == 2 and self.sum_hand(hand) == 21

    def score(self, hand):
        # Return final score: 0 if bust, else sum_hand
        return 0 if self.is_bust(hand) else self.sum_hand(hand)

    def reset(self):
        """Start a new game (WITHOUT reshuffling deck unless necessary)"""
        # Only clear hands, keep same deck
        self.player = self.draw_hand()
        self.dealer = self.draw_hand()
        self.game_over = False
        
        # Record if either side had a natural (but don't end game yet)
        self._player_natural = self.is_natural(self.player)
        self._dealer_natural = self.is_natural(self.dealer)
        
        return self._get_obs()  # ✅ Always returns just observation

    def step(self, action):
        # If we dealt a natural at reset, immediately terminate on first step:
        if not self.game_over and (self._player_natural or self._dealer_natural):
            self.game_over = True
            reward = self._calculate_reward()
            return self._get_obs(), reward, True, {}
        
        assert not self.game_over, "Game is already over. Call reset()."
        
        if action:  # hit
            self.player.append(self.draw_card())
            if self.is_bust(self.player):
                self.game_over = True
                return self._get_obs(), -1, True, {}
            else:
                return self._get_obs(), 0, False, {}
        else:  # stick (stay)
            # Dealer's turn
            while self.sum_hand(self.dealer) < 17:
                self.dealer.append(self.draw_card())
            
            self.game_over = True
            reward = self._calculate_reward()
            return self._get_obs(), reward, True, {}
    
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

    def _get_obs(self):
        return (self.sum_hand(self.player), self.dealer[0], self.usable_ace(self.player))

    def get_deck_info(self):
        """Get information about current deck state"""
        return {
            'cards_remaining': len(self.deck),
            'cards_dealt': len(self.cards_dealt),
            'total_cards': len(self.deck) + len(self.cards_dealt),
            'num_decks': self.num_decks,
            'reshuffle_threshold': self.reshuffle_threshold
        }

    def get_hi_lo_count(self):
        """Calculate Hi-Lo count from dealt cards"""
        count = 0
        for card in self.cards_dealt:
            if 2 <= card <= 6:
                count += 1  # Low cards
            elif card == 1 or card == 10:  # Ace or 10-value
                count -= 1  # High cards
            # 7, 8, 9 are neutral (count += 0)
        return count

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