- # Gesture Fruit Slicer - AI Hand-Controlled Fruit Ninja 🍉

  

  [Image/GIF of your game in action - You should add a screenshot or GIF here!]

  This is a virtual "Fruit Slicer" game developed using Python, OpenCV, and the `cvzone` hand tracking library.

  No mouse or touchscreen required! Just raise your hand, wave your **index finger** in the air, and slice flying fruit like a samurai. This project evolved from a simple prototype, iteratively adding features like dual game modes, special power-ups, gesture-based menus, and hidden easter eggs.

  

  ## 🎮 Core Features & Innovations

  

  - **Gesture-Based Menu**: No keyboard needed! On the menu screen, show a ✊ **Fist** to select "Infinite Mode" or a 🖐️ **Palm** for "Countdown Mode".
  - **Index Finger Slicing**: Your index fingertip 👆 is your blade.
  - **Dual Game Modes**:
    - **Infinite Mode**: Challenge your high score until you hit a bomb.
    - **Countdown Mode**: Score as much as you can in 60 seconds.
  - **🍋 Special "Freeze Lemon" FX**: Slicing a lemon triggers a 3-second "Bullet Time" effect, slowing all objects to a crawl—your perfect chance for a high-scoring combo!
  - **💣 Dodge Bombs**: Hit a bomb? Game over!
  - **Hidden Reset Easter Egg**: During the game or on the game over screen, show the **Middle Finger** 🖕 to instantly reset the game and return to the main menu.
  - ![gamescreenshot ](GestureFruitSlicer/gamescreenshot.png)

  

## 🛠️ Tech Stack



- Python 3.7+

  - opencv-python
  - cvzone
  - numpy (usually installed with OpenCV/cvzone)

  

## 🚀 Getting Started



1. **Download the Project**

   - Ensure `main.py` and all your image assets are in the same folder.

2. **Install Dependencies**

   - In your terminal or command prompt, run:

   Bash

   ```
     pip install opencv-python cvzone
   ```

3. **Prepare Assets (Crucial!)**

   - This project requires the following image files (or you must edit `main.py` to match your filenames):
     - **Fruits**: `orange.png`, `apple.png`, `pineapple.png`, `watermelon.png`, `banana.png`, `Lemon.png`, `durian.png`, `Mango.png`, `strawberry.png`
     - **Bomb**: `bomb.png`

4. **Run the Game**

   - In your terminal, run `main.py`:

   Bash

   ```
     python main.py
   ```



## ✋ Controls



| **Action**                | **Gesture / Key** | **Context**         |
| ------------------------- | ----------------- | ------------------- |
| **Slice**                 | Index Finger      | In-Game             |
| **Select Infinite Mode**  | ✊ Fist            | Main Menu           |
| **Select Countdown Mode** | 🖐️ Palm            | Main Menu           |
| **Reset Game (Gesture)**  | 🖕 Middle Finger   | In-Game / Game Over |
| **Reset Game (Keyboard)** | `r` key           | In-Game / Game Over |
| **Quit Game**             | `q` key           | Always              |



## Acknowledgements



- This project heavily utilizes the [cvzone library](https://github.com/cvzone/cvzone) for its simple and effective hand tracking module.
