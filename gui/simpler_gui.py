import tkinter as tk
from envs.blackjack_env import BlackjackEnv

CARD_WIDTH = 80
CARD_HEIGHT = 120
CARD_SPACING = 20
TOP_MARGIN = 150
PLAYER_Y = 800  # Adjust based on background height (1080-380)

class BlackjackGUI:
    def __init__(self, master):
        self.master = master
        master.title("Blackjack")
        master.resizable(False, False)
        
        # Load background image
        self.bg_photo = tk.PhotoImage(file="materials/bj_green_bg.png")
        self.canvas_width = self.bg_photo.width()
        self.canvas_height = self.bg_photo.height()
        
        # Canvas
        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_photo)

        # Stats
        self.wins = self.losses = self.ties = 0
        self.stats_text = self.canvas.create_text(
            100, self.canvas_height - 100,
            text=self._stats_text(), font=("Helvetica", 16), fill="white", anchor="w"
        )

        # Buttons (larger, bottom right)
        btn_font = ("Helvetica", 18, "bold")
        self.hit_btn = tk.Button(master, text="Hit!", font=btn_font, fg="red", command=self.on_hit)
        self.stay_btn = tk.Button(master, text="Stay", font=btn_font, fg="blue", command=self.on_stay)
        self.reset_btn = tk.Button(master, text="New Game", font=btn_font, fg="goldenrod", command=self.reset_game)
        # place buttons
        self.canvas.create_window(self.canvas_width - 100, self.canvas_height - 200, window=self.hit_btn)
        self.canvas.create_window(self.canvas_width - 100, self.canvas_height - 140, window=self.stay_btn)
        self.canvas.create_window(self.canvas_width - 100, self.canvas_height - 80, window=self.reset_btn)

        # Background for result message (hidden initially)
        self.result_bg = self.canvas.create_rectangle(0, 0, 0, 0,
                                                     fill="black", stipple="gray75", outline="",
                                                     state="hidden")
        # Result message
        self.result_text = self.canvas.create_text(
            self.canvas_width/2, self.canvas_height/2,
            text="", font=("Helvetica", 32, "bold"), fill="yellow"
        )

        # Environment
        self.env = BlackjackEnv(natural=True, num_decks=1, reshuffle_threshold=10)
        self.game_over = False
        
        self.reset_game()

    def _stats_text(self):
        total = self.wins + self.losses + self.ties
        win_pct = f"({self.wins/total:.0%})" if total else ""
        loss_pct = f"({self.losses/total:.0%})" if total else ""
        tie_pct = f"({self.ties/total:.0%})" if total else ""
        return f"Stats\nGames Won: {self.wins} {win_pct}\nGames Lost: {self.losses} {loss_pct}\nGames Tied: {self.ties} {tie_pct}"

    def reset_game(self):
        self.env.reset()
        self.game_over = False
        # hide result bg and text
        self.canvas.itemconfig(self.result_bg, state="hidden")
        self.canvas.itemconfig(self.result_text, text="")
        self.canvas.itemconfig(self.stats_text, text=self._stats_text())
        self.hit_btn.config(state=tk.NORMAL)
        self.stay_btn.config(state=tk.NORMAL)
        self.draw_hands()

    def draw_hands(self):
        # Remove old cards and sums
        self.canvas.delete("card")
        self.canvas.delete("sum")
        # Dealer hand
        dealer = self.env.dealer if self.env.game_over else [self.env.dealer[0], None]
        self._draw_cards(dealer, TOP_MARGIN)
        # Dealer sum
        if self.env.game_over:
            sum_text = f"Sum: {self.env.sum_hand(self.env.dealer)}"
        else:
            sum_text = "Sum: ?"
        self.canvas.create_text(
            self.canvas_width/2, TOP_MARGIN + CARD_HEIGHT + 30,
            text=sum_text, font=("Helvetica", 20), fill="white", tags="sum"
        )
        # Player hand
        self._draw_cards(self.env.player, PLAYER_Y)
        # Player sum
        p_sum = self.env.sum_hand(self.env.player)
        self.canvas.create_text(
            self.canvas_width/2, PLAYER_Y + CARD_HEIGHT + 30,
            text=f"Sum: {p_sum}", font=("Helvetica", 20), fill="white", tags="sum"
        )

    def _draw_cards(self, hand, y):
        total_width = len(hand) * CARD_WIDTH + (len(hand)-1) * CARD_SPACING
        start_x = (self.canvas_width - total_width) / 2
        for idx, card in enumerate(hand):
            x = start_x + idx * (CARD_WIDTH + CARD_SPACING)
            # rectangle
            self.canvas.create_rectangle(x, y, x+CARD_WIDTH, y+CARD_HEIGHT,
                                        fill="white", outline="black", tags="card")
            # face
            if card is not None:
                text = 'A' if card == 1 else str(card)
                self.canvas.create_text(x+CARD_WIDTH/2, y+CARD_HEIGHT/2,
                                        text=text, font=("Helvetica", 24), tags="card")

    def on_hit(self):
        if self.game_over: return
        _, reward, done, _ = self.env.step(1)
        self.draw_hands()
        if done: self.finish(reward)

    def on_stay(self):
        if self.game_over: return
        _, reward, done, _ = self.env.step(0)
        self.draw_hands()
        if done: self.finish(reward)

    def finish(self, reward):
        self.game_over = True
        # tally stats
        if reward > 0: self.wins += 1
        elif reward < 0: self.losses += 1
        else: self.ties += 1
        # determine message
        if self.env._player_natural:
            msg = "Blackjack! You win!"
        elif self.env._dealer_natural:
            msg = "Dealer Blackjack! " + ("Push" if reward==0 else "You lose")
        else:
            msg = "You win!" if reward>0 else "You lose" if reward<0 else "Push"
        # place background rectangle behind text
        self.canvas.itemconfig(self.result_text, text=msg)
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox(self.result_text)
        self.canvas.coords(self.result_bg, bbox)
        self.canvas.tag_lower(self.result_bg, self.result_text)
        self.canvas.itemconfig(self.result_bg, state="normal")
        # update stats
        self.canvas.itemconfig(self.stats_text, text=self._stats_text())
        self.hit_btn.config(state=tk.DISABLED)
        self.stay_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    gui = BlackjackGUI(root)
    root.mainloop()
