import tkinter as tk
from tkinter import simpledialog
import os
from envs.blackjack_env1 import BlackjackEnv

# Constants
CARD_WIDTH = 121      # half of original 242
CARD_HEIGHT = 170     # half of original 340
CARD_SPACING = 20
TOP_MARGIN = 150
PLAYER_Y = 800  # vertical offset for player's cards

# Paths
CARDS_DIR = "materials/playing-cards-master"

class BlackjackGUI:
    def __init__(self, master):
        self.master = master
        master.title("Blackjack")
        master.resizable(False, False)

        # Ask user how many decks
        num_decks = simpledialog.askinteger("Decks", "How many decks to use?", initialvalue=1, minvalue=1, maxvalue=8)
        if num_decks is None:
            num_decks = 1

        # Load background
        self.bg_photo = tk.PhotoImage(file="materials/bj_green_bg.png")
        self.canvas_width = self.bg_photo.width()
        self.canvas_height = self.bg_photo.height()
        
        # Preload card images and scale down 50%
        self.card_images = {}
        for fname in os.listdir(CARDS_DIR):
            if fname.endswith('.png') and '_' in fname:
                key = fname.replace('.png','')  # e.g. 'clubs_2'
                path = os.path.join(CARDS_DIR, fname)
                img = tk.PhotoImage(file=path)
                img = img.subsample(2, 2)  # reduce size by 50%
                self.card_images[key] = img
        # Back images
        self.back_dark = tk.PhotoImage(file=os.path.join(CARDS_DIR,'back_dark2.png')).subsample(2,2)
        self.back_light = tk.PhotoImage(file=os.path.join(CARDS_DIR,'back_light.png')).subsample(2,2)

        # Canvas
        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_photo)

        # Remaining cards display
        self.rem_text = self.canvas.create_text(
            self.canvas_width-150, 50,
            text="", font=("Helvetica", 18, "bold"), fill="white"
        )

        # Deck count display (above remaining cards)
        self.deck_text = self.canvas.create_text(
            self.canvas_width-150, 20,
            text=f"Decks: {num_decks}", font=("Helvetica", 18), fill="lightgray"
        )

        # Stats
        self.wins = self.losses = self.ties = 0
        self.stats_text = self.canvas.create_text(
            100, self.canvas_height - 100,
            text=self._stats_text(), font=("Helvetica", 16), fill="white", anchor="w"
        )

        # Buttons
        btn_font = ("Helvetica", 18, "bold")
        self.hit_btn = tk.Button(master, text="👊 Hit!", font=btn_font, fg="red", command=self.on_hit)
        self.stay_btn = tk.Button(master, text="✋ Stay.", font=btn_font, fg="blue", command=self.on_stay)
        self.reset_btn = tk.Button(master, text="🔄 New Game", font=btn_font, fg="goldenrod", command=self.reset_game)
        self.canvas.create_window(self.canvas_width - 100, self.canvas_height - 200, window=self.hit_btn)
        self.canvas.create_window(self.canvas_width - 100, self.canvas_height - 140, window=self.stay_btn)
        self.canvas.create_window(self.canvas_width - 100, self.canvas_height - 80, window=self.reset_btn)

        # Result backdrop & text
        self.result_bg = self.canvas.create_rectangle(0,0,0,0, fill="black", stipple="gray50", state="hidden")
        self.result_text = self.canvas.create_text(
            self.canvas_width/2, self.canvas_height/2,
            text="", font=("Helvetica", 50, "bold"), fill="yellow"
        )

        # Environment
        self.env = BlackjackEnv(natural=True, num_decks=num_decks, reshuffle_threshold=10)
        #self.env._init_new_deck()
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
        self.canvas.itemconfig(self.result_bg, state="hidden")
        self.canvas.itemconfig(self.result_text, text="")
        self.canvas.itemconfig(self.stats_text, text=self._stats_text())
        self.hit_btn.config(state=tk.NORMAL)
        self.stay_btn.config(state=tk.NORMAL)
        self.draw_hands()

    def draw_hands(self):
        # Clear old
        self.canvas.delete("card")
        self.canvas.delete("sum")
        
        # Update deck info and remaining cards
        rc = len(self.env.deck)
        self.canvas.itemconfig(self.rem_text, text=f"Cards left: {rc}")
        self.canvas.itemconfig(self.deck_text, text=f"Decks: {self.env.num_decks}")

        # Dealer
        dealer = self.env.dealer if self.env.game_over else [self.env.dealer[0], None]
        self._draw_cards(dealer, TOP_MARGIN)
        # Dealer sum
        dsum = self.env.sum_hand(self.env.dealer) if self.env.game_over else '??'
        self.canvas.create_text(self.canvas_width/2, TOP_MARGIN + CARD_HEIGHT + 30,
                                text=f"Sum: {dsum}", font=("Helvetica",20), fill="white", tags="sum")
        # Player
        self._draw_cards(self.env.player, PLAYER_Y)
        psum = self.env.sum_hand(self.env.player)
        self.canvas.create_text(self.canvas_width/2, PLAYER_Y + CARD_HEIGHT + 30,
                                text=f"Sum: {psum}", font=("Helvetica",20), fill="white", tags="sum")
    def _draw_cards(self, hand, y):
        n = len(hand)
        total_w = n*CARD_WIDTH + (n-1)*CARD_SPACING
        start_x = (self.canvas_width - total_w) / 2
        for i, card in enumerate(hand):
            x = start_x + i*(CARD_WIDTH + CARD_SPACING)
            if card is None:
                img = self.back_dark
            else:
                suit, label = card
                key = f"{suit}_{label}"   # e.g. 'hearts_Q', 'spades_J'
                img = self.card_images[key]
            self.canvas.create_image(x + CARD_WIDTH/2, y + CARD_HEIGHT/2, image=img, tags="card")

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
        if reward > 0: self.wins += 1
        elif reward < 0: self.losses += 1
        else: self.ties += 1
        # message
        if self.env._player_natural:
            msg = "Blackjack! You win!"
        elif self.env._dealer_natural:
            msg = "Dealer Blackjack! Push" if reward==0 else "Dealer Blackjack! You lose :("
        else:
            msg = "You win!" if reward>0 else "You lose :(" if reward<0 else "Push"
        self.canvas.itemconfig(self.result_text, text=msg)
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox(self.result_text)
        self.canvas.coords(self.result_bg, bbox)
        self.canvas.tag_lower(self.result_bg, self.result_text)
        self.canvas.itemconfig(self.result_bg, state="normal")
        self.canvas.itemconfig(self.stats_text, text=self._stats_text())
        self.hit_btn.config(state=tk.DISABLED)
        self.stay_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    gui = BlackjackGUI(root)
    root.mainloop()
