#include <FastLED.h>

#define LEFTLEDRINGPIN  D2 
#define RIGHTLEDRINGPIN D3
#define NUM_LEDS_PER_STRIP 24
#define VOLTMETER_PIN D6
#define TILTPIN A0

#define FADE_RADIUS 6  // Number of LEDs affected in the blur
#define SPEED 0.6  // Movement speed (absolute)
#define COOLING 1  // Flicker cooling rate
#define SPARK_PROBABILITY 0.25   // Probability of a spark per interval (1% chance)
#define SPARK_INTERVAL_MS 100  // How often we check for a spark
#define COOL_INTERVAL_MS 100
#define VOLT_INTERVAL_MS 100

#define FADE_INTERVAL_MS 100 // How often should fade in fade/out trigger?

#define MAX_CMD_LEN 128

float position = 0.0;  // Floating point position to enable sub-pixel movement
int voltmeter_value = 0;
bool heatingEnabled = false;

CRGB leds[NUM_LEDS_PER_STRIP];
CRGBPalette16 currentPalette;

// Gradient palette (slightly purple flickering effect)
DEFINE_GRADIENT_PALETTE(gradient) {
    0,   100,   0, 255,   // Blue with tiny bit of red
  255,  255,   0, 255    // More purple
};

// Heat value for flickering effect
byte heatMap[NUM_LEDS_PER_STRIP] = {0};

unsigned long lastSparkTime = 0;  // Track last time we checked for sparks
unsigned long lastCooldownTime = 0; 
unsigned long lastFadeTime = 0;
unsigned long lightOffTime = 0;
unsigned long lastVoltTime = 0;

int leftBrightness = 0;
int rightBrightness = 0;

int leftFlashing = false;
int rightFlashing = false;

bool leftFlashingRed = false;
bool rightFlashingRed = false;


void setup() {
  FastLED.addLeds<WS2812, LEFTLEDRINGPIN, GRB>(leds, NUM_LEDS_PER_STRIP).setCorrection(TypicalLEDStrip);
  FastLED.addLeds<WS2812, RIGHTLEDRINGPIN, GRB>(leds, NUM_LEDS_PER_STRIP).setCorrection(TypicalLEDStrip);
  
  currentPalette = gradient;  // Load color palette
  pinMode(VOLTMETER_PIN, OUTPUT);   
  Serial.begin(115200);
  Serial.println("Booted");
  FastLED.setBrightness(0); // Start with brightness off
}

void processCommand(String command) {

  char cmdBuffer[MAX_CMD_LEN];
  memset(cmdBuffer, 0, sizeof(cmdBuffer));  // Clear buffer to prevent leftover data

  // Ensure we don't overflow
  int len = command.length();
  if (len >= MAX_CMD_LEN) {
    Serial.println("Command too long");
    return;
  }
  command.toCharArray(cmdBuffer, MAX_CMD_LEN);
  cmdBuffer[sizeof(cmdBuffer) - 1] = '\0';
  
  trim(cmdBuffer);  // Trim newlines and trailing spaces

  char* keyword = strtok(cmdBuffer, " ");
  char* argument = strtok(NULL, "");

  if (keyword == NULL) return;
  strupr(keyword);  // Convert keyword to uppercase

  if (argument != NULL && strcmp(keyword, "WRITE") != 0) {
    strupr(argument);
  }
  
  if (strcmp(keyword, "NAME") == 0) {
    handleNameCommand(argument);
  } else if (strcmp(keyword, "LIGHT") == 0){
    handleLightCommand(argument);
  } else if (strcmp(keyword, "VOLT") == 0) {
    handleVoltCommand(argument);
  } else if (strcmp(keyword, "FLASH") == 0) {
    handleFlashCommand(argument);
  } else if (strcmp(keyword, "ERROR") == 0) {
    handleErrorCommand(argument);
  }
}

void handleFlashCommand(char* arguments) {
  char* directionStr = strtok(arguments, " ");
  if (directionStr == NULL) {
    Serial.println("Missing FLASH argument");
    return;
  }
  
  // Flash in blue for FLASH commands
  if (strcmp(directionStr, "LEFT") == 0) {
    leftBrightness = 0;
    leftFlashing = true;
    leftFlashingRed = false;
  } else if (strcmp(directionStr, "RIGHT") == 0) {
    rightBrightness = 0;
    rightFlashing = true;
    rightFlashingRed = false;
  } else if (strcmp(directionStr, "BOTH") == 0) {
    leftBrightness = 0;
    rightBrightness = 0;
    leftFlashing = true;
    rightFlashing = true;
    leftFlashingRed = false;
    rightFlashingRed = false;
  } else {
    Serial.println("Invalid FLASH argument");
  }
}

void handleErrorCommand(char* arguments) {
  char* directionStr = strtok(arguments, " ");
  if (directionStr == NULL) {
    Serial.println("Missing ERROR argument");
    return;
  }
  
  // Flash in red for ERROR commands
  if (strcmp(directionStr, "LEFT") == 0) {
    leftBrightness = 0;
    leftFlashing = true;
    leftFlashingRed = true;
  } else if (strcmp(directionStr, "RIGHT") == 0) {
    rightBrightness = 0;
    rightFlashing = true;
    rightFlashingRed = true;
  } else if (strcmp(directionStr, "BOTH") == 0) {
    leftBrightness = 0;
    rightBrightness = 0;
    leftFlashing = true;
    rightFlashing = true;
    leftFlashingRed = true;
    rightFlashingRed = true;
  } else {
    Serial.println("Invalid ERROR argument");
  }
}

void handleVoltCommand(char* arguments){
  char* valueStr = strtok(arguments, " ");

  unsigned long value = atol(valueStr);
  voltmeter_value = value;
}

void handleLightCommand(char* arguments){
  char* onOrOff = strtok(arguments, " ");
  char* durationStr = strtok(NULL, " ");
  
  if(onOrOff == NULL){
    Serial.println("LIGHT must be provided with an argument");
  } else if (strcmp(onOrOff, "ON") == 0) {
    heatingEnabled = true;
    if (durationStr != NULL) {
      unsigned long duration = atol(durationStr);
      if (duration > 0) {
        lightOffTime = millis() + duration;
      }
    }
    Serial.println("Turning lights on");
  } else if (strcmp(onOrOff, "OFF") == 0) {
    Serial.println("Turning lights off");
    heatingEnabled = false;
  } else {
    Serial.println("LIGHT must be provided with either ON or OFF");
  }
}

void handleNameCommand(char* argument) {
  if (argument != NULL) {
    Serial.println("Setting the name is not supported!");
  } 
  else {
    Serial.println("Name: LIGHT");
  }
}

void applyVolt(){
  //if(voltmeter_value > 255) voltmeter_value = 255;
  if(voltmeter_value < 0) voltmeter_value = 0;
  
  analogWrite(VOLTMETER_PIN, voltmeter_value);
  
}

void loop() {
  // Listen for commands over serial
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }

   
  // Move the floating-point position
  position += SPEED;
  if (position >= NUM_LEDS_PER_STRIP) {
    position -= NUM_LEDS_PER_STRIP; // Wrap around for the LED ring
  }
    
  if(rightFlashing) {
    rightBrightness += 1;
  } 
  if (leftFlashing) {
    leftBrightness += 1;  
  }

  // This bit of code handles the flashing of left && right 
  if(leftBrightness == 0 && rightBrightness == 0) {
    fill_solid(leds, NUM_LEDS_PER_STRIP, CRGB::Black);
  } else {

    if( rightBrightness > 0) {
      if(rightFlashingRed){
        fill_solid(leds, NUM_LEDS_PER_STRIP, CRGB::Red);
      } else {
        fill_solid(leds, NUM_LEDS_PER_STRIP, CRGB::Blue);
      }
      FastLED[0].showLeds(rightBrightness);
    }
    if(leftBrightness > 0) {
      if(leftFlashingRed){
        fill_solid(leds, NUM_LEDS_PER_STRIP, CRGB::Red);
      }  else {
        fill_solid(leds, NUM_LEDS_PER_STRIP, CRGB::Blue);
      }
      FastLED[1].showLeds(leftBrightness);
    }
    if(!rightFlashing) {
      rightBrightness -= 1;
    } 
    if (!leftFlashing) {
      leftBrightness -= 1;  
    }
    
    if(leftBrightness < 0) {
      leftBrightness = 0;
    } 
    if(leftBrightness >= 255){
      leftFlashing = false;
    }

    if(rightBrightness < 0) { 
      rightBrightness = 0;
    }

    if(rightBrightness >= 255){
      rightFlashing = false;
    }
    return;
  }


  // Clear the LED buffer
  

  // Update flickering effect based on time
  unsigned long currentTime = millis();
  
  if (currentTime - lastSparkTime >= SPARK_INTERVAL_MS) {
    lastSparkTime = currentTime; // Reset timer
    applyFlicker(); // Handle sparking logic
  }

  if (currentTime - lastVoltTime >= VOLT_INTERVAL_MS) {
    lastVoltTime = currentTime; // Reset timer
    applyVolt();
  }

  if (currentTime - lastCooldownTime >= COOL_INTERVAL_MS) {
    lastCooldownTime = currentTime;
    coolDown();
  }

  if(currentTime - lastFadeTime >= FADE_INTERVAL_MS){
    lastFadeTime = currentTime;
    if(heatingEnabled) {
      if(FastLED.getBrightness() + 2 < 255) {
        FastLED.setBrightness(FastLED.getBrightness() + 2);
      } else {
        FastLED.setBrightness(255);
      }
    } else {
      if(FastLED.getBrightness() - 3 > 0) {
        FastLED.setBrightness(FastLED.getBrightness() - 3);
      } else {
        FastLED.setBrightness(0);
      }
    }
  }

  // Disable the lights if a timer was set
  if(heatingEnabled && lightOffTime != 0 && currentTime >= lightOffTime) {
    Serial.println("Turning lights off");
    heatingEnabled = false;
    lightOffTime = 0;
  }


  // Calculate brightness for each LED based on its distance from position
  for (int i = 0; i < NUM_LEDS_PER_STRIP; i++) {
    float distance = abs(position - i);  // How far this LED is from the light source

    // Wrap around the ring properly
    if (distance > NUM_LEDS_PER_STRIP / 2) {
      distance = NUM_LEDS_PER_STRIP - distance;
    }

    float intensity = 1.0 - (distance / FADE_RADIUS); // Linear fade
    // Map flicker value to color from palette.
    // TODO; For some reason if I scale it to 255 instead of 230, it gets weird jittery color effects (shifting back to full blue) at the top values.
    byte colorIndex = scale8(heatMap[i], 230);
    leds[i] = ColorFromPalette(currentPalette, colorIndex, intensity * 255);
  }

  // Apply gamma correction
  napplyGamma_video(leds, NUM_LEDS_PER_STRIP, 2.2);  

  FastLED.show();
  delay(50); // Adjust for smoothness
}

void coolDown(){
  for (int i = 0; i < NUM_LEDS_PER_STRIP; i++) {
    int cooling = 0;
    // Normal runnig procedure.
    if(heatingEnabled){
      // Cool down based on heat.
      if(heatMap[i] < 100) {
        cooling = random8(0, COOLING + 1);
      } else if (heatMap[i] < 150) {
        cooling = random8(0, COOLING + 3);
      } else if (heatMap[i] < 200) {
        cooling = random8(0, COOLING + 4);
      } else {
        cooling = random8(0, COOLING + 6);
      }
    } else {
      // We're closing down, Cool down with fixed rate
       cooling = random8(0, COOLING + 2);
    }
    
    
    // Cool down slightly
    heatMap[i] = qsub8(heatMap[i], cooling);
  }
}

// 🎇 Time-Based Flicker Effect 🎇
void applyFlicker() {
  if(!heatingEnabled) return;
  
  if (random(1000) < (SPARK_PROBABILITY * 1000)) { // Convert probability to integer check
    int heating = random8(2, 5) + random8(2, 5); // Prefer the mid values a bit over the extremes
    for (int i = 0; i < NUM_LEDS_PER_STRIP; i++) {
    
      heatMap[i] = qadd8(heatMap[i], heating);
    }
  }
}

void trim(char* str) {
  int len = strlen(str);
  while (len > 0 && (str[len - 1] == '\r' || str[len - 1] == '\n' || str[len - 1] == ' ')) {
    str[--len] = '\0';
  }
}
