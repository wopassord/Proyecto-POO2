#include <iostream>
#include <fstream>
#include <sstream>
#include <windows.h>
#include <thread>
#include <chrono>
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

    // Método para activar la alarma visual y auditiva
    void activarAlarma() {
        HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);

        for (int i = 0; i < 5; ++i) {
            // Cambia el color de la consola a rojo y muestra el mensaje de alarma
            SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_INTENSITY);
            std::cout << "\r¡ALERTA! Error en la transferencia del archivo." << std::flush;

            // Generar un sonido de alarma
            Beep(1000, 300); // Frecuencia de 1000 Hz durante 300 ms
            MessageBeep(MB_ICONHAND); // Sonido de error del sistema

            // Pausa para el parpadeo
            std::this_thread::sleep_for(std::chrono::milliseconds(300));

            // Cambia el color de la consola al color normal
            SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE);
            std::cout << "\r                                     " << std::flush; // Borrar el mensaje

            // Pausa entre flashes
            std::this_thread::sleep_for(std::chrono::milliseconds(300));
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
            activarAlarma(); // Activar alarma en caso de error al abrir el archivo
            return;
        }

        // Convertir el contenido del archivo en una cadena
        stringstream buffer;
        buffer << archivoGCode.rdbuf();
        string contenidoArchivo = buffer.str();

        // Establecer los argumentos
        args[0] = XmlRpcValue(rutaArchivo);  // Nombre del archivo
        args[1] = XmlRpcValue(contenidoArchivo);

        // Enviar al servidor
        if (client.execute("subir_archivo_gcode", args, result)) {
            // Verificar respuesta del servidor para determinar si activar la alarma
            string respuesta = static_cast<string>(result);
            if (respuesta == "Error al subir el archivo") {
                activarAlarma();
            } else {
                cout << "Respuesta del servidor: " << respuesta << "\n\n";
            }
        } else {
            cerr << "Error en la conexión al subir el archivo G-Code\n\n";
            activarAlarma();
        }
    }

    // Método para conectar o desconectar el robot
    void conectarDesconectarRobot() {
        if (client.execute("recibir_comando_cliente", 1, result)) {
            cout << "Respuesta del servidor: " << result << "\n\n";
        } else {
            cerr << "Error al enviar el comando al servidor\n\n";
        }
    }

    // Método para enviar un comando personalizado
    void enviarComando(const string& comando) {
        args[0] = comando;  // Establece el comando a enviar

        if (client.execute("recibir_comando_cliente", args, result)) {
            cout << "Respuesta del servidor: " << result << "\n\n";
        } else {
            cerr << "Error al enviar el comando al servidor\n\n";
        }
    }

    // Método para mostrar el menú
    void mostrarMenu() {
        cout << "Menu de opciones:\n";
        cout << "1. Saludo personalizado\n";
        cout << "2. Subir archivo G-Code\n"; 
        cout << "3. Conectar/desconectar robot.\n"; // ACCION 1 EN SERVIDOR
        cout << "4. Activar/desactivar motores del robot.\n"; // ACCION 2
        cout << "5. Seleccionar los modos de trabajo (manual o automatico) o coordenadas (absolutas o relativas). \n "; // ACCION 3 Y 4
        cout << "6. Mostrar operaciones posibles a realizar por un cliente o un operador en el servidor. \n"; // ACCION 5
        cout << "7. [SOLO MODO MANUAL] Enviar comandos en formato G-Code para accionar robot. \n"; // ACCION 6
        cout << "8. Salir y apagar todo\n";
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
                // Implementar saludo personalizado aquí
            }  
            else if (opcion == 2) {
                cliente->subirArchivoGCode();
            } 
            else if (opcion == 3){
                cliente->conectarDesconectarRobot();
            }
            else if (opcion == 4){
                // Implementar función de activar/desactivar motores
            }
            else if (opcion == 5){
                // Implementar función de selección de modos de trabajo
            }
            else if (opcion == 6){
                // Implementar mostrar operaciones posibles
            }
            else if (opcion == 7){
                // Implementar enviar comando G-Code en modo manual
            }
            else if (opcion == 8) {
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