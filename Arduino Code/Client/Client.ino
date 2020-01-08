
#include "Arduino.h"
#include <TinyGPS++.h>
#include <SoftwareSerial.h>
#include <util/delay.h>
#define SOFT_SERIAL_TX 10
#define SOFT_SERIAL_RX 11

#define GPSBaud 9600

bool gps_valid = 0;
bool lora_valid = 0;
bool gps_serial_valid = 0;
int callsign = 0; //callsign to determine which device this is
bool airborne = 0; //if mounted on a helicopter or drone this needs to be specified
String current_position = ""; //Save the GPS cords here. When airborne this will include the height
String current_time = ""; //Get the time from the GPS-signal
long pings_so_far =0;

int gps_timer=0;
int lora_timer=0;
bool state=0;




TinyGPSPlus gps;
SoftwareSerial GPS_Serial(SOFT_SERIAL_RX, SOFT_SERIAL_TX);
unsigned long previousMillis = 0;
String latitude;
String longitude;
const long interval_1 = 3000; //how often so send the signal

void setup()
{
  GPS_Serial.begin(GPSBaud);
  Serial.begin(9600);
  for(int x = 2;x<=9;x++)
 {
    pinMode(x,INPUT_PULLUP);
 }
 if(digitalRead(2)==LOW)
 {
    callsign +=1; 
 }

if(digitalRead(3)==LOW)
 {
    callsign +=2; 
 }
 if(digitalRead(4)==LOW)
 {
    callsign +=4; 
 }
 if(digitalRead(5)==LOW)
 {
    callsign +=8; 
 }
 if(digitalRead(6)==LOW)
 {
    callsign +=16; 
 }
 if(digitalRead(7)==LOW)
 {
    callsign +=32; 
 }
 if(digitalRead(8)==LOW)
 {
    callsign +=64; 
 }
 if(digitalRead(9)==LOW)
 {
    callsign +=128; 
 }
}

void loop()
{
  for(int x =0; x<15;x++)
  {
    gps_utilities();
    _delay_ms(100);
  }
  daten_senden();
  }
void daten_senden()
{
  if(true)
  {
    String datenpaket = "";
    datenpaket += "%%N";
    datenpaket += callsign;
    datenpaket += "LAT";
    datenpaket += latitude;
    datenpaket += "LON";
    datenpaket += longitude;
    datenpaket += "$$";
    Serial.write((char)0x00);
    Serial.write((char)0x00);
    Serial.write((char)0x09);
    char charBuf[50];
    datenpaket.toCharArray(charBuf, datenpaket.length()+1);
    //Data
    Serial.write(charBuf,datenpaket.length()+1);
    delay(50);
  }
  else
  {
    String datenpaket = "";
    datenpaket += "N";
    datenpaket += callsign;
    datenpaket += current_position;
    datenpaket +="FAIL_GPS";
    Serial.write((char)0x00);
    Serial.write((char)0x00);
    Serial.write((char)0x09);
    char charBuf[50];
    datenpaket.toCharArray(charBuf, datenpaket.length()+1);
    Serial.write(charBuf,datenpaket.length()+1);
  }
}



void gps_utilities() //this will read all the gps informations and then set the according variables
{ 

   while (GPS_Serial.available() > 0)
   {
    gps_serial_valid = 1;
    if (gps.encode(GPS_Serial.read()))
      {
        process_gps();
      }
    if ( gps.charsProcessed() < 10)
    {
            gps_serial_valid = 0;
            gps_valid = 0;
    }
    }
}


void process_gps()
{
  if (gps.location.isValid())
    {
        gps_valid = 1;
        latitude = String(gps.location.lat(),6);
        longitude = String( gps.location.lng(),6);
    }
else
    {
        latitude = String("--------");
        longitude = String("--------");
        gps_valid = 0;
    }

  if (gps.time.isValid())
  {
  current_time = gps.time.hour()+2; //+2 for GMT2
  current_time += ":";
  current_time += gps.time.minute();
  current_time +=":";
  current_time += gps.time.second();
}}

ISR(TIMER0_COMPA_vect){    //This is the interrupt request
  gps_timer++;
  lora_timer++;
}
