; Inicio del archivo G-Code de prueba adicional - Alcanzable
G21         ; Establecer las unidades en milímetros
G90         ; Usar posicionamiento absoluto

G1 X80 Y80 F3000 ; Mover a (80, 80) a 3000 mm/min
G1 Z-2.0 F1200   ; Bajar el cabezal a -2 mm
G1 X90 Y90       ; Mover a (90, 90) sin especificar velocidad
G1 Z5.0          ; Elevar el cabezal a 5 mm

G28              ; Volver a la posición de origen (home)
M84              ; Apagar los motores

; Fin del archivo G-Code adicional - Alcanzable
