#include "AplicacionCliente.h"

AplicacionCliente::AplicacionCliente(const string& host, int port) {
    cliente = new ClienteRPC(host, port);
}

AplicacionCliente::~AplicacionCliente() {
    delete cliente;
}

void AplicacionCliente::ejecutar() {
    int opcion;

    cliente->login_o_signin();

    while (true) {
        cliente->mostrarMenu();
        cin >> opcion;

        switch (opcion) {
            
            case 1:
                cliente->conectarDesconectarRobot();
                break;
            case 2:
                cliente->activarDesactivarMotores();
                break;
            case 3:
                cliente->seleccionarModoTrabajo();
                break;
            case 4:
                cliente->seleccionarModoCoordenadas();
                break;
            case 5:
                cliente->mostrarOperacionesCliente();
                break;
            case 6:
                cliente->modoManual();
                break;
            case 7:
                cliente->subirArchivoGCode();
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
