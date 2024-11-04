; Inicio del archivo G-Code de prueba
G21         ; Establecer las unidades en mil�metros
G90         ; Usar posicionamiento absoluto
G28         ; Llevar a casa todas las posiciones

G1 Z15.0 F9000 ; Elevar el cabezal para evitar colisiones
G1 X50 Y50 F3000 ; Mover el cabezal a (50, 50) a una velocidad de 3000 mm/min
G1 Z-1.0 F1200 ; Bajar el cabezal a -1 mm a una velocidad de 1200 mm/min
G1 X60 Y60 F1500 ; Mover el cabezal a (60, 60)
G1 X70 Y70 ; Mover el cabezal a (70, 70) sin especificar velocidad (usa la previa)

G28         ; Volver a la posici�n de origen (home)
M84         ; Apagar los motores

; Fin del archivo G-Code de prueba