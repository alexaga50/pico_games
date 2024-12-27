import machine
import ssd1306
import utime
import urandom

# Set up GPIO pins for input
button_pin = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)

# Set up OLED screen
i2c = machine.I2C(0, sda=machine.Pin(20), scl=machine.Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Game variables
bird_pos = [32, 32]
bird_velocity = 0
gravity = 0.3
jump_strength = -3
game_over = False
score = 0

# Pipe variables
pipe_width = 10
pipe_height = 40
pipe_gap = 20
pipe_distance = 60
pipe_speed = 2
pipe_pos = [128, 0]
pipe_passed = False

# Button variables
button_state = False

# Clear screen
oled.fill(0)
oled.show()

def draw_bird():
    oled.fill_rect(bird_pos[0], bird_pos[1], 4, 4, 1)

def draw_pipe():
    oled.fill_rect(pipe_pos[0], 0, pipe_width, pipe_pos[1], 1)
    oled.fill_rect(pipe_pos[0], pipe_pos[1] + pipe_gap, pipe_width, oled.height - (pipe_pos[1] + pipe_gap), 1)

def update_bird():
    global bird_pos, bird_velocity, game_over

    bird_velocity += gravity
    bird_pos[1] += int(bird_velocity)

    if bird_pos[1] < 0:
        bird_pos[1] = 0
        bird_velocity = 0

    if bird_pos[1] > oled.height - 4:
        bird_pos[1] = oled.height - 4
        game_over = True
        reset_game()  # Call reset_game() function when the bird touches the ground

def update_pipe():
    global pipe_pos, pipe_passed, score

    pipe_pos[0] -= pipe_speed

    if pipe_pos[0] < -pipe_width:
        pipe_pos[0] = oled.width
        pipe_pos[1] = urandom.randint(8, oled.height - pipe_gap - 8)
        pipe_passed = False
        score += 1

def handle_buttons():
    global button_state

    button_state = button_pin.value() == 0

def check_collision():
    if bird_pos[0] + 4 > pipe_pos[0] and bird_pos[0] < pipe_pos[0] + pipe_width:
        if bird_pos[1] < pipe_pos[1] or bird_pos[1] + 4 > pipe_pos[1] + pipe_gap:
            return True
    if bird_pos[1] < 0 or bird_pos[1] + 4 > oled.height:
        return True
    return False

def reset_game():
    global bird_pos, bird_velocity, game_over, score, pipe_pos, pipe_passed

    bird_pos = [32, 32]
    bird_velocity = 0
    game_over = False
    score = 0
    pipe_pos = [oled.width, 0]
    pipe_passed = False

# Game loop
while True:
    oled.fill(0)

    handle_buttons()

    if button_state:
        bird_velocity = jump_strength

    update_bird()
    update_pipe()

    if check_collision():
        reset_game()

    draw_pipe()
    draw_bird()

    # Display score in bottom right corner
    score_text = str(score) + " "
    score_x = oled.width - len(score_text) * 6
    score_y = oled.height - 8
    oled.text(score_text, score_x, score_y)

    oled.show()
    utime.sleep(0.01)