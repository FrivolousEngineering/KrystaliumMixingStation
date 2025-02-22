#include <FastLED.h>

#define LEFTLEDRINGPIN  D2 
#define RIGHTLEDRINGPIN D3
#define NUM_LEDS_PER_STRIP 24

#define FADE_RADIUS 5  // Number of LEDs affected in the blur
#define SPEED 0.4  // Movement speed (absolute)
#define COOLING 1  // Flicker cooling rate
#define SPARK_PROBABILITY 0.08   // Probability of a spark per interval (1% chance)
#define SPARK_INTERVAL_MS 500  // How often we check for a spark
#define COOL_INTERVAL_MS 100

float position = 0.0;  // Floating point position to enable sub-pixel movement
CRGB leds[NUM_LEDS_PER_STRIP];
CRGBPalette16 currentPalette;

// Gradient palette (slightly purple flickering effect)
DEFINE_GRADIENT_PALETTE(gradient) {
    0,   0,   0, 255,   // Blue
//  240,  120,   0, 255,   // Slightly purple
  255,  255,   0, 255    // More purple
};

// Heat value for flickering effect
byte heatMap[NUM_LEDS_PER_STRIP] = {0};

unsigned long lastSparkTime = 0;  // Track last time we checked for sparks
unsigned long lastCooldownTime = 0; 

void setup() {
  FastLED.addLeds<WS2812, LEFTLEDRINGPIN, GRB>(leds, NUM_LEDS_PER_STRIP).setCorrection(TypicalLEDStrip);
  FastLED.addLeds<WS2812, RIGHTLEDRINGPIN, GRB>(leds, NUM_LEDS_PER_STRIP).setCorrection(TypicalLEDStrip);
  
  currentPalette = gradient;  // Load color palette

  Serial.begin(115200);
  Serial.println("Booted");
}

void loop() {
  // Move the floating-point position
  position += SPEED;
  if (position >= NUM_LEDS_PER_STRIP) {
    position -= NUM_LEDS_PER_STRIP; // Wrap around for the LED ring
  }

  // Clear the LED buffer
  fill_solid(leds, NUM_LEDS_PER_STRIP, CRGB::Black);

  // Update flickering effect based on time
  unsigned long currentTime = millis();



  
  if (currentTime - lastSparkTime >= SPARK_INTERVAL_MS) {
    lastSparkTime = currentTime; // Reset timer
    applyFlicker(); // Handle sparking logic
    Serial.print("Current heat: ");
    Serial.println(heatMap[0]);
  }


  if (currentTime - lastCooldownTime >= COOL_INTERVAL_MS) {
    lastCooldownTime = currentTime;
    coolDown();
  }
  
  // Calculate brightness for each LED based on its distance from position
  for (int i = 0; i < NUM_LEDS_PER_STRIP; i++) {
    float distance = abs(position - i);  // How far this LED is from the light source

    // Wrap around the ring properly
    if (distance > NUM_LEDS_PER_STRIP / 2) {
      distance = NUM_LEDS_PER_STRIP - distance;
    }

    // Apply brightness based on distance
    if (distance <= FADE_RADIUS) {
      float intensity = 1.0 - (distance / FADE_RADIUS); // Linear fade
      // Map flicker value to color from palette
      byte colorIndex = scale8(heatMap[i], 255);
      leds[i] = ColorFromPalette(currentPalette, colorIndex, intensity * 255);
    }
  }

  // Apply gamma correction
  napplyGamma_video(leds, NUM_LEDS_PER_STRIP, 2.2);  

  FastLED.show();
  delay(50); // Adjust for smoothness
}

void coolDown(){
  int cooling = random8(0, COOLING + 2);
  for (int i = 0; i < NUM_LEDS_PER_STRIP; i++) {
    // Cool down slightly
    heatMap[i] = qsub8(heatMap[i], cooling);
  }
}

// 🎇 Time-Based Flicker Effect 🎇
void applyFlicker() {
  if (random(1000) < (SPARK_PROBABILITY * 1000)) { // Convert probability to integer check
    int heating = random8(160, 255);
    for (int i = 0; i < NUM_LEDS_PER_STRIP; i++) {
    
      heatMap[i] = qadd8(heatMap[i], heating);
    }
  }
}
