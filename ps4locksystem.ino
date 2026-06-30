#include <LiquidCrystal.h>
#include <string.h>

// ---------------- LCD ----------------
LiquidCrystal lcd(12, 11, 2, 3, 4, 5);

// ---------------- PINS ----------------
const int fanPin = 9;

// ---------------- PASSWORD SYSTEM ----------------
char password[4] = {'X','S','T','C'};
char input[4];
int indexPos = 0;

bool unlocked = false;

// ---------------- SCROLL CONTROL ----------------
const char* lockedMsg   = "FAN LOCKED, ENTER PASSWORD    ";
const char* unlockedMsg = "FAN UNLOCKED, Press R1 to Relock.    ";

int pos = 0;
unsigned long lastMove = 0;
const int scrollSpeed = 400;

void setup() {

  Serial.begin(9600);

  pinMode(fanPin, OUTPUT);
  digitalWrite(fanPin, LOW);

  lcd.begin(16, 2);

  lcd.clear();
  lcd.print("BOOTING...");
  delay(1500);

  lcd.clear();
  lcd.print("ENTER PASSWORD");
}

void loop() {

  // ---------------- SERIAL INPUT (PS4 VIA PYTHON / KEYBOARD) ----------------
  if (Serial.available() > 0) {

    char c = Serial.read();

    // ======== KEYBOARD RELOCK COMMAND ========
    if (c == 'F') {
      unlocked = false;                 // Lock the system
      digitalWrite(fanPin, LOW);        // Instantly force fan off
      indexPos = 0;                     // Reset password character position
      memset(input, 0, sizeof(input));  // Clear the password input buffer
      pos = 0;                          // Reset text scroll position

      lcd.clear();
      lcd.print("SYSTEM LOCKED");
      Serial.println("LOCKED");         // Feedback to Python terminal
      delay(1500);

      lcd.clear();
      lcd.print("ENTER PASSWORD");
      return;                           // Skip processing anything else for this check
    }

    // -------- PASSWORD INPUT --------
    // Only accept password characters if the system isn't already unlocked
    if (!unlocked && (c == 'X' || c == 'S' || c == 'T' || c == 'C')) {

      if (indexPos < 4) {
        input[indexPos] = c;

        lcd.setCursor(indexPos, 1);
        lcd.print("*");

        indexPos++;
      }
    }

    // -------- ENTER PASSWORD --------
    if (!unlocked && c == 'E') {

      bool correct = true;

      // Ensure they have actually typed 4 characters first
      if (indexPos < 4) {
        correct = false;
      } else {
        for (int i = 0; i < 4; i++) {
          if (input[i] != password[i]) {
            correct = false;
          }
        }
      }

      lcd.clear();

      if (correct) {
        unlocked = true;
        lcd.print("ACCESS GRANTED");
        Serial.println("AuthComplete:NilErrors");
      }
      else {
        unlocked = false;
        lcd.print("ACCESS DENIED");
        Serial.println("AuthDenied:WrongPass");
      }

      delay(1500);

      indexPos = 0;
      memset(input, 0, sizeof(input));  // Safely wipe old input
      pos = 0;                          // Clean scroll start
      lcd.clear();
      lcd.print("ENTER PASSWORD");
    }
  }

  // ---------------- FAN CONTROL ----------------
  if (unlocked) {
    digitalWrite(fanPin, HIGH);
  } else {
    digitalWrite(fanPin, LOW);
  }

  // ---------------- LCD SCROLL (NON-BLOCKING, WRAPAROUND) ----------------
  if (millis() - lastMove >= scrollSpeed) {
    lastMove = millis();

    const char* msg = unlocked ? unlockedMsg : lockedMsg;
    int len = strlen(msg);

    // Always build a full 16-char window so every column gets overwritten.
    char window[17];
    for (int i = 0; i < 16; i++) {
      window[i] = msg[(pos + i) % len];
    }
    window[16] = '\0';

    lcd.setCursor(0, 0);
    lcd.print(window);

    pos++;
    if (pos >= len) pos = 0;
  }

  delay(10);
}