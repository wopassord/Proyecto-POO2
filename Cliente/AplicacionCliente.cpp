#include "AplicacionCliente.h"

AplicacionCliente::AplicacionCliente(const string& host, int port) {
    cliente = new ClienteRPC(host, port);
}

AplicacionCliente::~AplicacionCliente() {
    delete cliente;
}

void AplicacionCliente::ejecutar() {
    int opcion;

    while (true) {
        cliente->mostrarMenu();
        cin >> opcion;

        switch (opcion) {
            case 2:
                cliente->subirArchivoGCode();
                break;
            case 3:
                cliente->conectarDesconectarRobot();
                break;
            case 4:
                cliente->activarDesactivarMotores();
                break;
            case 5:
                cliente->seleccionarModoTrabajo();
                cliente->seleccionarModoCoordenadas();
                break;
            case 6:
                cliente->mostrarOperacionesCliente();
                break;
            case 7:
                cliente->modoManual();
                break;
            case 8:
                cliente->apagarServidor();
                cout << "Cliente apagado.\n";
                return;
            default:
                cout << "Opción solo disponible en Servidor. Intente de nuevo.\n";
                break;
        }
    }
}
