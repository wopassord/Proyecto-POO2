#ifndef LOGINWINDOW_H
#define LOGINWINDOW_H

#include <QWidget>
#include <QLineEdit>
#include <QPushButton>
#include <QLabel>
#include "MainWindow.h"  // La ventana principal
#include "ClienteRPC.h"  // Cliente RPC para login y registro

class LoginWindow : public QWidget {
    Q_OBJECT

public:
    LoginWindow(const std::string& host, int port,QWidget *parent = nullptr);
    ~LoginWindow();

private slots:
    void onLoginClicked();
    void onSignUpClicked();

private:
    QLineEdit *usernameEdit;
    QLineEdit *passwordEdit;
    QPushButton *loginButton;
    QPushButton *signUpButton;
    QLabel *statusLabel;
    ClienteRPC *clienteRpc;  // Instancia de ClienteRPC para manejar solicitudes al servidor
};

#endif // LOGINWINDOW_H
