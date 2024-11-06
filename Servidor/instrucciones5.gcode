; Archivo G-Code Final sin Errores de Espacio de Trabajo

G21         ; Establecer las unidades en milímetros
G90         ; Usar posicionamiento absoluto
G28         ; Llevar a casa todas las posiciones

; Movimientos dentro de los límites ajustados

; Movimientos bajos en Z (conservador)
G1 X50 Y50 Z10 F1500   ; Cerca del origen, Z bajo
G1 X100 Y50 Z10 F1500  ; Límite seguro en X alto, Y bajo
G1 X100 Y100 Z10 F1500 ; Límite seguro en X y Y alto, Z bajo
G1 X50 Y100 Z10 F1500  ; X bajo, Y alto, Z bajo

; Movimientos intermedios en Z
G1 X50 Y50 Z50 F1500   ; Cerca del origen, Z intermedio
G1 X100 Y50 Z50 F1500  ; X alto, Y bajo, Z intermedio
G1 X100 Y100 Z50 F1500 ; X y Y altos, Z intermedio
G1 X50 Y100 Z50 F1500  ; X bajo, Y alto, Z intermedio

; Movimientos altos en Z
G1 X50 Y50 Z80 F1500   ; Cerca del origen, Z alto
G1 X100 Y50 Z80 F1500  ; X alto, Y bajo, Z alto
G1 X100 Y100 Z80 F1500 ; X y Y altos, Z alto
G1 X50 Y100 Z80 F1500  ; X bajo, Y alto, Z alto

; Movimientos de prueba en el centro
G1 X75 Y75 Z30 F1500   ; Centro aproximado, Z bajo
G1 X75 Y75 Z50 F1500   ; Centro aproximado, Z intermedio
G1 X75 Y75 Z80 F1500   ; Centro aproximado, Z alto

; Regresar a posición segura antes de finalizar
G28                      ; Llevar a origen (home)
M18                     ; Apagar los motores

; Fin del archivo G-Code Final sin Errores

