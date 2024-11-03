#include <iostream>
#include <cstdlib>
#include "AplicacionCliente.h"
// '''
// #include <QApplication>
// #include "LoginWindow.h"
// ''' COMENTADAS LAS LIBRERIAS

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Uso: cliente IP_HOST N_PORT\n";
        return -1;
    }


    string host = argv[1];
    int port = atoi(argv[2]);

    // Crear la aplicación cliente y ejecutar el ciclo principal
    AplicacionCliente app(host, port);
    app.ejecutar();

    return 0;
}
// '''
//     QApplication app(argc, argv);

//     // Crear la ventana de login con el host y el puerto
//     LoginWindow loginWindow(host, port);
//     loginWindow.show();

    // return app.exec();
    // ''' COMENTADA INTERFAZ DE USUARIO DISTINTA DE LA TERMINAL
}

