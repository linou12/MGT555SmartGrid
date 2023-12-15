#include <FastLED.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#define SCREEN_WIDTH 128// OLED display width, in pixels
#define SCREEN_HEIGHT 40 // OLED display height, in pixels
#define NUM_LEDS 105
#define LED_PIN 4
#define LED_PIN_POS_V 11 
#define LED_PIN_NEG_V 12 // Define the pin connected to the WS2812B LEDs

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

CRGB leds[NUM_LEDS];
CRGB pulseColor = CRGB(0,0,255); // Stores last time LED was updated
const long interval = 1000;       // Interval at which to blink (milliseconds)
bool ledState = false;            // LED state used to set the LED
bool isBlinking = false;          // Flag to check if blinking is active


// Defining constraints
const int t = 50;
const int a = 0;
const int b = 13;
const int c = 14;
const int d = 31;
const int e = 32;
const int f = 55;
const int g = 56;
const int h = 66;
const int z = 67;
const int j = 76;
const int k = 77;
const int l = 102;
// anodes
int row[] = {5,6,7};
// cathodes
int col[] = {8,9,10};

// bit patterns for each row
byte data[] = {
  0,0,0};

// defines the size of the matrix 
int columns = 3;
int rows = 3;

//millisecond delay between displaying each row
int pause = 1;

struct Animation {
    int start, end, step;
    unsigned long lastUpdate;
    int currentIndex;
    bool active;
} animations[8];

void setup() {
    FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
    Serial.begin(9600); // Start serial communication
    for (int i=0;i<3;i++)
  {
    pinMode(row[i], OUTPUT);
    pinMode(col[i], OUTPUT);
  } 
  allOff();
    // Initialize animations
    for (int i = 0; i < 8; ++i) {
        animations[i].lastUpdate = 0;
        animations[i].currentIndex = -1;
        animations[i].active = false;
    }
    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3D for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    }
    else{
      display.clearDisplay();
      updateDisplay(0);
      // Display for 2 seconds
      display.clearDisplay();}
      pinMode(LED_PIN_POS_V, OUTPUT);
      pinMode(LED_PIN_NEG_V, OUTPUT);

}

void updateDisplay(int value) {
  display.clearDisplay();
  display.setTextSize(3);
  display.setTextColor(WHITE);
  display.setCursor(30, 20);
  // Calculate percentage based on input value
  // Display dynamic text
  display.print(value);
  display.println("%");
  display.display();
}

void updateAnimation(Animation &anim, CRGB color) {
    if (millis() - anim.lastUpdate > t) {
        anim.lastUpdate = millis();

        if (anim.currentIndex == -1) {
            // Initialize the starting index based on the step direction
            anim.currentIndex = (anim.step > 0) ? anim.start -1 : anim.end +1; // Adjust for reverse direction
        } else {
            // Clear the previous LED
            leds[anim.currentIndex] = CRGB::Black;
            // Move to the next index
            anim.currentIndex += anim.step;
        }

        // Check if the current index is within bounds
        if ((anim.step > 0 && anim.currentIndex <= anim.end) || (anim.step < 0 && anim.currentIndex >= anim.start)) {
            leds[anim.currentIndex] = color;
        } else {
            // Out of bounds, reset animation
            anim.currentIndex = -1;
            anim.active = false;
            return;
        }

        FastLED.show();
    }
}

void loop() {
    
    // CRGB pulseColor = CRGB(255, 255, 0);
    if (Serial.available() > 0) {
        char command = Serial.read();
        switch (command) {
            case 'a': animations[0] = {k, l + 1 , -1, 0, l + 1, true}; break;
            case 'b': animations[1] = {z -1, j , 1, 0, z -1, true}; break;
            case 'c': animations[2] = {g -1, h, 1, 0, g -1, true}; break;
            case 'd': animations[3] = {g , h +1, -1, 0, h +1, true}; break;
            case 'e': animations[4] = {a , b, 1, 0, a , true}; break;
            case 'f': animations[5] = {c -1, d  , 1, 0, c -1, true}; break;
            case 'h': animations[6] = {e , f +1, -1, 0, f +1, true}; break;
            case 'A': updateDisplay(0); break;
            case 'B': updateDisplay(10); break;
            case 'C': updateDisplay(20); break;
            case 'D': updateDisplay(30); break;
            case 'E': updateDisplay(40); break;
            case 'F': updateDisplay(50); break;
            case 'G': updateDisplay(60); break;
            case 'H': updateDisplay(70); break;
            case 'I': updateDisplay(80); break;
            case 'J': updateDisplay(90); break;
            case 'K': updateDisplay(100); break;
            case 'L' : pulseColor = CRGB(0,0,255);break;
            case 'M': pulseColor = CRGB(255, 255, 0);break;
            case 'N': blinkLED(); break;
            case 'O' : offLED();break;
            case 'g':
            data[0] = B00000000;
            data[1] = B00000000;
            data[2] = B00000000;
            break;

            case 'i':
            data[0] = B00000000;
            data[1] = B00000000;
            data[2] = B00000100;
            break;

            case 'j':
            data[0] = B00000000;
            data[1] = B00000000;
            data[2] = B00000110;
            break;

            case 'k':
            data[0] = B00000000;
            data[1] = B00000000;
            data[2] = B00000111;
            break;

            case 'l':
            data[0] = B00000000;
            data[1] = B00000100;
            data[2] = B00000111;
            break;

            case 'm':
            data[0] = B00000000;
            data[1] = B00000110;
            data[2] = B00000111;
            break;

            case 'n':
            data[0] = B00000000;
            data[1] = B00000111;
            data[2] = B00000111;
            break;

            case 'o':
            data[0] = B00000100;
            data[1] = B00000111;
            data[2] = B00000111;
            break;

            case 'p':
            data[0] = B00000110;
            data[1] = B00000111;
            data[2] = B00000111;
            break;

            case 'q':
            data[0] = B00000111;
            data[1] = B00000111;
            data[2] = B00000111;
            break;  
        }
        
    }
    showPattern();
    

    // Update active animations
    for (int i = 0; i < 8; ++i) {
        if (animations[i].active) {
            updateAnimation(animations[i], pulseColor);
        }
    }

    // Other tasks for your Arduino loop can be added here
}

void allOff()
{
  for (int i=0;i<3;i++)
  {
    digitalWrite(row[i], LOW);
    digitalWrite(col[i], HIGH);
  }
}
void blinkLED() {
   
      // Save the last time you blinked the LED
       // Toggle LED state
            digitalWrite(LED_PIN_POS_V, HIGH);
            digitalWrite(LED_PIN_NEG_V,LOW);  // Set LED state
        
}

void offLED() {
   
   // Toggle LED state
            digitalWrite(LED_PIN_POS_V, LOW);
            digitalWrite(LED_PIN_NEG_V,HIGH);  // Set LED state
        
}

void showPattern()
{
  for (int thisrow=0;thisrow<rows;thisrow++)
  {
    //turn everything off
    allOff();
    //turn on current row
    digitalWrite(row[thisrow], HIGH);
    // loop through columns of this row and light
    for (int thiscol=0;thiscol<columns;thiscol++)
    {
      if (bitRead(data[thisrow],columns-thiscol-1)==1)
      {
        digitalWrite(col[thiscol], LOW);
      }
      else
      {
        digitalWrite(col[thiscol], HIGH);
      }
    }
    delay(pause);
  }
}