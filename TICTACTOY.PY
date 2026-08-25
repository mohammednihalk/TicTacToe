from tkinter import *
import time
import pygame

# ---------------- AUDIO SETUP ---------------- #

pygame.mixer.init()

try:
    pygame.mixer.music.load("gamemusic-6082.mp3")
    pygame.mixer.music.play(-1)

    win_sound = pygame.mixer.Sound("you-win-sequence-1-183948.mp3")
    tie_sound = pygame.mixer.Sound("game-over-38511.mp3")
    click_sound = pygame.mixer.Sound("click-buttons-ui-menu-sounds-effects-button-7-203601.mp3")

except pygame.error as e:
    print("Sound Error:", e)

# ---------------- GAME DATA ---------------- #

lst = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
buttons = [['', '', ''], ['', '', ''], ['', '', '']]

PLAYER_X = 'X'
PLAYER_O = 'O'

color_X = '#0000FF'
color_O = '#FF0000'
bg_color = '#000000'
highlight_color = 'LightSeaGreen'

font_style = ("Consolas", 20, 'bold')
headline_font = ("Impact", 28, 'bold')

current_player = PLAYER_X
starting_player = PLAYER_X
ai_mode = False   # False = Local Match | True = AI Match

local_score_X = 0
local_score_O = 0

ai_score_X = 0
ai_score_O = 0

# ---------------- BUTTON GRID ---------------- #

def create_buttons():
    for r in range(3):
        for c in range(3):
            txt = lst[r][c]

            buttons[r][c] = Button(
                can1,
                width=30,
                height=4,
                text=txt,
                font=font_style,
                fg=color_X if txt == PLAYER_X else color_O if txt == PLAYER_O else 'white',
                bg=bg_color,
                command=lambda row=r, col=c: click(row, col)
            )

            buttons[r][c].grid(row=r, column=c)

# ---------------- CLICK EVENT ---------------- #

def click(row, col):
    global current_player

    if lst[row][col] != '-':
        return

    # PLAYER MOVE
    lst[row][col] = current_player
    click_sound.play()
    create_buttons()

    if check_game_over():
        return

    # ---------------- LOCAL MATCH ---------------- #
    if not ai_mode:
        current_player = PLAYER_O if current_player == PLAYER_X else PLAYER_X
        label_turn.config(text=f"{current_player} Turn",
                          fg=color_X if current_player == PLAYER_X else color_O)

    # ---------------- AI MATCH ---------------- #
    else:
        label_turn.config(text="AI Thinking...", fg=color_O)
        root.update()
        time.sleep(0.5)

        ai_move()
        create_buttons()
        check_game_over()

# ---------------- GAME CHECK ---------------- #

def check_game_over():

    win = winner(lst)

    if win:
      global local_score_X, local_score_O
      global ai_score_X, ai_score_O

      if ai_mode:
        if win == PLAYER_X:
            ai_score_X += 1
        else:
            ai_score_O += 1

        score_label.config(
            text=f"Player X: {ai_score_X}    AI O: {ai_score_O}"
        )

      else:
        if win == PLAYER_X:
            local_score_X += 1
        else:
            local_score_O += 1

        score_label.config(
            text=f"Player X: {local_score_X}    Player O: {local_score_O}"
        )

    # These happen for both Local Match and AI Match
      label_turn.config(
        text=f"{win} Wins!",
        fg=color_X if win == PLAYER_X else color_O
       )

      win_sound.play()
      highlight_winning_combination(win)

      return True

    if is_board_full():
        label_turn.config(text="It's a Tie!", fg="yellow")
        tie_sound.play()
        return True

    return False

# ---------------- WIN CHECK ---------------- #

def winner(board):

    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != '-':
            return board[i][0]

        if board[0][i] == board[1][i] == board[2][i] != '-':
            return board[0][i]

    if board[0][0] == board[1][1] == board[2][2] != '-':
        return board[0][0]

    if board[0][2] == board[1][1] == board[2][0] != '-':
        return board[0][2]

    return None

# ---------------- HIGHLIGHT WIN ---------------- #

def highlight_winning_combination(symbol):

    for i in range(3):
        if lst[i][0] == lst[i][1] == lst[i][2] == symbol:
            for j in range(3):
                buttons[i][j].config(bg=highlight_color)

        if lst[0][i] == lst[1][i] == lst[2][i] == symbol:
            for j in range(3):
                buttons[j][i].config(bg=highlight_color)

    if lst[0][0] == lst[1][1] == lst[2][2] == symbol:
        for i in range(3):
            buttons[i][i].config(bg=highlight_color)

    if lst[0][2] == lst[1][1] == lst[2][0] == symbol:
        for i in range(3):
            buttons[i][2 - i].config(bg=highlight_color)

# ---------------- RESET ---------------- #

def reset():
    global lst, current_player, starting_player

    lst = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]

    current_player = starting_player

    starting_player = PLAYER_O if starting_player == PLAYER_X else PLAYER_X

    create_buttons()

    label_turn.config(
        text=f"{current_player} Turn",
        fg=color_X if current_player == PLAYER_X else color_O
    )

    # If AI starts the round
    if ai_mode and current_player == PLAYER_O:
        label_turn.config(text="AI Thinking...", fg=color_O)
        root.update()
        time.sleep(0.5)

        ai_move()
        create_buttons()

        if check_game_over():
            return

        current_player = PLAYER_X

        label_turn.config(text="X Turn", fg=color_X)

# ---------------- MODE SWITCH ---------------- #

def local_match():
    global ai_mode

    ai_mode = False

    score_label.config(
        text=f"Player X: {local_score_X}    Player O: {local_score_O}"
    )

    reset()

def ai_match():
    global ai_mode
    ai_mode = True
    reset()

# ---------------- AI (MINIMAX) ---------------- #

def ai_move():

    best_score = -1000
    best_move = None

    for i in range(3):
        for j in range(3):

            if lst[i][j] == '-':
                lst[i][j] = PLAYER_O
                score = minimax(lst, False)
                lst[i][j] = '-'

                if score > best_score:
                    best_score = score
                    best_move = (i, j)

    if best_move:
        r, c = best_move
        lst[r][c] = PLAYER_O
        click_sound.play()

def minimax(board, is_max):

    result = winner(board)

    if result == PLAYER_O:
        return 1
    if result == PLAYER_X:
        return -1
    if is_board_full():
        return 0

    if is_max:
        best = -1000
        for i in range(3):
            for j in range(3):
                if board[i][j] == '-':
                    board[i][j] = PLAYER_O
                    score = minimax(board, False)
                    board[i][j] = '-'
                    best = max(best, score)
        return best

    else:
        best = 1000
        for i in range(3):
            for j in range(3):
                if board[i][j] == '-':
                    board[i][j] = PLAYER_X
                    score = minimax(board, True)
                    board[i][j] = '-'
                    best = min(best, score)
        return best

def is_board_full():
    for row in lst:
        if '-' in row:
            return False
    return True

# ---------------- GUI SETUP ---------------- #

root = Tk()
root.title("Advanced Tic Tac Toe")
root.config(bg=bg_color)

headline = Label(root, text="TIC TAC TOE", font=headline_font,
                 bg=bg_color, fg="white")
headline.pack(pady=10)

can1 = Canvas(root, width=300, height=300,
              bg=bg_color, highlightthickness=0)
can1.pack()

can2 = Canvas(root, width=300, height=160,
              bg=bg_color, highlightthickness=0)
can2.pack()

# ---------------- CONTROL BUTTONS ---------------- #

local_btn = Button(can2, text="Local Match",
                   width=10, height=2,
                   font=("Consolas", 12, "bold"),
                   command=local_match)

local_btn.place(x=10, y=20)

ai_btn = Button(can2, text="AI Match",
                width=10, height=2,
                font=("Consolas", 12, "bold"),
                command=ai_match)

ai_btn.place(x=190, y=20)

reset_btn = Button(can2, text="Reset",
                   width=10, height=2,
                   font=("Consolas", 12, "bold"),
                   command=reset)

reset_btn.place(x=100, y=90)

# ---------------- TURN LABEL ---------------- #

score_label = Label(root, text="Player X: 0    Player O: 0",
                    font=("Consolas", 16, "bold"),
                    bg=bg_color, fg="white")

score_label.pack(pady=5)

label_turn = Label(root, text="Player X Turn",
                   font=("Consolas", 18),
                   bg=bg_color, fg=color_X)

label_turn.pack(pady=5)

create_buttons()

root.mainloop()

pygame.mixer.music.stop()
