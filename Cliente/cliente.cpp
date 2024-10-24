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
        cout<< "3. Conectar/desconectar robot.\n";
        cout<< "4. Activar/desactivar motores del robot.\n";
        cout<< "5. Mostrar reporte de informacion general. \n";
        cout<<"6. [SOLO ADMIN] Mostrar reporte de log de trabajo del servidor. \n "; // las que dicen solo admin para mi no van 
        cout<< "7. Seleccionar los modos de trabajo (manual o automatico) o coordenadas (absolutas o relativas). \n ";
        cout<<"8. [SOLO ADMIN] Mostrar usuarios. \n";
        cout<< "9. [SOLO ADMIN] Mostrar/editar los parametros de conexion del robot. \n ";
        cout<< "10. Mostrar operaciones posibles a realizar por un cliente o un operador en el servidor. \n";
        cout<< "11. [SOLO MODO MANUAL] Enviar comandos en formato G-Code para accionar robot. \n";
        cout << "12. Salir y apagar todo\n";// esta la deje para probar pero no va
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
            else if (opcion == 12) {
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
