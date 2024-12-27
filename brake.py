import time
from machine import Pin, I2C
import ssd1306
import random

# Initialize I2C for SSD1306 OLED
i2c = I2C(0, scl=Pin(21), sda=Pin(20))  # Use GPIO 22 for SCL and GPIO 21 for SDA
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Game constants
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 3
BALL_SIZE = 2
BRICK_WIDTH = 12
BRICK_HEIGHT = 5
ROWS = 5
COLS = 9

# Paddle position
paddle_x = 64 - PADDLE_WIDTH // 2
paddle_y = 60

# Ball position and movement
ball_x = 64
ball_y = 30
ball_dx = 1
ball_dy = -1

# Brick positions
bricks = []
for row in range(ROWS):
    for col in range(COLS):
        bricks.append([col * (BRICK_WIDTH + 2), row * (BRICK_HEIGHT + 2)])

# Buttons for paddle movement
left_button = Pin(2, Pin.IN, Pin.PULL_UP)  # GPIO 2 for left
right_button = Pin(13, Pin.IN, Pin.PULL_UP)  # GPIO 13 for right
restart_button = Pin(15, Pin.IN, Pin.PULL_UP) # GPIO 15 FOR restart
def draw_paddle():
    oled.fill_rect(paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT, 1)

def draw_ball():
    oled.fill_rect(ball_x, ball_y, BALL_SIZE, BALL_SIZE, 1)

def draw_bricks():
    for brick in bricks:
        oled.fill_rect(brick[0], brick[1], BRICK_WIDTH, BRICK_HEIGHT, 1)

def move_ball():
    global ball_x, ball_y, ball_dx, ball_dy, paddle_y
    ball_x += ball_dx
    ball_y += ball_dy

    # Ball collision with left and right walls
    if ball_x <= 0 or ball_x >= 128 - BALL_SIZE:
        ball_dx = -ball_dx

    # Ball collision with top wall
    if ball_y <= 0:
        ball_dy = -ball_dy

    # Ball collision with paddle
    if ball_y + BALL_SIZE >= paddle_y and paddle_x <= ball_x <= paddle_x + PADDLE_WIDTH:
        ball_dy = -ball_dy

    # Ball out of bottom
    if ball_y >= 64:
        return True  # Ball is out of bounds
    return False
def reset_game():
    global ball_x, ball_y, ball_dx, ball_dy
    ball_x = 64
    ball_y = 30
    ball_dx = 1
    ball_dy = -1
    
    
def move_paddle():
    global paddle_x
    if not left_button.value():
        if paddle_x > 0:
            paddle_x -= 2  # Move paddle left
    if not right_button.value():
        if paddle_x < 128 - PADDLE_WIDTH:
            paddle_x += 2  # Move paddle right

def check_collisions():
    global ball_dx, ball_dy, bricks
    for brick in bricks[:]:
        if brick[0] <= ball_x <= brick[0] + BRICK_WIDTH and brick[1] <= ball_y <= brick[1] + BRICK_HEIGHT:
            bricks.remove(brick)  # Remove brick
            ball_dy = -ball_dy  # Bounce ball

def game_over():
    oled.fill(0)
    oled.text("Game Over!", 30, 25)
    oled.show()
    time.sleep(0.01)
def restart_but():
    global bricks, paddle_x, paddle_y, ball_x, ball_y, ball_dx, ball_dy
    if not restart_button.value():
    # Reset game state after win
        reset_game()  # Reset ball
        reset_bricks()  # Reset bricks
        paddle_x = 64 - PADDLE_WIDTH // 2  # Reset paddle position
        paddle_y = 60  # Reset paddle position

def win_game():
    global bricks, paddle_x, paddle_y, ball_x, ball_y, ball_dx, ball_dy
    oled.fill(0)
    oled.text("You Win!", 40, 30)
    oled.show()
    time.sleep(2)
    
    # Reset game state after win
    reset_game()  # Reset ball
    reset_bricks()  # Reset bricks
    paddle_x = 64 - PADDLE_WIDTH // 2  # Reset paddle position
    paddle_y = 60  # Reset paddle position

def reset_bricks():
    global bricks
    bricks = []
    for row in range(ROWS):
        for col in range(COLS):
            bricks.append([col * (BRICK_WIDTH + 2), row * (BRICK_HEIGHT + 2)])

# Main game loop
while True:
    oled.fill(0)  # Clear the screen
    
    # Draw all game objects
    draw_paddle()
    draw_ball()
    draw_bricks()

    # Move the ball and paddle
    if move_ball():
        game_over()
        restart_but()

    move_paddle()

    # Check for ball and brick collisions
    check_collisions()

    # Check for win condition (no bricks left)
    if not bricks:
        win_game()

    # Update display
    oled.show()

    # Delay for smooth animation
    time.sleep(0.01)
