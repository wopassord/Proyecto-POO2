#include <iostream>
#include <stdlib.h>
#include <fstream>
#include <sstream>
#include "libreria_Chris_Morley/XmlRpc.h" 
using namespace std;
using namespace XmlRpc;

// Clase que representa el cliente XML-RPC
class ClienteRPC {
private:
    XmlRpcClient client;
    XmlRpcValue result, noArgs, args;

public:
    // Constructor para inicializar el cliente con el host y puerto
    ClienteRPC(const string& host, int port) : client(host.c_str(), port) {}

    // Método para solicitar un saludo personalizado
    void solicitarSaludo() {
        string nombre;
        cout << "Ingrese su nombre para el saludo personalizado: ";
        cin >> nombre;
        args[0] = nombre;

        if (client.execute("saludo_personalizado", args, result)) {
            cout << "Respuesta del servidor: " << result << "\n\n";
        } else {
            cerr << "Error al ejecutar el saludo personalizado\n\n";
        }
    }

    // Método para apagar el servidor de manera remota
    void apagarServidor() {
        if (client.execute("apagar_servidor", noArgs, result)) {
            cout << "Servidor apagado correctamente: " << result << "\n\n";
        } else {
            cerr << "Error al intentar apagar el servidor.\n\n";
        }
    }

    // Método para subir archivo G-Code
    void subirArchivoGCode() {
        string rutaArchivo;
        cout << "Ingrese la ruta del archivo G-Code: ";
        getline(cin >> ws, rutaArchivo);

        // Leer el archivo
        ifstream archivoGCode(rutaArchivo);
        if (archivoGCode.fail()) {
            cerr << "Error al abrir el archivo: " << rutaArchivo << "\n\n";
            return;
        }

        // Convertir el contenido del archivo en una cadena
        stringstream buffer;
        buffer << archivoGCode.rdbuf();
        string contenidoArchivo = buffer.str();

        // Establecer los argumentos
        args[0] = XmlRpcValue(rutaArchivo);        // Nombre del archivo
        args[1] = XmlRpcValue(contenidoArchivo);

        // Enviar al servidor
        if (client.execute("subir_archivo_gcode", args, result)) {
            cout << "Respuesta del servidor: " << result << "\n\n";
        } else {
            cerr << "Error al subir el archivo G-Code\n\n";
        }
    }

    // Método para mostrar el menú
    void mostrarMenu() {
        cout << "Menu de opciones:\n";
        cout << "1. Saludo personalizado\n";
        cout << "2. Subir archivo G-Code\n";
        cout << "3. Salir y apagar todo\n";
        cout << "Seleccione una opción: ";
    }
};

// Clase que controla el flujo del programa principal
class AplicacionCliente {
private:
    ClienteRPC* cliente;

public:
    // Constructor para inicializar el cliente con los argumentos de host y puerto
    AplicacionCliente(const string& host, int port) {
        cliente = new ClienteRPC(host, port);
    }

    ~AplicacionCliente() {
        delete cliente;
    }

    // Método que ejecuta el bucle principal del programa
    void ejecutar() {
        int opcion;

        while (true) {
            cliente->mostrarMenu();
            cin >> opcion;

            if (opcion == 1) {
                cliente->solicitarSaludo();
            }  
            else if (opcion == 2) {
                cliente->subirArchivoGCode();
            } 
            else if (opcion == 3) {
                cliente->apagarServidor();
                cout << "Cliente apagado.\n";
                break;
            } 
            else {
                cout << "Opción inválida. Intente de nuevo.\n";
            }
        }
    }
};

// Función principal
int main(int argc, char* argv[])
{
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
