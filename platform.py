import time
from machine import Pin, I2C
import ssd1306
import random

# Initialize I2C for SSD1306 OLED
i2c = I2C(0, scl=Pin(21), sda=Pin(20))  # Use GPIO 22 for SCL and GPIO 21 for SDA
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Game constants
PLAYER_WIDTH = 8
PLAYER_HEIGHT = 8
PLATFORM_WIDTH = 10
BOTTOM_WIDTH = 110
PLATFORM_HEIGHT = 5
GRAVITY = 1
JUMP_STRENGTH = 7

# Player position and velocity
player_x = 64 - PLAYER_WIDTH // 2
player_y = 50
player_dx = 0
player_dy = 0
exit_x, exit_y = 100, 22

on_ground = False

# Platforms
platforms = [
    [20, 40, PLATFORM_WIDTH],  # x, y, width
    [40, 30, PLATFORM_WIDTH],
    [60, 20, PLATFORM_WIDTH],
    [80, 10, PLATFORM_WIDTH],
    [100, 30, PLATFORM_WIDTH],
    [0, 63, BOTTOM_WIDTH]
]

# Buttons for control
left_button = Pin(2, Pin.IN, Pin.PULL_UP)  # GPIO 14 for left
right_button = Pin(13, Pin.IN, Pin.PULL_UP)  # GPIO 15 for right
jump_button = Pin(15, Pin.IN, Pin.PULL_UP)  # GPIO 16 for jump

def reset_game():
    global player_x, player_y, exit_x, exit_y
    player_x, player_y = 64, 50
    
def draw_player():
    oled.fill_rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT, 1)


def draw_exit():
    oled.fill_rect(exit_x, exit_y,8,8, 1)
    
    
    
def draw_platforms():
    for platform in platforms:
        oled.fill_rect(platform[0], platform[1], platform[2], PLATFORM_HEIGHT, 1)

def move_player():
    global player_x, player_y, player_dx, player_dy, on_ground

    # Apply gravity
    if not on_ground:
        player_dy += GRAVITY  # Gravity pulls the player down

    # Move left or right
    if not left_button.value():  # Button 1: Move left
        player_dx = -2
    elif not right_button.value():  # Button 2: Move right
        player_dx = 2
    else:
        player_dx = 0

    # Jump when button is pressed (Button 3)
    if not jump_button.value() and on_ground:
        player_dy = -JUMP_STRENGTH  # Jump velocity
        on_ground = False

    # Update player position based on velocity
    player_x += player_dx
    player_y += player_dy

    # Prevent the player from going out of bounds (left and right)
    if player_x < 0:
        player_x = 0
    elif player_x > 128 - PLAYER_WIDTH:
        player_x = 128 - PLAYER_WIDTH

    # Check for collision with platforms
    on_ground = False
    for platform in platforms:
        if (player_x + PLAYER_WIDTH > platform[0] and player_x < platform[0] + platform[2] and
            player_y + PLAYER_HEIGHT <= platform[1] and player_y + PLAYER_HEIGHT + player_dy >= platform[1]):
            player_y = platform[1] - PLAYER_HEIGHT  # Place player on top of the platform
            player_dy = 0  # Stop falling
            on_ground = True
            break

    # If the player is not on the ground, keep falling
    if not on_ground:
        if player_y >= 64 - PLAYER_HEIGHT:  # If player reaches the bottom
            player_y = 80 - PLAYER_HEIGHT
            player_dy = 0
            game_over()
            reset_game()

def check_win():
    if player_x == exit_x and player_y == exit_y:
        reset_game()
        oled.fill(0)
        oled.text("You Win!", 40, 30)
        oled.show()
        time.sleep(1)
        return True
    return False
def game_over():
    oled.fill(0)
    oled.text("Game Over!", 30, 20)
    oled.show()
    time.sleep(1)

# Main game loop
while True:
    oled.fill(0)  # Clear the screen
    
    # Move player based on input and gravity
    move_player()

    # Draw player and platforms
    draw_player()
    draw_exit()
    draw_platforms()
    if check_win():
        reset_game()
    # Update display
    oled.show()

    # Delay for smooth animation
    time.sleep(0.05)
