#include <iostream>
#include <cstdlib>
#include "AplicacionCliente.h"

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Uso: cliente IP_HOST N_PORT\n";
        return -1;
    }


    string host = argv[1];
    int port = stoi(argv[2]);

    // Crear la aplicación cliente
    AplicacionCliente app(host, port);

    bool sesionIniciada = false;
    while (!sesionIniciada) {
        std::cout << "\nMenú de Inicio de Sesión:\n";
        std::cout << "1. Iniciar Sesión\n";
        std::cout << "2. Agregar Usuario\n";
        std::cout << "Seleccione una opción: ";
        int opcion;
        std::cin >> opcion;

        if (opcion == 1) {
            sesionIniciada = app.iniciar_sesion();
        } else if (opcion == 2) {
            app.agregar_usuario();
        } else {
            std::cout << "Opción inválida. Intente nuevamente.\n";
        }
    }
    
    app.ejecutar();

    return 0;
}
