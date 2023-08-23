Testy łączności LoRa.

Testy zrealizowane na modułach:
- moduł raspberry PI PICO RP2040: https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html#raspberry-pi-pico
- moduł LCD TFT RGB, 160x128px, 65k color, interfejs:SPI, sterownik: ST7735S, 1,8 cala.
- moduł radiowy LoRa RA-02, 433MHz, interfejs SPI, układ SX1278.

Aplikacja testowa zrealizowana w Micro Python.

Przetestowano w wersji: v1.20.0 (2023-04-26)

Do testu użyte są dwa zestawy ww modułów.

Jeden z aplikacją w konfiguracji MASTER (parametr LoRaMaster = 1) inicuje łączność z modułem SLAVE.

Drugi z aplikacją w konfiguracji SLAVE (parametr LoRaMaster = 0) po odebraniu ramki wysyła ramkę potwierdzenia do MASTERa.

![20230823_211132](https://github.com/kolomanoloxxx/lora_TEST/assets/142832900/d13c2868-a3a5-4aed-a70c-ba31649a6612)
![20230823_210946](https://github.com/kolomanoloxxx/lora_TEST/assets/142832900/45d7652d-8665-41d2-a386-7d3ea1e29322)
![20230823_211205](https://github.com/kolomanoloxxx/lora_TEST/assets/142832900/5a6b997a-f05a-4a6b-bf2e-16f702232fe7)
