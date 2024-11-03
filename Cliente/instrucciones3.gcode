; Inicio del archivo G-Code de prueba adicional - Inalcanzable
G21         ; Establecer las unidades en mil�metros
G90         ; Usar posicionamiento absoluto

G1 X200 Y200 F3000 ; Mover a (200, 200), excede el rango m�ximo
G1 Z-10.0 F1200    ; Bajar el cabezal a -10 mm
G1 X250 Y250       ; Mover a (250, 250) sin especificar velocidad

G28                ; Volver a la posici�n de origen (home)
M84                ; Apagar los motores

; Fin del archivo G-Code adicional - Inalcanzable
