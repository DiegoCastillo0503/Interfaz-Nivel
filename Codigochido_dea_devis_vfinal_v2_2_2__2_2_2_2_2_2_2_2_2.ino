#include "BTS7960.h"

const uint8_t EN = 8;
const uint8_t L_PWM = 9;
const uint8_t R_PWM = 10;
const uint8_t pinAnalogico = A0;

BTS7960 motorController(EN, L_PWM, R_PWM);

// --- PARÁMETROS DEL CONTROL PI ---
float Kp = 1000;
float Ki = 0.5;
float setpoint = 3.0;
int clk;

float integral = 0;
unsigned long tiempoAnterior = 0;

// --- PARÁMETROS DEL FILTRO EMA ---
float alpha = 0.1;
float voltajeFiltrado = 0.0;

void setup() {
  Serial.begin(9600);
  motorController.Enable();
  tiempoAnterior = millis();
  analogReference(INTERNAL);   // referencia de 1.1 V
  voltajeFiltrado = analogRead(pinAnalogico) * (1.1 / 1023.0);
}

void loop() {
  // --- LEER NUEVO SET POINT DESDE EL MONITOR SERIE ---
  if (Serial.available() > 0) {
    String entrada = Serial.readStringUntil('\n');
    float nuevoSetpoint = entrada.toFloat();
  }
    // --- CÁLCULOS DE TIEMPO ---
  unsigned long tiempoActual = millis();
  float dt = (tiempoActual - tiempoAnterior) / 1000.0;
  tiempoAnterior = tiempoActual;

  // --- LECTURA Y FILTRADO ---
  int lecturaADC = analogRead(pinAnalogico);
  float voltajeCrudo = lecturaADC * (1.1 / 1023.0);

  voltajeFiltrado = (alpha * voltajeCrudo) + ((1.0 - alpha) * voltajeFiltrado);

  // --- CONVERSIÓN A DISTANCIA ---
  float distancia = (voltajeFiltrado - 0.366) * 17.15;

  // --- CÁLCULO DEL ERROR ---
  float error = setpoint - distancia;

  // --- CÁLCULO DEL PI ---
  integral = integral + (error * dt);
  float salidaPI = (Kp * error) + (Ki * integral);
  int pwm = (int)salidaPI;
  
  // --- REGLA BANG-BANG (Acelerar si falta mucho) ---
  if (error > 4.0) {
    pwm = 255;
  }
  // --- LÍMITES Y ANTI-WINDUP ---
  if (pwm >= 255) {
    pwm = 255;
    integral = integral - (error * dt);
  }
  else if (pwm < 110) {
    pwm = 110;
    integral = integral - (error * dt);
  }
    // --- MONITOREO ---
  if (clk = 10) {
    Serial.print("Distancia:");
    Serial.print(distancia);
    Serial.print(", SetPoint:");
    Serial.print(setpoint);
    Serial.print(", Error:");
    Serial.println(error);
    clk = 0;
  }

  // --- ACCIÓN DEL MOTOR ---
  motorController.TurnLeft(pwm);
  clk++;
  delay (10);
}