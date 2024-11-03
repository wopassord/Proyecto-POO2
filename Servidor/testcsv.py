import csv

try:
    with open('usuarios_servidor.csv', mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['usuario_prueba', 'contrasena_prueba', True])
    print("Escritura de prueba exitosa en usuarios_servidor.csv")
except Exception as e:
    print(f"Error al escribir en el archivo CSV: {e}")
