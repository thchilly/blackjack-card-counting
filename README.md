# Blackjack Card Counting - RL Project
A simple Blackjack environment + GUI for Reinforcement Learning experiments and human play.

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










