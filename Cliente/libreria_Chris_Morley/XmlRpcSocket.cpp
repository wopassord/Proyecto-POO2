#include <iostream>
#include <string>
#include <cstring>  // Para memset
#include <cstdlib>  // Para exit
#include <cstdio>   // Para snprintf

#if defined(_WIN32)
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "Ws2_32.lib")  // Vincula la biblioteca Winsock
#define EINPROGRESS    WSAEINPROGRESS
#define EWOULDBLOCK    WSAEWOULDBLOCK
#define ETIMEDOUT      WSAETIMEDOUT
#else
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <errno.h>
#include <fcntl.h>
#endif

using namespace std;

namespace XmlRpc {

// Inicializa Winsock en Windows
#if defined(_WIN32)
static void initWinSock() {
    static bool wsInit = false;
    if (!wsInit) {
        WSADATA wsaData;
        if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
            cerr << "Error al inicializar Winsock: " << WSAGetLastError() << endl;
            exit(1);
        }
        wsInit = true;
    }
}
#else
#define initWinSock() // No es necesario en Linux
#endif // _WIN32

class XmlRpcSocket {
public:
    static int socket();
    static void close(int fd);
    static bool setNonBlocking(int fd);
    static bool setReuseAddr(int fd);
    static bool bind(int fd, int port);
    static bool listen(int fd, int backlog);
    static int accept(int fd);
    static bool connect(int fd, string& host, int port);
    static bool nbRead(int fd, string& s, bool* eof);
    static bool nbWrite(int fd, string& s, int* bytesSoFar);
    static int getError();
    static string getErrorMsg();
    static string getErrorMsg(int error);
};

// Manejo de errores no fatales
static inline bool nonFatalError() {
    int err = XmlRpcSocket::getError();
    return (err == EINPROGRESS || err == EAGAIN || err == EWOULDBLOCK || err == EINTR);
}


// Implementaciones de los métodos

int XmlRpcSocket::socket() {
    initWinSock();
    return (int)::socket(AF_INET, SOCK_STREAM, 0);
}

void XmlRpcSocket::close(int fd) {
    #if defined(_WIN32)
        closesocket(fd);
    #else
        ::close(fd);
    #endif
}

bool XmlRpcSocket::setNonBlocking(int fd) {
    #if defined(_WIN32)
        unsigned long flag = 1;
        return (ioctlsocket((SOCKET)fd, FIONBIO, &flag) == 0);
    #else
        return (fcntl(fd, F_SETFL, O_NONBLOCK) == 0);
    #endif
}

bool XmlRpcSocket::setReuseAddr(int fd) {
    int sflag = 1;
    return (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, (const char*)&sflag, sizeof(sflag)) == 0);
}

bool XmlRpcSocket::bind(int fd, int port) {
    struct sockaddr_in saddr;
    memset(&saddr, 0, sizeof(saddr));
    saddr.sin_family = AF_INET;
    saddr.sin_addr.s_addr = htonl(INADDR_ANY);
    saddr.sin_port = htons((u_short)port);
    return (::bind(fd, (struct sockaddr*)&saddr, sizeof(saddr)) == 0);
}

bool XmlRpcSocket::listen(int fd, int backlog) {
    return (::listen(fd, backlog) == 0);
}

int XmlRpcSocket::accept(int fd) {
    struct sockaddr_in addr;
    socklen_t addrlen = sizeof(addr);
    return (int)::accept(fd, (struct sockaddr*)&addr, &addrlen);
}

bool XmlRpcSocket::connect(int fd, string& host, int port) {
    struct sockaddr_in saddr;
    memset(&saddr, 0, sizeof(saddr));
    saddr.sin_family = AF_INET;

    struct hostent* hp = gethostbyname(host.c_str());
    if (hp == 0) return false;

    saddr.sin_family = hp->h_addrtype;
    memcpy(&saddr.sin_addr, hp->h_addr, hp->h_length);
    saddr.sin_port = htons((u_short)port);

    int result = ::connect(fd, (struct sockaddr*)&saddr, sizeof(saddr));
    return result == 0 || nonFatalError();
}

bool XmlRpcSocket::nbRead(int fd, string& s, bool* eof) {
    const int READ_SIZE = 4096;
    char readBuf[READ_SIZE];

    bool wouldBlock = false;
    *eof = false;

    while (!wouldBlock && !*eof) {
        #if defined(_WIN32)
            int n = recv(fd, readBuf, READ_SIZE - 1, 0);
        #else
            int n = read(fd, readBuf, READ_SIZE - 1);
        #endif

        if (n > 0) {
            readBuf[n] = 0;  // Asegurarse de que el buffer esté terminado en nulo
            s.append(readBuf, n);
        } else if (n == 0) {
            *eof = true;  // Se ha llegado al final
        } else if (nonFatalError()) {
            wouldBlock = true;  // No hay más datos en este momento
        } else {
            return false;  // Error
        }
    }
    return true;
}

bool XmlRpcSocket::nbWrite(int fd, string& s, int* bytesSoFar) {
    int nToWrite = int(s.length()) - *bytesSoFar;
    char* sp = const_cast<char*>(s.c_str()) + *bytesSoFar;
    bool wouldBlock = false;

    while (nToWrite > 0 && !wouldBlock) {
        #if defined(_WIN32)
            int n = send(fd, sp, nToWrite, 0);
        #else
            int n = write(fd, sp, nToWrite);
        #endif

        if (n > 0) {
            sp += n;
            *bytesSoFar += n;
            nToWrite -= n;
        } else if (nonFatalError()) {
            wouldBlock = true;  // No se puede escribir en este momento
        } else {
            return false;  // Error
        }
    }
    return true;
}

int XmlRpcSocket::getError() {
    #if defined(_WIN32)
        return WSAGetLastError();
    #else
        return errno;
    #endif
}

string XmlRpcSocket::getErrorMsg() {
    return getErrorMsg(getError());
}

string XmlRpcSocket::getErrorMsg(int error) {
    char err[60];
    snprintf(err, sizeof(err), "error %d", error);
    return string(err);
}

} // namespace XmlRpc
