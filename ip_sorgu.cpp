#include <iostream>
#include <curl/curl.h>
#include <string>

using namespace std;

#define CYAN "\033[36m"
#define GREEN "\033[32m"
#define YELLOW "\033[33m"
#define RESET "\033[0m"

string response;

size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    response.append((char*)contents, size * nmemb);
    return size * nmemb;
}

void banner() {
    cout << CYAN;
    cout << "IP SORGU TOOL\n";
    cout << "Telegram: @zeldyhackteam\n";
    cout << RESET << "\n";
}

int main() {
    banner();

    string ip;
    cout << YELLOW << "IP gir: " << RESET;
    cin >> ip;

    string url = "http://ip-api.com/json/" + ip;

    CURL* curl = curl_easy_init();

    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_perform(curl);
        curl_easy_cleanup(curl);
    }

    cout << GREEN << "\nSONUC:\n" << RESET;
    cout << response << "\n";

    return 0;
}
