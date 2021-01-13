from screeninfo import get_monitors

# Get the screen size (Jack's edit)
screen_width, screen_height = None, None
for m in get_monitors():
    screen_width = m.width
    screen_height = m.height
scale = 6.5 if screen_width > 1900 else 12.5
print(str(screen_width) + "," + str(screen_height))