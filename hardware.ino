#include <SPI.h>
#include <MFRC522.h>
#include <HTTPClient.h>
#include <WiFi.h>
#include <ArduinoJson.h>

#define SS_1_PIN 21
#define SS_2_PIN 22
#define SS_3_PIN 2
//#define SS_4_PIN 5 //I am admin
#define RST_PIN 4
#define LED_STP1_1 12
#define LED_STP1_2 14
#define LED_STP2_1 27
#define LED_STP2_2 26
#define LED_STP3_1 25
#define LED_STP3_2 33

const int ipaddress[4] = {103, 97, 67, 25};

char* ssid = "vivo1951";
char* pass = "12345678";

byte nuidPICC[4] = {0, 0, 0, 0};
MFRC522::MIFARE_Key key;
MFRC522 rfid_1 = MFRC522(SS_1_PIN, RST_PIN);
MFRC522 rfid_2 = MFRC522(SS_2_PIN, RST_PIN);
MFRC522 rfid_3 = MFRC522(SS_3_PIN, RST_PIN);
//MFRC522 rfid_4 = MFRC522(SS_4_PIN, RST_PIN);
void setup() {
 
 Serial.begin(115200);
 Serial.println(F("Initialize System"));

 WiFi.begin("vivo1951", "12345678");
 while (WiFi.status() != WL_CONNECTED) {          
 
    delay(500);
    Serial.println("Waiting for connection");
 
 }
 SPI.begin();
 rfid_1.PCD_Init();
 //rfid_4.PCD_Init();
 rfid_2.PCD_Init();
 rfid_3.PCD_Init();
 Serial.print(F("Reader : \n"));
 rfid_1.PCD_DumpVersionToSerial();
 //rfid_4.PCD_DumpVersionToSerial();
 rfid_2.PCD_DumpVersionToSerial();
 rfid_3.PCD_DumpVersionToSerial();
 pinMode(LED_STP1_1, OUTPUT);
 digitalWrite(LED_STP1_1, LOW);
 pinMode(LED_STP1_2, OUTPUT);
 digitalWrite(LED_STP1_2, LOW);

 pinMode(LED_STP2_1, OUTPUT);
 digitalWrite(LED_STP2_1, LOW);
 pinMode(LED_STP2_2, OUTPUT);
 digitalWrite(LED_STP2_2, LOW);

 pinMode(LED_STP3_1, OUTPUT);
 digitalWrite(LED_STP3_1, LOW);
 pinMode(LED_STP3_2, OUTPUT);
 digitalWrite(LED_STP3_2, LOW);
 
}
void loop() {
 readRFID1();
 readRFID2();
 readRFID3();
 //readRFID4();
}
void readRFID1(void ) { 
 
 for (byte i = 0; i < 6; i++) {
   key.keyByte[i] = 0xFF;
 }
 
 if ( ! rfid_1.PICC_IsNewCardPresent())
   return;
 
 if (  !rfid_1.PICC_ReadCardSerial())
   return;
 
 for (byte i = 0; i < 4; i++) {
   nuidPICC[i] = rfid_1.uid.uidByte[i];
 }
 
 Serial.print(F("RFID_1 In dec: "));
 String resp = printDec(rfid_1.uid.uidByte, rfid_1.uid.size, "stop1");
 if(resp == "100"){
  Serial.println("Success");
  digitalWrite(LED_STP1_1, HIGH);
  delay(2000);
  digitalWrite(LED_STP1_1, LOW);
 }else{
  Serial.println("Fail");
  digitalWrite(LED_STP1_2, HIGH);
  delay(2000);
  digitalWrite(LED_STP1_2, LOW);
 }
 //sendData("r1", )
 Serial.println();
 // Halt PICC
 rfid_1.PICC_HaltA();
 // Stop encryption on PCD
 rfid_1.PCD_StopCrypto1();

 readRFID1();
}

void readRFID2(void ) { 
 ////Read RFID card
 for (byte i = 0; i < 6; i++) {
   key.keyByte[i] = 0xFF;
 }
 // Look for new 1 cards
 if ( ! rfid_2.PICC_IsNewCardPresent())
   return;
 // Verify if the NUID has been readed
 if (  !rfid_2.PICC_ReadCardSerial())
   return;
 // Store NUID into nuidPICC array
 for (byte i = 0; i < 4; i++) {
   nuidPICC[i] = rfid_2.uid.uidByte[i];
 }
 
 Serial.print(F("RFID_2 In dec: "));
 String resp = printDec(rfid_2.uid.uidByte, rfid_2.uid.size, "stop2");
 if(resp == "100"){
  Serial.println("Success");
  digitalWrite(LED_STP2_1, HIGH);
  delay(2000);
  digitalWrite(LED_STP2_1, LOW);
 }else{
  Serial.println("Fail");
  digitalWrite(LED_STP2_2, HIGH);
  delay(2000);
  digitalWrite(LED_STP2_2, LOW);
 }
 Serial.println();
 // Halt PICC
 rfid_2.PICC_HaltA();
 // Stop encryption on PCD
 rfid_2.PCD_StopCrypto1();

 readRFID2();
}

void readRFID3(void ) { 
 ////Read RFID card
 for (byte i = 0; i < 6; i++) {
   key.keyByte[i] = 0xFF;
 }
 // Look for new 1 cards
 if ( ! rfid_3.PICC_IsNewCardPresent())
   return;
 // Verify if the NUID has been readed
 if (  !rfid_3.PICC_ReadCardSerial())
   return;
 // Store NUID into nuidPICC array
 for (byte i = 0; i < 4; i++) {
   nuidPICC[i] = rfid_3.uid.uidByte[i];
 }
 
 Serial.print(F("RFID_3 In dec: "));
 String resp = printDec(rfid_3.uid.uidByte, rfid_3.uid.size, "stop3");
 if(resp == "100"){
  Serial.println("Success");
  digitalWrite(LED_STP3_1, HIGH);
  delay(2000);
  digitalWrite(LED_STP3_1, LOW);
 }else{
  Serial.println("Fail");
  digitalWrite(LED_STP3_2, HIGH);
  delay(2000);
  digitalWrite(LED_STP3_2, LOW);
 }
 Serial.println();
 // Halt PICC
 rfid_3.PICC_HaltA();
 // Stop encryption on PCD
 rfid_3.PCD_StopCrypto1();

 readRFID3();
}

//void readRFID4(void ) { /* function readRFID */
/* ////Read RFID card
 for (byte i = 0; i < 6; i++) {
   key.keyByte[i] = 0xFF;
 }
 // Look for new 1 cards
 if ( ! rfid_4.PICC_IsNewCardPresent())
   return;
 // Verify if the NUID has been readed
 if (  !rfid_4.PICC_ReadCardSerial())
   return;
 // Store NUID into nuidPICC array
 for (byte i = 0; i < 4; i++) {
   nuidPICC[i] = rfid_4.uid.uidByte[i];
 }
 
 Serial.print(F("RFID_4 In dec: "));
 byte *buffer = rfid_4.uid.uidByte; 
 byte bufferSize = rfid_4.uid.size;
 String s="";
 for (byte i = 0; i < bufferSize; i++) {
   Serial.print(buffer[i] < 0x10 ? " 0" : " ");
   s = s +(String)(buffer[i] < 0x10 ? " 0" : " ");
   Serial.print(buffer[i], DEC); 
   s = s +(String)(buffer[i]); 
 }
 Serial.println(s);
 sendData1(s);

 Serial.println();
 // Halt PICC
 rfid_4.PICC_HaltA();
 // Stop encryption on PCD
 rfid_4.PCD_StopCrypto1();

 readRFID4();
}*/
/**
   Helper routine to dump a byte array as hex values to Serial.
*/
void printHex(byte *buffer, byte bufferSize) {
 for (byte i = 0; i < bufferSize; i++) {
   Serial.print(buffer[i] < 0x10 ? " 0" : " ");
   Serial.print(buffer[i], HEX);
 }
}

/**
   Helper routine to dump a byte array as dec values to Serial.
*/
String printDec(byte *buffer, byte bufferSize, String t) {
 String s="";
 for (byte i = 0; i < bufferSize; i++) {
   Serial.print(buffer[i] < 0x10 ? " 0" : " ");
   s = s +(String)(buffer[i] < 0x10 ? " 0" : " ");
   Serial.print(buffer[i], DEC); 
   s = s +(String)(buffer[i]); 
 }
 Serial.println(s);
 String resp = sendData(t,s);
 return(resp);
}

String sendData(String stp, String uid){

  if (WiFi.status() == WL_CONNECTED) {             //Check WiFi connection status
 
    DynamicJsonDocument doc(2048);
    doc["uid"] = uid;
    doc["stp"] = stp;

    // Serialize JSON document
    String json;
    serializeJson(doc, json);

    WiFiClient client;
    HTTPClient http;                               //Declare object of class HTTPClient
 
    http.begin(client, "http://192.168.168.203:5000/tryMy");      //Specify request destination 
    http.addHeader("Content-Type", "application/json");           //Specify content-type header
 
    int httpCode = http.POST(json);                               //Send the request
    String payload = http.getString();                            //Get the response payload
 
    Serial.println(httpCode);                                     //Print HTTP return code
    Serial.println(payload);                                     //Print request response payload
    String resp = payload;
    
    http.end();  //Close connection

    return(resp);
 
  } else {
 
    Serial.println("Error in WiFi connection");
 
  }
}

void sendData1(String s ) {
  if (WiFi.status() == WL_CONNECTED) {             //Check WiFi connection status
 
    DynamicJsonDocument doc(2048);
    doc["uid"] = s;

    // Serialize JSON document
    String json;
    serializeJson(doc, json);

    WiFiClient client;
    HTTPClient http;                               //Declare object of class HTTPClient
 
    http.begin(client, "http://192.168.168.203/setrfid");      //Specify request destination
    http.addHeader("Content-Type", "application/json");           //Specify content-type header
 
    int httpCode = http.POST(json);                               //Send the request
    String payload = http.getString();                            //Get the response payload
 
    Serial.println("httpcode: "+httpCode);                                     //Print HTTP return code
    Serial.println(payload);                                      //Print request response payload
 
    http.end();  //Close connection
 
  } else {
 
    Serial.println("Error in WiFi connection");
 
  }
}
