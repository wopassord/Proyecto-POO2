#include "ClienteRPC.h"

ClienteRPC::ClienteRPC(const string &host, int port) : client(host.c_str(), port) {}

void ClienteRPC::login_o_signin()
{
    string nombre_usuario, contrasena;
    cout << "Ingrese el nombre de usuario: ";
    cin >> nombre_usuario;
    cout << "Ingrese la contrasena: ";
    cin >> contrasena;

    args[0] = nombre_usuario;
    args[1] = contrasena;

    cout << "Conexion exitosa" << endl;

    /*
    if (client.execute("login_o_signin", args, result)) {
        cout << static_cast<string>(result) << "\n";
    } else {
        cerr << "Error en la conexión al iniciar sesión o registrar el usuario.\n";
    }
    */
}

void ClienteRPC::activarAlarma()
{
#ifdef _WIN32
    HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);

    for (int i = 0; i < 5; ++i)
    {
        SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_INTENSITY);
        std::cout << "\r¡ALERTA! Error en la transferencia del archivo." << std::flush;

        Beep(1000, 300);
        MessageBeep(MB_ICONHAND);

        std::this_thread::sleep_for(std::chrono::milliseconds(300));

        SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE);
        std::cout << "\r                                     " << std::flush;

        std::this_thread::sleep_for(std::chrono::milliseconds(300));
    }
#else
    for (int i = 0; i < 5; ++i)
    {
        std::cout << "\033[1;31m" << "\r¡ALERTA! Error en la transferencia del archivo.\a" << std::flush;
        std::this_thread::sleep_for(std::chrono::milliseconds(300));

        // Restablecer color de texto
        std::cout << "\033[0m" << "\r                                     " << std::flush;
        std::this_thread::sleep_for(std::chrono::milliseconds(300));
    }
#endif
}

void ClienteRPC::apagarServidor()
{
    if (client.execute("apagar_servidor", noArgs, result))
    {
        cout << "Servidor apagado correctamente: " << result << "\n\n";
    }
    else
    {
        cerr << "Error al intentar apagar el servidor.\n\n";
    }
}

bool ClienteRPC::esPosicionAlcanzable(double x, double y, double z)
{
    double distancia = sqrt(pow(x, 2) + pow(y, 2) + pow(z, 2));
    double longitudMaxima = 122.0 + 120.0 + 120.0;
    return distancia <= longitudMaxima;
}

void ClienteRPC::subirArchivoGCode()
{
    string rutaArchivo;
    cout << "Ingrese la ruta del archivo G-Code: ";
    getline(cin >> ws, rutaArchivo);

    // Leer el archivo en modo de solo lectura
    ifstream archivoGCode(rutaArchivo, ios::in);
    if (archivoGCode.fail())
    {
        cerr << "Error al abrir el archivo: " << rutaArchivo << "\n\n";
        activarAlarma(); // Activar alarma en caso de error al abrir el archivo
        return;
    }

    // Convertir el contenido del archivo en una cadena completa
    stringstream buffer;
    buffer << archivoGCode.rdbuf();
    string contenidoArchivo = buffer.str();

    // Cierra el archivo para asegurarnos de no manipularlo más
    archivoGCode.close();

    // Procesar el contenido del G-Code para verificar coordenadas
    stringstream contenidoStream(contenidoArchivo); // Reutilizamos el contenido leído
    string linea;
    bool coordenadasValidas = true;
    double modoAbsoluto = true;

    // Reiniciar posición acumulada para este archivo
    double posAcumuladaX = 0.0, posAcumuladaY = 0.0, posAcumuladaZ = 0.0;

    while (getline(contenidoStream, linea))
    {
        // Cambiar el modo de coordenadas según el comando
        if (linea.find("G90") != string::npos)
        {
            modoAbsoluto = true; // Modo absoluto
            continue;
        }
        else if (linea.find("G91") != string::npos)
        {
            modoAbsoluto = false; // Modo relativo
            continue;
        }

        // Verificar si la línea contiene un comando G1, que especifica una posición
        if (linea.find("G1") != string::npos)
        {
            double x = posicionActualX, y = posicionActualY, z = posicionActualZ;
            size_t posX = linea.find("X"), posY = linea.find("Y"), posZ = linea.find("Z");

            if (posX != string::npos)
                x = stod(linea.substr(posX + 1));
            if (posY != string::npos)
                y = stod(linea.substr(posY + 1));
            if (posZ != string::npos)
                z = stod(linea.substr(posZ + 1));

            // Calcular nueva posición acumulada
            double nuevaPosX = modoAbsoluto ? x : posicionActualX + x;
            double nuevaPosY = modoAbsoluto ? y : posicionActualY + y;
            double nuevaPosZ = modoAbsoluto ? z : posicionActualZ + z;

            // Verificar si la posición es alcanzable
            if (!esPosicionAlcanzable(nuevaPosX, nuevaPosY, nuevaPosZ))
            {
                cerr << "Posicion fuera del alcance acumulativo: X" << nuevaPosX << " Y" << nuevaPosY << " Z" << nuevaPosZ << "\n";
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

    if (!coordenadasValidas)
    {
        cerr << "El archivo G-Code contiene posiciones no alcanzables acumuladas.\n\n";
        return;
    }

    // Establecer los argumentos para el servidor
    args[0] = XmlRpcValue(rutaArchivo);      // Nombre del archivo
    args[1] = XmlRpcValue(contenidoArchivo); // Contenido completo del archivo

    // Enviar al servidor si las coordenadas son válidas
    if (client.execute("subir_archivo_gcode", args, result))
    {
        string respuesta = static_cast<string>(result);
        if (respuesta == "Error al subir el archivo")
        {
            activarAlarma();
        }
        else
        {
            cout << "Respuesta del servidor: " << respuesta << "\n\n";
        }
    }
    else
    {
        cerr << "Error en la conexion al subir el archivo G-Code\n\n";
        activarAlarma();
    }
}

void ClienteRPC::conectarDesconectarRobot()
{
    if (client.execute("recibir_comando_cliente", 1, result))
    {
        cout << "Respuesta del servidor: " << result << "\n\n";
    }
    else
    {
        cerr << "Error al enviar el comando al servidor\n\n";
    }
}

void ClienteRPC::enviarComando(const string &comando)
{
    XmlRpcValue args;
    args[0] = comando;
    if (client.execute("recibir_comando_cliente", args, result))
    {
        cout << "Respuesta del servidor: " << result << "\n\n";
    }
    else
    {
        cerr << "Error al enviar el comando al servidor\n\n";
    }
}

void ClienteRPC::seleccionarModoTrabajo()
{
    if (client.execute("recibir_comando_cliente", 3, result))
    {
        cout << "Modo de trabajo actualizado: " << result << "\n\n";
    }
    else
    {
        cerr << "Error al enviar el comando de modo de trabajo\n\n";
    }
}

void ClienteRPC::seleccionarModoCoordenadas()
{
    if (client.execute("recibir_comando_cliente", 4, result))
    {
        cout << "Modo de coordenadas actualizado: " << result << "\n\n";
    }
    else
    {
        cerr << "Error al enviar el comando de modo de coordenadas\n\n";
    }
}

void ClienteRPC::mostrarOperacionesCliente()
{
    cout << "\nOperaciones posibles a realizar por un cliente o por un operador en el servidor: \n";
    cout << "M3: Activar gripper." << endl;
    cout << "M5: Desactivar gripper." << endl;
    cout << "G28: Hacer homing." << endl;
    cout << "G1: Hacer un movimiento a una determinada posición (para enviar este comando, realizar lo siguiente: [G1 Xa Yb Zc], donde Xa, Yb y Zc son las posiciones a las que se debe mover)." << endl;
    cout << "M114: Reporte de modo de coordenadas y posición actual." << endl;
    cout << "G90: Modo de coordenadas absolutas." << endl;
    cout << "G91: Modo de coordenadas relativas." << endl;
    cout << "M17: Activar motores." << endl;
    cout << "M18: Desactivar motores.\n" << endl;
}


void ClienteRPC::activarDesactivarMotores()
{
    if (client.execute("recibir_comando_cliente", 2, result))
    {
        cout << "Respuesta del servidor: " << result << "\n\n";
    }
    else
    {
        cerr << "Error al enviar el comando al servidor\n\n";
    }
}

#include <regex> //libreria para comprobar que se ingrese GCode
void ClienteRPC::enviarComandoGCode()
{
    string comando;
    cout << "Ingrese el comando G-Code para el robot: ";
    getline(cin >> ws, comando);

    std::regex gcode_regex("^[GM]\\d+"); // valida que el comando empieza con G o M
    if (!std::regex_match(comando, gcode_regex))
    {
        cerr << "Error: Comando invalido. Solo se permiten comandos en GCode.\n\n";
        activarAlarma();
        return; // Salir del método sin enviar el comando
    }


    XmlRpcValue args;
    args[0] = comando;

    if (client.execute("recibir_comando_cliente", args, result))
    {
        cout << "Comando G-Code enviado correctamente: " << result << "\n\n";
    }
    else
    {
        cerr << "Error al enviar el comando G-Code\n\n";
        activarAlarma();
    }
}

void ClienteRPC::modoManual()
{
    string entrada;
    while (true)
    {
        cout << "\n--- MODO MANUAL ---\n";
        cout << "1. Enviar comando G-Code\n";
        cout << "2. Salir del Modo Manual y volver al inicio (envia G28)\n";
        cout << "Seleccione una opcion: ";

        cin >> entrada;

        // Verificar si la entrada contiene solo dígitos
        bool esNumeroValido = !entrada.empty() && std::all_of(entrada.begin(), entrada.end(), ::isdigit);
        if (!esNumeroValido)
        {
            cout << "Entrada invalida. Por favor, ingrese un numero entero.\n";
            continue;
        }

        int opcionManual = std::stoi(entrada); // Convertir la cadena a entero

        if (opcionManual == 1)
        {
            enviarComandoGCode();
        }
        else if (opcionManual == 2)
        {
            enviarComando("G28");
            cout << "Saliendo del Modo Manual y volviendo al inicio...\n";
            break;
        }
        else
        {
            cout << "Opción invalida. Intente de nuevo.\n";
        }
    }
}


void ClienteRPC::mostrarMenu()
{
    cout << "Menu de opciones:\n";
    cout << "1. Conectar/desconectar robot.\n";
    cout << "2. Activar/desactivar motores del robot.\n";
    cout << "3. Seleccionar modos de trabajo (manual o automatico).\n";
    cout << "4. Seleccionar modos de coordenadas.\n";
    cout << "5. Mostrar operaciones posibles.\n";
    cout << "6. [MODO MANUAL] Enviar comandos en formato G-Code.\n";
    cout << "7. [MODO AUTOMATICO] Subir archivo G-Code\n";
    cout << "8. Salir y apagar todo\n";
    cout << "Seleccione una opcion: ";
}
