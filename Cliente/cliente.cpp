#include <iostream>
#include <fstream>
#include <sstream>
#include <windows.h>
#include <thread>
#include <chrono>
#include <thread>
#include <chrono>
#include <cmath>
#include "libreria_Chris_Morley/XmlRpc.h" 
using namespace std;
using namespace XmlRpc;

// Clase que representa el cliente XML-RPC
class ClienteRPC {
private:
    XmlRpcClient client;
    XmlRpcValue result, noArgs, args;
    double posicionActualX = 0.0, posicionActualY = 0.0, posicionActualZ = 0.0; // Posición acumulada del robot

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
 #include <cmath> // Para usar sqrt y pow

// Método para verificar si una posición es alcanzable
bool esPosicionAlcanzable(double x, double y, double z) {
    double distancia = sqrt(pow(x, 2) + pow(y, 2) + pow(z, 2));
    double longitudMaxima = 122.0 + 120.0 + 120.0; // Longitud máxima del brazo

    return distancia <= longitudMaxima;
}

// Método para subir archivo G-Code con verificación de coordenadas
void subirArchivoGCode() {
    string rutaArchivo;
    cout << "Ingrese la ruta del archivo G-Code: ";
    getline(cin >> ws, rutaArchivo);

    // Leer el archivo en modo de solo lectura
    ifstream archivoGCode(rutaArchivo, ios::in);
    if (archivoGCode.fail()) {
        cerr << "Error al abrir el archivo: " << rutaArchivo << "\n\n";
        activarAlarma();  // Activar alarma en caso de error al abrir el archivo
        return;
    }

    // Convertir el contenido del archivo en una cadena completa
    stringstream buffer;
    buffer << archivoGCode.rdbuf();
    string contenidoArchivo = buffer.str();

    // Cierra el archivo para asegurarnos de no manipularlo más
    archivoGCode.close();

    // Procesar el contenido del G-Code para verificar coordenadas
    stringstream contenidoStream(contenidoArchivo);  // Reutilizamos el contenido leído
    string linea;
    bool coordenadasValidas = true;
    double modoAbsoluto = true;

    // Reiniciar posición acumulada para este archivo
    double posAcumuladaX = 0.0, posAcumuladaY = 0.0, posAcumuladaZ = 0.0;

    while (getline(contenidoStream, linea)) {
        // Cambiar el modo de coordenadas según el comando
        if(linea.find("G90") != string::npos){
            modoAbsoluto = true; // Modo absoluto
            continue;
        } else if (linea.find("G91") != string::npos){
            modoAbsoluto = false; // Modo relativo
            continue;
        }

        // Verificar si la línea contiene un comando G1, que especifica una posición
        if (linea.find("G1") != string::npos) {
            double x = posicionActualX, y = posicionActualY, z = posicionActualZ;
            size_t posX = linea.find("X"), posY = linea.find("Y"), posZ = linea.find("Z");

            if (posX != string::npos) x = stod(linea.substr(posX + 1));
            if (posY != string::npos) y = stod(linea.substr(posY + 1));
            if (posZ != string::npos) z = stod(linea.substr(posZ + 1));

            // Calcular nueva posición acumulada
            double nuevaPosX = modoAbsoluto ? x : posicionActualX + x;
            double nuevaPosY = modoAbsoluto ? y : posicionActualY + y;
            double nuevaPosZ = modoAbsoluto ? z : posicionActualZ + z;

            // Verificar si la posición es alcanzable
            if (!esPosicionAlcanzable(nuevaPosX, nuevaPosY, nuevaPosZ)) {
                cerr << "Posición fuera del alcance acumulativo: X" << nuevaPosX << " Y" << nuevaPosY << " Z" << nuevaPosZ << "\n";
                activarAlarma();
                coordenadasValidas = false;
                break;
            }

            // Actualizar la posición acumulada solo en modo relativo
            posicionActualX = nuevaPosX;
            posicionActualY = nuevaPosY;
            posicionActualZ = nuevaPosZ;
        }
    }

    if (!coordenadasValidas) {
        cerr << "El archivo G-Code contiene posiciones no alcanzables acumuladas.\n\n";
        return;
    }

    // Establecer los argumentos para el servidor
    args[0] = XmlRpcValue(rutaArchivo);  // Nombre del archivo
    args[1] = XmlRpcValue(contenidoArchivo);  // Contenido completo del archivo

    // Enviar al servidor si las coordenadas son válidas
    if (client.execute("subir_archivo_gcode", args, result)) {
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

    void seleccionarModoTrabajo() {
        if (client.execute("recibir_comando_cliente", 3, result)) {
            cout << "Modo de trabajo actualizado: " << result << "\n\n";
        } else {
            cerr << "Error al enviar el comando de modo de trabajo\n\n";
        }
    }

    void seleccionarModoCoordenadas() {
        if (client.execute("recibir_comando_cliente", 4, result)) {
            cout << "Modo de coordenadas actualizado: " << result << "\n\n";
        } else {
            cerr << "Error al enviar el comando de modo de coordenadas\n\n";
        }
    }

    void mostrarOperacionesCliente() {
        if (client.execute("recibir_comando_cliente", 5, result)) {
            cout << "Operaciones disponibles:\n" << result << "\n\n";
        } else {
            cerr << "Error al obtener las operaciones del servidor\n\n";
        }
    }
    void activarDesactivarMotores() {

    }

    void enviarComandoGCode() {
        string comando;
        cout << "Ingrese el comando G-Code para el robot: ";
        getline(cin >> ws, comando);

        args[0] = XmlRpcValue(comando);

        if (client.execute("recibir_comando_cliente", args, result)) {
            cout << "Comando G-Code enviado correctamente: " << result << "\n\n";
        } else {
            cerr << "Error al enviar el comando G-Code\n\n";
            activarAlarma();
        }
    }

    // Método para mostrar el menú
    void mostrarMenu() {
        cout << "Menu de opciones:\n";
        cout << "2. [MODO AUTOMÁTICO] Subir archivo G-Code\n"; 
        cout << "3. Conectar/desconectar robot.\n";
        cout << "4. Activar/desactivar motores del robot.\n";
        cout << "5. Seleccionar modos de trabajo y coordenadas.\n";
        cout << "6. Mostrar operaciones posibles.\n";
        cout << "7. [MODO MANUAL] Enviar comandos en formato G-Code.\n";
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
                    cliente->enviarComandoGCode();
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
