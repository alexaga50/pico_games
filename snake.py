import machine
import ssd1306
import utime
import random

# Set up GPIO pins for input
left_pin = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
right_pin = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)

# Set up OLED screen
i2c = machine.I2C(0, sda=machine.Pin(20), scl=machine.Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Game variables
snake_size = 4
snake_pos = [(64, 32)]
snake_direction = "right"
snake_speed = 0.2  # Adjust snake speed (increase value for slower speed)
food_pos = (0, 0)
score = 0

# Button variables
LEFT = 0
RIGHT = 1
button_state = [False, False]  # Initialize button states

# Clear screen
oled.fill(0)
oled.show()

def draw_snake():
    for pos in snake_pos:
        oled.fill_rect(pos[0], pos[1], 4, 4, 1)

def generate_food():
    global food_pos

    x = random.randint(4, 124)
    y = random.randint(4, 60)
    food_pos = (x, y)
    draw_food()  # Draw the food at the new position

def draw_food():
    oled.fill_rect(food_pos[0], food_pos[1], 2, 2, 1)

def draw_score():
    if score < 10:
        oled.text(str(score), 120, 56, 1)
    else:
        oled.text(str(score), 120 - 6, 56, 1)

def update_snake():
    global snake_pos, snake_direction, score

    # Update snake position
    if snake_direction == "up":
        new_pos = (snake_pos[0][0], snake_pos[0][1] - 4)
    elif snake_direction == "down":
        new_pos = (snake_pos[0][0], snake_pos[0][1] + 4)
    elif snake_direction == "left":
        new_pos = (snake_pos[0][0] - 4, snake_pos[0][1])
    elif snake_direction == "right":
        new_pos = (snake_pos[0][0] + 4, snake_pos[0][1])

    # Check if snake hits itself
    if new_pos in snake_pos[1:]:
        reset_game()
        return

    # Check if snake hits the edge of the screen
    if new_pos[0] < 0 or new_pos[0] >= 128 or new_pos[1] < 0 or new_pos[1] >= 64:
        reset_game()
        return

    # Check if snake eats the food
    if new_pos == food_pos or (food_pos[0] in range(new_pos[0], new_pos[0] + 4) and food_pos[1] in range(new_pos[1], new_pos[1] + 4)):
        snake_pos.insert(0, new_pos)
        score += 1  # Increment the score
        generate_food()  # Generate new food position
    else:
        snake_pos.insert(0, new_pos)
        snake_pos.pop()

def reset_game():
    global snake_pos, snake_direction, score

    snake_pos = [(64, 32)]
    snake_direction = "right"
    score = 0
    generate_food()

def handle_buttons():
    global snake_direction

    # Read button states
    button_state[LEFT] = left_pin.value() == 0
    button_state[RIGHT] = right_pin.value() == 0

    # Update snake direction based on button input
    if button_state[LEFT]:
        if snake_direction == "up":
            snake_direction = "left"
        elif snake_direction == "down":
            snake_direction = "right"
        elif snake_direction == "left":
            snake_direction = "down"
        elif snake_direction == "right":
            snake_direction = "up"
    elif button_state[RIGHT]:
        if snake_direction == "up":
            snake_direction = "right"
        elif snake_direction == "down":
            snake_direction = "left"
        elif snake_direction == "left":
            snake_direction = "up"
        elif snake_direction == "right":
            snake_direction = "down"

# Generate initial food
generate_food()

# Game loop
while True:
    oled.fill(0)

    handle_buttons()
    update_snake()

    draw_snake()
    draw_food()
    draw_score()

    oled.show()
    utime.sleep(snake_speed)