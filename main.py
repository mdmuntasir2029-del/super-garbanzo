"""
PS4 Controller -> Arduino Fan Lock System  (with audio feedback)
----------------------------------------------------------------
Sends single characters over serial to match the Arduino sketch:

    'X','S','T','C'  -> password characters (face buttons)
    'E'              -> ENTER / submit password (Options button)
    'F'              -> relock the system        (R1 button)

Audio feedback uses winsound (built into Python on Windows -- NOTHING to install).
Tones are triggered by the Arduino's own replies, so they reflect real state:
    AuthComplete  -> rising "granted" tone
    AuthDenied    -> low "denied" buzz
    LOCKED        -> descending "lock" tone
Each button press also plays a short blip.

Requires (already installed):
    pip install pygame-ce pyserial
    (winsound needs no installation; it ships with Python on Windows.)

Usage:
    1. Set SERIAL_PORT below to your Arduino's port.
    2. Run once with DEBUG = True to confirm your button numbers.
    3. Set DEBUG = False and play.
"""

import sys
import time
import serial
import pygame

# winsound is Windows-only and part of the standard library.
# Guard the import so the script still runs (silently) on other OSes.
try:
    import winsound
    AUDIO = True
except ImportError:
    AUDIO = False

# ----------------- CONFIG -----------------
SERIAL_PORT = "COM5"      # Windows: "COM3"  |  check the Arduino IDE for yours
BAUD_RATE   = 9600
DEBUG       = False      # True = print button indices instead of sending
SOUND       = True         # set False to mute all audio feedback

# PS4 face-button -> character map (pygame button indices).
# Run with DEBUG = True to confirm, then edit the numbers if needed.
BUTTON_MAP = {
    0: 'X',   # Cross    -> password char X
    2: 'S',   # Square   -> password char S
    3: 'T',   # Triangle -> password char T
    1: 'C',   # Circle   -> password char C
    9: 'E',   # L1  -> ENTER
    10: 'F',   # R1       -> RELOCK
}

BUTTON_NAMES = {
    0: "Cross",  3: "Triangle",  2: "Square",  1: "Circle",
    9: "L1", 10: "R1",
}
# ------------------------------------------


def beep(freq, dur_ms):
    """Play a single tone if audio is available and enabled."""
    if AUDIO and SOUND:
        try:
            winsound.Beep(int(freq), int(dur_ms))
        except RuntimeError:
            pass  # some systems reject odd freq/duration; ignore quietly


def tone_press():
    """Short blip when a button is sent."""
    beep(1200, 40)


def tone_granted():
    """Rising two-note tone for access granted."""
    beep(880, 120)
    beep(1320, 160)


def tone_denied():
    """Low buzz for access denied."""
    beep(300, 250)
    beep(220, 250)


def tone_locked():
    """Descending tone for relock."""
    beep(900, 120)
    beep(500, 180)


def connect_serial():
    """Open the serial port, retrying briefly so a not-yet-ready Arduino isn't fatal."""
    for attempt in range(5):
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
            time.sleep(2)  # let the Arduino finish its auto-reset on connect
            print(f"Connected to Arduino on {SERIAL_PORT}")
            return ser
        except serial.SerialException as e:
            print(f"Serial connect failed ({e}); retry {attempt + 1}/5...")
            time.sleep(1)
    print("Could not open the serial port. Check SERIAL_PORT and that the Arduino is plugged in.")
    sys.exit(1)


def init_controller():
    """Initialise pygame and grab the first connected controller."""
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No controller detected. Pair/connect your PS4 controller and try again.")
        sys.exit(1)

    js = pygame.joystick.Joystick(0)
    js.init()
    print(f"Controller: {js.get_name()}  ({js.get_numbuttons()} buttons)")
    return js


def read_serial_feedback(ser):
    """Print any text the Arduino sends back and play a matching tone."""
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode(errors="ignore").strip()
            if line:
                print(f"  Arduino: {line}")
                # Trigger audio based on the actual reply text.
                if "AuthComplete" in line:
                    tone_granted()
                elif "AuthDenied" in line:
                    tone_denied()
                elif "LOCKED" in line:
                    tone_locked()
    except (serial.SerialException, OSError):
        pass


def main():
    if not AUDIO:
        print("Note: winsound not available (non-Windows) -- running without audio.")

    ser = None if DEBUG else connect_serial()
    js = init_controller()

    if DEBUG:
        print("\nDEBUG MODE: press each button to see its index. Ctrl+C to quit.\n")
    else:
        print("\nReady. Press buttons to send. Ctrl+C to quit.")
        print("Mapping:")
        for idx, ch in BUTTON_MAP.items():
            print(f"  {BUTTON_NAMES.get(idx, f'button {idx}'):8} -> '{ch}'")
        print()

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    btn = event.button

                    if DEBUG:
                        print(f"Button index: {btn}")
                        continue

                    ch = BUTTON_MAP.get(btn)
                    if ch is not None:
                        ser.write(ch.encode())
                        name = BUTTON_NAMES.get(btn, f"button {btn}")
                        print(f"{name} -> sent '{ch}'")
                        tone_press()

                elif event.type == pygame.JOYDEVICEREMOVED:
                    print("Controller disconnected.")
                    return

            if not DEBUG:
                read_serial_feedback(ser)

            time.sleep(0.01)  # keep CPU usage low

    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        if ser is not None and ser.is_open:
            ser.close()
        pygame.quit()


if __name__ == "__main__":
    main()