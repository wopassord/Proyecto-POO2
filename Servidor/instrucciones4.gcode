; Inicio del archivo G-Code de prueba
G21         ; Establecer las unidades en milímetros
G90         ; Usar posicionamiento absoluto
G28         ; Llevar a casa todas las posiciones

M17         ; Activar motores
M3          ; Activar gripper
G1 X50 Y50 Z10 F1500 ; Mover a la posición (50, 50, 10) a 1500 mm/min
G1 X60 Y40 Z5 F2000  ; Mover a la posición (60, 40, 5) a 2000 mm/min
G91         ; Cambiar a modo de coordenadas relativas
G1 X10 Y-10 Z-5      ; Mover (10, -10, -5) relativo a la posición actual
M5          ; Desactivar gripper
M114        ; Reportar la posición actual y el modo de coordenadas
G28         ; Llevar todas las posiciones a casa (homing)
M18         ; Desactivar motores

; Fin del archivo G-Code de prueba
