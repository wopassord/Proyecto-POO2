#include "LoginWindow.h"
#include <QVBoxLayout>
#include <QMessageBox>

// Constructor modificado para inicializar ClienteRPC con host y puerto
LoginWindow::LoginWindow(const std::string& host, int port, QWidget *parent)
    : QWidget(parent) {
    setWindowTitle("Login");

    // Crear ClienteRPC con el host y puerto dados
    clienteRpc = new ClienteRPC(host, port);

    // Elementos de la GUI
    QLabel *usernameLabel = new QLabel("Usuario:");
    usernameEdit = new QLineEdit();
    
    QLabel *passwordLabel = new QLabel("Contraseña:");
    passwordEdit = new QLineEdit();
    passwordEdit->setEchoMode(QLineEdit::Password);
    
    loginButton = new QPushButton("Iniciar sesión");
    signUpButton = new QPushButton("Registrarse");
    statusLabel = new QLabel();

    // Layout
    QVBoxLayout *layout = new QVBoxLayout();
    layout->addWidget(usernameLabel);
    layout->addWidget(usernameEdit);
    layout->addWidget(passwordLabel);
    layout->addWidget(passwordEdit);
    layout->addWidget(loginButton);
    layout->addWidget(signUpButton);
    layout->addWidget(statusLabel);
    setLayout(layout);

    // Conexiones
    connect(loginButton, &QPushButton::clicked, this, &LoginWindow::onLoginClicked);
    connect(signUpButton, &QPushButton::clicked, this, &LoginWindow::onSignUpClicked);
}

LoginWindow::~LoginWindow() {
    delete clienteRpc;
}

void LoginWindow::onLoginClicked() {
    std::string username = usernameEdit->text().toStdString();
    std::string password = passwordEdit->text().toStdString();

    // Intentar iniciar sesión a través de ClienteRPC
    clienteRpc->login_o_signin(username, password);

    // Suponiendo que login_o_signin devuelve un resultado exitoso o no:
    QMessageBox::information(this, "Login", "Inicio de sesión exitoso.");
    MainWindow *mainWindow = new MainWindow(clienteRpc);  // Pasamos el cliente a la ventana principal
    mainWindow->show();
    this->close();
}

void LoginWindow::onSignUpClicked() {
    std::string username = usernameEdit->text().toStdString();
    std::string password = passwordEdit->text().toStdString();

    // Intentar registrarse a través de ClienteRPC
    clienteRpc->login_o_signin(username, password);

    QMessageBox::information(this, "Registro", "Registro exitoso.");
}
