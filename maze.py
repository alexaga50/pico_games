import time
from machine import Pin, I2C
import ssd1306

# Initialize I2C for SSD1306 OLED
i2c = I2C(0, scl=Pin(21), sda=Pin(20))  # Use GPIO 22 for SCL and GPIO 21 for SDA
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Maze configuration (1 = wall, 0 = open path, 2 = player, 3 = exit)
maze = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Player position (start at (1, 1))
player_x, player_y = 1, 1

# Exit position (end at (8, 14))
exit_x, exit_y = 2, 8

# Button setup for movement
left_button = Pin(2, Pin.IN, Pin.PULL_UP)  # GPIO 14 for left
right_button = Pin(13, Pin.IN, Pin.PULL_UP)  # GPIO 15 for right
up_button = Pin(17, Pin.IN, Pin.PULL_UP)  # GPIO 16 for up
down_button = Pin(15, Pin.IN, Pin.PULL_UP)  # GPIO 17 for down

def reset_game():
    global player_x, player_y, exit_x, exit_y
    player_x, player_y = 1, 1
def draw_maze():
    oled.fill(0)  # Clear the screen

    # Draw the maze grid
    for y in range(10):
        for x in range(16):
            if maze[y][x] == 1:  # Wall
                oled.fill_rect(x * 8, y * 6, 8, 6, 1)
            elif maze[y][x] == 2:  # Player
                oled.fill_rect(x * 8, y * 6, 8, 6, 1)
            elif maze[y][x] == 3:  # Exit
                oled.fill_rect(x * 8, y * 6, 8, 6, 1)

    oled.show()

def move_player():
    global player_x, player_y

    if not left_button.value() and player_x > 0 and maze[player_y][player_x - 1] != 1:
        player_x -= 1
    if not right_button.value() and player_x < 15 and maze[player_y][player_x + 1] != 1:
        player_x += 1
    if not up_button.value() and player_y > 0 and maze[player_y - 1][player_x] != 1:
        player_y -= 1
    if not down_button.value() and player_y < 9 and maze[player_y + 1][player_x] != 1:
        player_y += 1

def check_win():
    if player_x == exit_x and player_y == exit_y:
        oled.fill(0)
        oled.text("You Win!", 40, 30)
        oled.show()
        time.sleep(1)
        return True
    return False

# Main game loop
while True:
    maze[player_y][player_x] = 2  # Set player position in the maze (2 is for player)
    draw_maze()  # Draw the updated maze
    maze[player_y][player_x] = 0  # Reset player position for next loop

    # Move the player based on button inputs
    move_player()

    # Check if the player reached the exit
    if check_win():
        reset_game()

    # Delay to make movement smooth
    time.sleep(0.1)
