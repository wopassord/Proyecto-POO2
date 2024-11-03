#include "MainWindow.h"
#include <QVBoxLayout>
#include <QMessageBox>
#include <QFile>

MainWindow::MainWindow(ClienteRPC *clienteRpc, QWidget *parent) : QMainWindow(parent), clienteRpc(clienteRpc) {
    setWindowTitle("Cliente G-Code");

    // Widgets
    selectFileButton = new QPushButton("Seleccionar archivo G-Code");
    uploadFileButton = new QPushButton("Subir archivo al servidor");
    connectButton = new QPushButton("Conectar/Desconectar Robot");
    toggleMotorsButton = new QPushButton("Activar/Desactivar Motores");
    filePathLabel = new QLabel("Archivo no seleccionado.");

    // Layout
    QVBoxLayout *layout = new QVBoxLayout();
    layout->addWidget(selectFileButton);
    layout->addWidget(filePathLabel);
    layout->addWidget(uploadFileButton);
    layout->addWidget(connectButton);
    layout->addWidget(toggleMotorsButton);

    QWidget *centralWidget = new QWidget(this);
    centralWidget->setLayout(layout);
    setCentralWidget(centralWidget);

    // Conexiones
    connect(selectFileButton, &QPushButton::clicked, this, &MainWindow::onSelectFileClicked);
    connect(uploadFileButton, &QPushButton::clicked, this, &MainWindow::onUploadFileClicked);
    connect(connectButton, &QPushButton::clicked, this, &MainWindow::onConnectClicked);
    connect(toggleMotorsButton, &QPushButton::clicked, this, &MainWindow::onToggleMotorsClicked);
}

void MainWindow::onSelectFileClicked() {
    filePath = QFileDialog::getOpenFileName(this, "Seleccionar archivo G-Code", "", "Archivos G-Code (*.gcode);;Todos los archivos (*)");
    if (!filePath.isEmpty()) {
        filePathLabel->setText("Archivo seleccionado: " + filePath);
    }
}

void MainWindow::onUploadFileClicked() {
    if (filePath.isEmpty()) {
        QMessageBox::warning(this, "Error", "Seleccione un archivo primero.");
        return;
    }

    // Leer el archivo
    QFile file(filePath);
    if (!file.open(QIODevice::ReadOnly)) {
        QMessageBox::critical(this, "Error", "No se pudo abrir el archivo.");
        return;
    }

    QByteArray fileData = file.readAll();
    file.close();

    std::string contenidoArchivo = fileData.toStdString();
    clienteRpc->subirArchivoGCode(contenidoArchivo);

    QMessageBox::information(this, "Subida", "Archivo subido correctamente.");
}

void MainWindow::onConnectClicked() {
    clienteRpc->conectarDesconectarRobot();
}

void MainWindow::onToggleMotorsClicked() {
    clienteRpc->activarDesactivarMotores();
}
