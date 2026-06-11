/*
 * ================================================================
 *  Smart City Traffic Monitor - ESP32 (v2 - Simplified)
 * ================================================================
 *  Arsitektur baru (mengatasi AP Isolation di WiFi cafe):
 *    HP Camera → Backend Python (auto-fetch + YOLO) → ESP32 (poll + LCD)
 * 
 *  ESP32 hanya poll hasil analisis dari backend, tidak perlu
 *  ambil gambar dari HP camera langsung.
 * 
 *  Hardware:
 *    - ESP32 Dev Module
 *    - LCD I2C 16x2 (SDA=21, SCL=22)
 * 
 *  Library: LiquidCrystal I2C (by Frank de Brabander)
 * ================================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ── Konfigurasi WiFi ──────────────────────────────────────────────
const char* WIFI_SSID     = "Tjaptigabersaudara";
const char* WIFI_PASSWORD = "KitaBersaudara03";

// ── Backend Python ────────────────────────────────────────────────
const char* IP_BACKEND    = "192.168.100.175";
const int   PORT_BACKEND  = 8000;

// ── Interval Polling ──────────────────────────────────────────────
const unsigned long POLL_INTERVAL_MS = 1000;  // 1 detik

// ── LCD I2C ───────────────────────────────────────────────────────
LiquidCrystal_I2C lcd(0x27, 16, 2);

// ── State ─────────────────────────────────────────────────────────
String  lastStatus       = "MENUNGGU...";
int     lastVehicleCount = 0;
int     lastCarCount     = 0;
int     lastMotorCount   = 0;
unsigned long lastPollMs = 0;
int     errorCount       = 0;

// ─────────────────────────────────────────────────────────────────
//  Helper: Parse angka dari JSON
// ─────────────────────────────────────────────────────────────────
int parseJsonInt(const String& json, const String& key) {
  String search = "\"" + key + "\":";
  int idx = json.indexOf(search);
  if (idx == -1) return 0;
  int start = idx + search.length();
  while (start < (int)json.length() && json[start] == ' ') start++;
  int end = start;
  while (end < (int)json.length() && (isDigit(json[end]) || json[end] == '-')) end++;
  if (end == start) return 0;
  return json.substring(start, end).toInt();
}

// ─────────────────────────────────────────────────────────────────
//  Helper: Parse string dari JSON
// ─────────────────────────────────────────────────────────────────
String parseJsonString(const String& json, const String& key) {
  String search = "\"" + key + "\":";
  int idx = json.indexOf(search);
  if (idx == -1) return "";
  int start = idx + search.length();
  while (start < (int)json.length() && json[start] == ' ') start++;
  if (json[start] != '"') return "";
  start++;
  int end = json.indexOf('"', start);
  if (end == -1) return "";
  return json.substring(start, end);
}

// ─────────────────────────────────────────────────────────────────
//  Tampilkan hasil di LCD
// ─────────────────────────────────────────────────────────────────
void tampilkanLCD() {
  lcd.clear();

  // Baris 1: Status + jumlah total
  lcd.setCursor(0, 0);
  if (lastStatus == "LANCAR") {
    lcd.print("LANCAR  ");
  } else if (lastStatus == "PADAT") {
    lcd.print("PADAT   ");
  } else if (lastStatus == "MACET") {
    lcd.print("MACET!! ");
  } else {
    lcd.print(lastStatus.substring(0, 8));
  }
  char totalStr[8];
  snprintf(totalStr, sizeof(totalStr), "N:%d", lastVehicleCount);
  lcd.setCursor(16 - strlen(totalStr), 0);
  lcd.print(totalStr);

  // Baris 2: Mobil & Motor
  lcd.setCursor(0, 1);
  char detail[17];
  snprintf(detail, sizeof(detail), "M:%d Mtr:%d", lastCarCount, lastMotorCount);
  lcd.print(detail);
}

// ─────────────────────────────────────────────────────────────────
//  Poll backend untuk hasil analisis terbaru
// ─────────────────────────────────────────────────────────────────
void pollBackend() {
  HTTPClient http;
  char url[80];
  snprintf(url, sizeof(url), "http://%s:%d/esp32/result", IP_BACKEND, PORT_BACKEND);

  http.begin(url);
  http.setTimeout(5000);
  int httpCode = http.GET();

  if (httpCode == HTTP_CODE_OK) {
    String body = http.getString();
    Serial.printf("[Backend] Response: %s\n", body.c_str());

    lastVehicleCount = parseJsonInt(body, "vehicle_count");
    lastCarCount     = parseJsonInt(body, "car_count");
    lastMotorCount   = parseJsonInt(body, "motorcycle_count");
    lastStatus       = parseJsonString(body, "status");
    if (lastStatus == "") lastStatus = "UNKNOWN";

    errorCount = 0;

    Serial.printf("[Hasil] N:%d M:%d Mtr:%d Status:%s\n",
      lastVehicleCount, lastCarCount, lastMotorCount, lastStatus.c_str());

    tampilkanLCD();
  } else {
    errorCount++;
    Serial.printf("[Backend] Error HTTP: %d (count: %d)\n", httpCode, errorCount);

    if (errorCount >= 3) {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("BACKEND ERROR");
      lcd.setCursor(0, 1);
      lcd.printf("HTTP: %d", httpCode);
    }
  }

  http.end();
}

// ─────────────────────────────────────────────────────────────────
//  SETUP
// ─────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(500);

  Wire.begin(21, 22);
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Smart Traffic");
  lcd.setCursor(0, 1);
  lcd.print("Connecting WiFi..");

  Serial.printf("\nMenghubungkan ke WiFi: %s\n", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempt = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    attempt++;
    if (attempt > 40) {
      Serial.println("\nGagal connect WiFi! Restart...");
      lcd.clear();
      lcd.print("WIFI GAGAL!");
      delay(3000);
      ESP.restart();
    }
  }

  String localIP = WiFi.localIP().toString();
  Serial.printf("\nWiFi Connected! IP: %s\n", localIP.c_str());
  Serial.printf("Backend: %s:%d\n", IP_BACKEND, PORT_BACKEND);

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("READY!");
  lcd.setCursor(0, 1);
  lcd.print(localIP);
}

// ─────────────────────────────────────────────────────────────────
//  LOOP
// ─────────────────────────────────────────────────────────────────
void loop() {
  unsigned long now = millis();
  if (now - lastPollMs >= POLL_INTERVAL_MS) {
    lastPollMs = now;
    Serial.println("--- Poll backend ---");
    pollBackend();
  }
}
