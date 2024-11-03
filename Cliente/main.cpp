#include <iostream>
#include <cstdlib>
#include "AplicacionCliente.h"
#include <QApplication>
#include "LoginWindow.h"

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Uso: cliente IP_HOST N_PORT\n";
        return -1;
    }

    std::string host = argv[1];
    int port = std::atoi(argv[2]);

    QApplication app(argc, argv);

    // Crear la ventana de login con el host y el puerto
    LoginWindow loginWindow(host, port);
    loginWindow.show();

    return app.exec();
}

