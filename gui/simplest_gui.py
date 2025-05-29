import tkinter as tk
from envs.blackjack_env import BlackjackEnv

class BlackjackGUI:
    def __init__(self, master):
        self.master = master
        master.title("Blackjack")
        master.geometry("500x350")
        master.configure(bg='darkgreen')

        # Initialize environment
        self.env = BlackjackEnv(natural=True, num_decks=1, reshuffle_threshold=10)
        self.game_over = False

        # Dealer and player info labels
        lbl_font = ("Helvetica", 16)
        self.dealer_label = tk.Label(master, text="", font=lbl_font, bg='darkgreen', fg='white')
        self.dealer_label.pack(pady=10)
        self.player_label = tk.Label(master, text="", font=lbl_font, bg='darkgreen', fg='white')
        self.player_label.pack(pady=10)

        # Result display
        self.result_label = tk.Label(master, text="", font=("Helvetica", 20, "bold"), bg='darkgreen', fg='yellow')
        self.result_label.pack(pady=10)

        # Action buttons
        button_frame = tk.Frame(master, bg='darkgreen')
        button_frame.pack(pady=10)

        btn_font = ("Helvetica", 14)
        self.hit_button = tk.Button(button_frame, text="Hit", font=btn_font, width=10, command=self.on_hit)
        self.hit_button.pack(side=tk.LEFT, padx=10)
        self.stay_button = tk.Button(button_frame, text="Stay", font=btn_font, width=10, command=self.on_stay)
        self.stay_button.pack(side=tk.LEFT, padx=10)
        self.reset_button = tk.Button(button_frame, text="New Game", font=btn_font, width=10, command=self.reset_game)
        self.reset_button.pack(side=tk.LEFT, padx=10)

        # Start first game
        self.reset_game()

    def reset_game(self):
        obs = self.env.reset()
        self.game_over = False
        self.result_label.config(text="")
        self.hit_button.config(state=tk.NORMAL)
        self.stay_button.config(state=tk.NORMAL)
        self.update_display()
        # If initial blackjack
        if self.env._player_natural or self.env._dealer_natural:
            reward = self.env._calculate_reward()
            self.after_natural(reward)

    def update_display(self):
        # Show dealer (hide second card if game not over)
        if self.env.game_over:
            dealer_hand = self.env.dealer
            dealer_sum = self.env.sum_hand(self.env.dealer)
        else:
            dealer_hand = [self.env.dealer[0], '?']
            dealer_sum = '??'
        self.dealer_label.config(
            text=f"Dealer: {dealer_hand} (sum: {dealer_sum})"
        )
        # Show player's full hand
        player_sum = self.env.sum_hand(self.env.player)
        self.player_label.config(
            text=f"Player: {self.env.player} (sum: {player_sum})"
        )

    def on_hit(self):
        obs, reward, done, _ = self.env.step(1)
        self.update_display()
        if done:
            self.finish(reward)
        else:
            # if player hits 21 exactly
            if self.env.sum_hand(self.env.player) == 21:
                obs2, reward2, done2, _ = self.env.step(0)
                self.update_display()
                self.finish(reward2)

    def on_stay(self):
        obs, reward, done, _ = self.env.step(0)
        self.update_display()
        if done:
            self.finish(reward)

    def finish(self, reward):
        self.env.game_over = True
        if self.env._player_natural:
            text = "Blackjack! You win!"
        elif self.env._dealer_natural:
            text = "Dealer Blackjack! Push." if reward==0 else "Dealer Blackjack! You lose."
        else:
            if reward > 0:
                text = "You Win!"
            elif reward < 0:
                text = "You Lose"
            else:
                text = "Push"
        self.result_label.config(text=text)
        self.hit_button.config(state=tk.DISABLED)
        self.stay_button.config(state=tk.DISABLED)

    def after_natural(self, reward):
        # Handle naturals immediately after deal
        self.env.game_over = True
        self.update_display()
        if self.env._player_natural and not self.env._dealer_natural:
            text = "Blackjack! You win!"
        elif self.env._dealer_natural and not self.env._player_natural:
            text = "Dealer Blackjack! You lose."
        else:
            text = "Push (both Blackjack)"
        self.result_label.config(text=text)
        self.hit_button.config(state=tk.DISABLED)
        self.stay_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    gui = BlackjackGUI(root)
    root.mainloop()
