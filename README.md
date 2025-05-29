# Blackjack Card Counting - RL Project

A comprehensive Python framework for Blackjack, combining environment simulation, model-based benchmarks, model-free learning, card-counting, and a user-friendly GUI:

- **Custom Environment**  
  A custom `BlackjackEnv` implementation: supports multiple decks, reshuffling, natural-pay rules (3:2), ace handling, and a running Hi–Lo count.

- **Model-Based Ground Truth**  
  Exact MDP solutions via Value Iteration and Policy Iteration under infinite-deck assumptions, yielding the canonical “basic strategy” hit/stand policy.

- **Model-Free Baseline**  
  Tabular Q-Learning recovers the optimal hit/stand policy from scratch, using linearly decaying learning and exploration rates.

- **Card-Counting Extension**  
  Augments the Q-Learning state with a simple Hi–Lo running count (Low/Neutral/High bins) to adapt play decisions based on shoe composition.

- **Graphical Interface**  
  A Tkinter-based GUI for human play: choose decks, view dealer upcard and remaining cards, track session stats, and play via Hit/Stay buttons.

- **Experiments & Visualization**  
  Jupyter notebook with training scripts, learning curves, win-rate comparisons, and policy heatmaps for both baseline and counting agents.

- **Full Report (PDF)**  
  Detailed write-up of methodology, experiments, and results in `report/Blackjack_Card_Counting_Phase1.pdf`.



## Project Structure

```text
blackjack/
├── agents/
│   ├── q_learning_agent.py
│   └── value_iteration.py
├── envs/
│   ├── blackjack_env.py
│   └── blackjack_env1.py
├── gui/
│   └── simple_gui.py
├── materials/
│   └── playing-cards-master/
├── notebooks/
│   └── experiments.ipynb
├── figures/
├── test_env.py
├── requirements.txt
└── README.md
```

## Installation

1. **Clone** this repo  
   ```bash
   git clone https://github.com/yourusername/blackjack.git
   cd blackjack
   ```

2. **Create and Activate** a virtual-env (optional but recommended)
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate   # Mac/Linux
     .venv\Scripts\activate      # Windows
     ```

4. **Install** dependencies
      ```bash
      pip install -r requirements.txt
      ```
      
## Smoke Test
Run a quick environment sanity check:
    ```bash
    python test_env.py
    ```

## Launch the GUI
  ```bash
  python -m gui.simple gui
  ```

* Enter number of decks (1–8).
* Use the 👊 Hit, ✋ Stay, and 🔄 New Game buttons.
* Watch session stats & remaining cards update in real time.

## Jupyter Experiments and Analysis
All RL training & evaluation code is in:
  ```bash
  notebooks/experiments.ipynb
  ```

Launch with:
  ```bash
jupyter lab notebooks/experiments.ipynb
  ```










