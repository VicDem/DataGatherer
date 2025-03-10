from pynput.keyboard import Listener, Key

# Counter for right arrow key presses
right_arrow_count = 0

def on_press(key):
    global right_arrow_count

    if key == Key.right:
        right_arrow_count += 1
    elif key == Key.space:
        right_arrow_count =  0  # Reset counter

    print(f"Right arrow key pressed {right_arrow_count} times", end="\r")  # Overwrites the line

# Start listening for key presses
with Listener(on_press=on_press) as listener:
    listener.join()
  