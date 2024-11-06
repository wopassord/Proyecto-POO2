#include "AplicacionCliente.h"
#include <algorithm>
#include <iostream>

AplicacionCliente::AplicacionCliente(const string& host, int port) {
    cliente = new ClienteRPC(host, port);
}

AplicacionCliente::~AplicacionCliente() {
    delete cliente;
}

bool AplicacionCliente::iniciar_sesion(){
    return cliente->iniciarSesion();
}
bool AplicacionCliente::agregar_usuario(){
   return cliente->agregarUsuario();
}
void AplicacionCliente::ejecutar() {
    string entrada;


    
    while (true) {
        cliente->mostrarMenu();
        cin >> entrada;

        // Verificar si la entrada contiene solo dígitos
        bool esNumeroValido = !entrada.empty() && std::all_of(entrada.begin(), entrada.end(), ::isdigit);
        if (!esNumeroValido)
        {
            cout << "Entrada inválida. Por favor, ingrese un número entero.\n";
            continue;
        }

        int opcion = std::stoi(entrada); // Convertir la cadena a entero


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
