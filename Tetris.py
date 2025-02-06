from machine import Pin, SPI, PWM
from sh1106 import SH1106_SPI
import time
import random

# Pins configuration for the OLED display
spi = SPI(1, baudrate=1000000)
oled = SH1106_SPI(128, 64, spi, Pin(17), Pin(16), Pin(18))
oled.sleep(False)

# Display parameters
WIDTH = 64  # Rotated width
HEIGHT = 128  # Rotated height

# Constants

SIZE = 5
MARGIN_TOP = 2
MARGIN_LEFT = 4
last_rotate_time = 50


# Buttons for paddle movement
left_button = Pin(0, Pin.IN, Pin.PULL_UP)  # GPIO 0 for left
right_button = Pin(9, Pin.IN, Pin.PULL_UP)  # GPIO 9 for right
rotate_button = Pin(15, Pin.IN, Pin.PULL_UP)  # GPIO 15 for rotate


# Grid (10x18)
grid = [[0 for _ in range(18)] for _ in range(10)]

pieces = [[[0, 0, 0, 0], [0, 1, 2, 3]], # I
          [[1, 1, 0, 2], [0, 1, 1, 0]], # Z,  
          [[0, 1, 1, 0], [1, 1, 0, 0]], # O
          [[0, 0, 0, 1], [0, 1, 2, 0]], # J
          [[0, 1, 1, 2], [1, 1, 0, 1]]] # T
   # [[0, 1], [1, 1], [1, 0], [2, 0]] ]  # Z

# Current piece (example piece)
current_piece = random.choice(pieces)
next_piece = random.choice(pieces)  # Next piece preview
current_position = [4, 0]

score = 0
game_over = False
drop_interval = 500  # Initial drop speed (milliseconds)
last_drop_time = 0
last_left_time = 0
last_right_time = 0

# Function to play a melody
def play_melody():
    for i in range(len(MELODY_NOTES)):
        speaker.freq(MELODY_NOTES[i])
        speaker.duty_u16(32768)  # 50% volume
        time.sleep_ms(MELODY_DURATIONS[i])
        speaker.duty_u16(0)
        time.sleep_ms(50)

# Function to refresh the display
def refresh():
    oled.fill(0)  # Clear the screen
    draw_grid()
    draw_piece()
    oled.show()

# Function to draw the grid
def draw_grid():
    for x in range(10):
        for y in range(18):
            if grid[x][y]:
                draw_rect_rotated(MARGIN_LEFT + (SIZE + 1) * x, MARGIN_TOP + (SIZE + 1) * y, SIZE, SIZE)
                
def new_piece():
    global current_piece, next_piece, current_position, game_over
    current_piece = next_piece
    next_piece = random.choice(pieces)
    current_position = [4, 0]
    if not can_move(0, 0):  # Check for game over
        game_over = True

# Function to draw the current piece
def draw_piece():
    for i in range(4):
        x = current_piece[0][i] + current_position[0]
        y = current_piece[1][i] + current_position[1]
        draw_rect_rotated(MARGIN_LEFT + (SIZE + 1) * x, MARGIN_TOP + (SIZE + 1) * y, SIZE, SIZE)

# Function to draw a rectangle with rotation by 90 degrees
def draw_rect_rotated(x, y, w, h):
    oled.rect(HEIGHT - y - h, x, h, w, 1)

# Function to check for and clear completed lines
def check_lines():
    for y in range(17, -1, -1):
        if all(grid[x][y] for x in range(10)):
            break_line(y)
             
            

# Function to clear a line and shift everything down
def break_line(line):
    for y in range(line, 0, -1):
        for x in range(10):
            grid[x][y] = grid[x][y - 1]
    for x in range(10):
        grid[x][0] = 0

# Function to move the piece left
def move_left():
    global current_position
    if can_move(-1, 0):
        current_position[0] -= 1

# Function to move the piece right
def move_right():
    global current_position
    if can_move(1, 0):
        current_position[0] += 1

# Function to drop the piece down
def drop_piece():
    global current_position
    if can_move(0, 1):
        current_position[1] += 1
    else:
        lock_piece()
        

# Function to check if the piece can move
def can_move(dx, dy):
    for i in range(4):
        x = current_piece[0][i] + current_position[0] + dx
        y = current_piece[1][i] + current_position[1] + dy
        if x < 0 or x >= 10 or y < 0 or y >= 18 or grid[x][y]:
            return False
    return True

# Function to lock the piece into the grid
def lock_piece():
    global current_position, current_piece
    for i in range(4):
        x = current_piece[0][i] + current_position[0]
        y = current_piece[1][i] + current_position[1]
        grid[x][y] = 1
    current_position = [4, 0]  # Reset position for the next piece

# Function to rotate the piece
def rotate_piece():
    global current_piece
    new_piece = [
        [-current_piece[1][i] for i in range(4)],
        [current_piece[0][i] for i in range(4)]
    ]
    if can_rotate(new_piece):
        current_piece = new_piece

# Function to check if rotation is possible
def can_rotate(new_piece):
    for i in range(4):
        x = new_piece[0][i] + current_position[0]
        y = new_piece[1][i] + current_position[1]
        if x < 0 or x >= 10 or y < 0 or y >= 18 or grid[x][y]:
            return False
    return True


# Μέσα στο κύριο loop:


'''while True:
    current_time = time.ticks_ms()  # Πάρε τον τρέχοντα χρόνο σε ms
    refresh()  # Ενημέρωσε την οθόνη

    # Ανιχνεύει το κουμπί περιστροφής χωρίς καθυστέρηση
    if not rotate_button.value() and current_time - last_rotate_time > 100:  # 100ms debounce
        rotate_piece()
        last_rotate_time = current_time  # Ενημέρωσε τον χρόνο περιστροφής

    # Ανιχνεύει τα υπόλοιπα κουμπιά
    if not left_button.value():
        move_left()
    if not right_button.value():
        move_right()

    drop_piece()  # Ρίξε το σχήμα προς τα κάτω
    check_lines()  # Έλεγξε για ολοκληρωμένες γραμμές

    time.sleep(0.2)  # Μικρή καθυστέρηση για ρευστότητα'''
while not game_over:
    current_time = time.ticks_ms()
    refresh()

    if not rotate_button.value() and current_time - last_rotate_time > 100:
        rotate_piece()
        last_rotate_time = current_time

    if not left_button.value() and current_time - last_left_time > 100:
        move_left()
        last_left_time = current_time

    if not right_button.value() and current_time - last_right_time > 100:
        move_right()
        last_right_time = current_time


    if current_time - last_drop_time > drop_interval:
        drop_piece()
        last_drop_time = current_time

    if not can_move(0, 1):  # Piece landed
        lock_piece()
        new_piece()
        check_lines()

    # ... (Score update and level increase logic - add this)

    time.sleep(0.01)  # Reduced delay

if game_over:
    oled.fill(0)
    oled.rotate(0)
    oled.text("Game Over!", 20, 30, 1)
    oled.show()
    while True:  # Freeze the game
      pass

