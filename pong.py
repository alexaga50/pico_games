import machine
import ssd1306
import utime
import random
import math

# Set up GPIO pins for input
up_pin = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
down_pin = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)

# Set up OLED screen
i2c = machine.I2C(0, sda=machine.Pin(20), scl=machine.Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Game variables
paddle_height = 14
paddle_width = 2
paddle_speed = 3
paddle_y = (64 - paddle_height) // 2
ball_radius = 2
ball_speed_x = 2
ball_speed_y = 1
ball_pos_x = 64
ball_pos_y = 32
player_score = 0
computer_score = 0
score_display_duration = 2  # Duration to display scores after reset (in seconds)

# Court variables
court_color = 1  # Court color (1 for white)
border_width = 2
court_line_width = 2
court_top = border_width
court_bottom = 64 - border_width

# Clear screen
oled.fill(0)
oled.show()

def draw_court():
    # Draw top border
    oled.fill_rect(0, 0, 128, border_width, court_color)
    # Draw bottom border
    oled.fill_rect(0, 64 - border_width, 128, border_width, court_color)
    # Draw middle line
    oled.fill_rect(64 - court_line_width // 2, 0, court_line_width, 64, court_color)

def draw_paddle(x, y):
    oled.fill_rect(x, y, paddle_width, paddle_height, 1)

def draw_player_paddle():
    oled.fill_rect(0, paddle_y, paddle_width, paddle_height, 1)

def update_player_paddle_position():
    global paddle_y

    if up_pin.value() == 0 and paddle_y > court_top:
        paddle_y -= paddle_speed
    if down_pin.value() == 0 and paddle_y < court_bottom - paddle_height:
        paddle_y += paddle_speed

def update_computer_paddle_position():
    global computer_paddle_y

    # Adjust the delay here (increase the value for a slower AI)
    delay = 4

    if computer_paddle_y < ball_pos_y - paddle_height // 2 and utime.ticks_ms() % delay == 0:
        computer_paddle_y += paddle_speed
    elif computer_paddle_y > ball_pos_y - paddle_height // 2 and utime.ticks_ms() % delay == 0:
        computer_paddle_y -= paddle_speed

def draw_ball():
    oled.fill_rect(int(ball_pos_x) - ball_radius, int(ball_pos_y) - ball_radius, int(ball_radius * 2), int(ball_radius * 2), 1)

def update_ball_position():
    global ball_pos_x, ball_pos_y, ball_speed_x, ball_speed_y, player_score, computer_score

    # Erase previous ball position
    oled.fill_rect(int(ball_pos_x) - ball_radius, int(ball_pos_y) - ball_radius, int(ball_radius * 2), int(ball_radius * 2), 0)

    # Update ball position
    ball_pos_x += ball_speed_x
    ball_pos_y += ball_speed_y

    # Convert ball position to integers
    ball_pos_x = int(ball_pos_x)
    ball_pos_y = int(ball_pos_y)

    # Check ball collision with paddles
    if ball_pos_x - ball_radius <= paddle_width and paddle_y <= ball_pos_y <= paddle_y + paddle_height:
        if ball_speed_x < 0:
            ball_speed_x = abs(ball_speed_x)  # Reverse x direction
        ball_speed_y += random.uniform(-2, 2)  # Random angle adjustment

    elif ball_pos_x + ball_radius >= 128 - paddle_width and computer_paddle_y <= ball_pos_y <= computer_paddle_y + paddle_height:
        if ball_speed_x > 0:
            ball_speed_x = -abs(ball_speed_x)  # Reverse x direction
        ball_speed_y += random.uniform(-2, 2)  # Random angle adjustment

    # Check ball collision with top and bottom borders
    if ball_pos_y - ball_radius <= court_top:
        ball_speed_y = abs(ball_speed_y)  # Reverse y direction
        ball_pos_y = court_top + ball_radius
    elif ball_pos_y + ball_radius >= court_bottom:
        ball_speed_y = -abs(ball_speed_y)  # Reverse y direction
        ball_pos_y = court_bottom - ball_radius

    # Check ball scoring
    if ball_pos_x - ball_radius <= 0:
        computer_score += 1
        reset_game(computer_serves=True)
    elif ball_pos_x + ball_radius >= 128:
        player_score += 1
        reset_game(computer_serves=False)

    # Draw ball at new position
    draw_ball()

def reset_game(computer_serves):
    global ball_pos_x, ball_pos_y, ball_speed_x, ball_speed_y

    ball_pos_x = 64
    ball_pos_y = 32
    ball_speed_x = abs(ball_speed_x) if computer_serves else -abs(ball_speed_x)
    ball_speed_y = random.uniform(-2, 2)  # Randomize the ball's vertical speed

    # Display scores for a short duration
    oled.fill(0)
    oled.text("Player: " + str(player_score), 38, 25, 1)
    oled.text("Computer: " + str(computer_score), 25, 35, 1)
    oled.show()
    utime.sleep(score_display_duration)

# Initial paddle positions
player_paddle_y = (64 - paddle_height) // 2
computer_paddle_y = (64 - paddle_height) // 2

# Draw initial court, paddles, and scores
draw_court()
draw_paddle(0, paddle_y)
draw_paddle(128 - paddle_width, computer_paddle_y)
oled.text("Player: " + str(player_score), 0, 0, 1)
oled.text("Computer: " + str(computer_score), 0, 10, 1)
oled.show()

# Game loop
while True:
    oled.fill(0)

    update_player_paddle_position()
    update_computer_paddle_position()
    draw_court()  # Draw court
    oled.fill_rect(0, 0, paddle_width, 64, 0)  # Clear player paddle
    oled.fill_rect(128 - paddle_width, 0, paddle_width, 64, 0)  # Clear computer paddle
    draw_player_paddle()  # Draw player paddle
    draw_paddle(128 - paddle_width, computer_paddle_y)  # Draw computer paddle
    update_ball_position()
    oled.show()
    utime.sleep(0.01)