import time
from machine import Pin, I2C
import ssd1306
import random

# Initialize I2C for SSD1306 OLED
i2c = I2C(0, scl=Pin(21), sda=Pin(20))  # Use GPIO 22 for SCL and GPIO 21 for SDA
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Game constants
PLAYER_WIDTH = 10
PLAYER_HEIGHT = 6
BULLET_WIDTH = 2
BULLET_HEIGHT = 3
ENEMY_WIDTH = 10
ENEMY_HEIGHT = 6
NUM_ENEMIES = 4

# Player position
player_x = 64 - PLAYER_WIDTH // 2
player_y = 58

# Bullet list
bullets = []

# Enemy list
enemies = []

# Buttons for control
left_button = Pin(2, Pin.IN, Pin.PULL_UP)  # GPIO 14 for left
right_button = Pin(13, Pin.IN, Pin.PULL_UP)  # GPIO 15 for right
shoot_button = Pin(15, Pin.IN, Pin.PULL_UP)  # GPIO 16 for shoot


def reset_game():
    global player_x, player_y
    init_enemies()
    player_x = 64 - PLAYER_WIDTH // 2
    player_y = 58

# Initialize enemies
def init_enemies():
    for i in range(NUM_ENEMIES):
        enemies.append([random.randint(0, 80), 10])

def draw_player():
    oled.fill_rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT, 1)

def draw_bullets():
    for bullet in bullets:
        oled.fill_rect(bullet[0], bullet[1], BULLET_WIDTH, BULLET_HEIGHT, 1)

def draw_enemies():
    for enemy in enemies:
        oled.fill_rect(enemy[0], enemy[1], ENEMY_WIDTH, ENEMY_HEIGHT, 1)

def move_bullets():
    global bullets
    for bullet in bullets[:]:
        bullet[1] -= 2  # Move bullet upwards
        if bullet[1] < 0:  # Remove bullet if it goes off-screen
            bullets.remove(bullet)

def move_enemies():
    for enemy in enemies:
        enemy[0] += 1  # Move enemy downwards
        if enemy[0] > 100:  # Reset enemy if it goes off-screen
            enemy[0] -=1
            enemy[0] = random.randint(0,0)
            enemy[0] = random.randint(0,0)

def check_collisions():
    global bullets, enemies
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if (bullet[0] + BULLET_WIDTH > enemy[0] and bullet[0] < enemy[0] + ENEMY_WIDTH and
                bullet[1] < enemy[1] + ENEMY_HEIGHT and bullet[1] + BULLET_HEIGHT > enemy[1]):
                enemies.remove(enemy)  # Remove enemy on collision
                bullets.remove(bullet)  # Remove bullet on collision

def game_over():
    oled.fill(0)
    oled.text("Game Over!", 40, 30)
    oled.show()
    time.sleep(2)

def win_game():
    oled.fill(0)
    oled.text("You Win!", 40, 30)
    oled.show()
    time.sleep(2)

def move_player():
    global player_x
    if not left_button.value() and player_x > 0:
        player_x -= 2  # Move player left
    if not right_button.value() and player_x < 128 - PLAYER_WIDTH:
        player_x += 2  # Move player right

def shoot():
    if not shoot_button.value():
        bullets.append([player_x + PLAYER_WIDTH // 2 - BULLET_WIDTH // 2, player_y])

# Initialize enemies
init_enemies()

# Main game loop
while True:
    oled.fill(0)  # Clear the screen
    
    # Move game elements
    move_player()
    move_bullets()
    move_enemies()
    shoot()
    check_collisions()

    # Draw game elements
    draw_player()
    draw_bullets()
    draw_enemies()

    # Check for collisions with enemies (game over condition)
    for enemy in enemies:
        if enemy[1] + ENEMY_HEIGHT >= player_y:
            game_over()
            break

    # Check for win condition (no enemies left)
    if not enemies:
        win_game()
        reset_game()

    # Update display
    oled.show()

    # Delay for smooth animation
    time.sleep(0.05)
