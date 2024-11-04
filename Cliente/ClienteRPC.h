#ifndef CLIENTERPC_H
#define CLIENTERPC_H

#include <iostream>
#include <fstream>
#include <sstream>
#ifdef _WIN32
#include <windows.h>
#endif
#include <thread>
#include <chrono>
#include <cmath>
#include "libreria_Chris_Morley/XmlRpc.h"

using namespace std;
using namespace XmlRpc;

class ClienteRPC
{
private:
    XmlRpcClient client;
    XmlRpcValue result, noArgs, args;
    double posicionActualX = 0.0, posicionActualY = 0.0, posicionActualZ = 0.0;
    bool estadoManual;

public:
    ClienteRPC(const string &host, int port);
    void login_o_signin();
    void activarAlarma();
    void apagarServidor();
    bool esPosicionAlcanzable(double x, double y, double z);
    void subirArchivoGCode();
    void conectarDesconectarRobot();
    void enviarComando(const string &comando);
    void seleccionarModoTrabajo();
    void seleccionarModoCoordenadas();
    void mostrarOperacionesCliente();
    void activarDesactivarMotores();
    void enviarComandoGCode();
    void modoManual();
    void mostrarMenu();
};

#endif
