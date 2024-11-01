#ifndef APLICACIONCLIENTE_H
#define APLICACIONCLIENTE_H

#include "ClienteRPC.h"

class AplicacionCliente {
private:
    ClienteRPC* cliente;

public:
    AplicacionCliente(const string& host, int port);
    ~AplicacionCliente();
    void ejecutar();
};

#endif // APLICACIONCLIENTE_H
