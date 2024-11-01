#include <iostream>
#include <cstdlib>
#include "AplicacionCliente.h"

using namespace std;

int main(int argc, char* argv[]) {
    if (argc != 3) {
        cerr << "Uso: cliente IP_HOST N_PORT\n";
        return -1;
    }

    string host = argv[1];
    int port = atoi(argv[2]);

    // Crear la aplicación cliente y ejecutar el ciclo principal
    AplicacionCliente app(host, port);
    app.ejecutar();

    return 0;
}
