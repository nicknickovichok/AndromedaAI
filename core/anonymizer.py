import socket
import requests

class NetworkAnonymizer:
    """
    Network Anonymizer service for AndromedaAI.
    Provides direct IP lookup, SOCKS5 proxy IP verification (Tor),
    and Tor circuit rotation via Control Port 9051.
    """

    def __init__(self, socks_proxy: str = "socks5://127.0.0.1:9050", control_port: int = 9051):
        self.socks_proxy = socks_proxy
        self.control_port = control_port

    def check_current_ip(self) -> str:
        """
        Makes standard HTTP request to https://api.ipify.org without proxy.
        Returns real IP address string or 'Ошибка сети' on failure.
        """
        try:
            resp = requests.get("https://api.ipify.org?format=json", timeout=5)
            if resp.status_code == 200:
                return resp.json().get("ip", resp.text.strip())
            resp = requests.get("https://api.ipify.org", timeout=5)
            if resp.status_code == 200:
                return resp.text.strip()
        except Exception:
            pass
        return "Ошибка сети"

    def check_proxy_ip(self) -> str:
        """
        Makes HTTP request to https://api.ipify.org through local Tor SOCKS5 proxy (socks5://127.0.0.1:9050).
        Returns proxy-IP string if Tor is running, or 'Error: Tor Offline' on error/timeout.
        """
        proxies = {
            "http": "socks5h://127.0.0.1:9050",
            "https": "socks5h://127.0.0.1:9050"
        }
        try:
            resp = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=5)
            if resp.status_code == 200:
                return resp.json().get("ip", resp.text.strip())
            resp = requests.get("https://api.ipify.org", proxies=proxies, timeout=5)
            if resp.status_code == 200:
                return resp.text.strip()
        except Exception:
            pass

        # Fallback to standard socks5:// proxy format
        try:
            proxies_direct = {
                "http": "socks5://127.0.0.1:9050",
                "https": "socks5://127.0.0.1:9050"
            }
            resp = requests.get("https://api.ipify.org?format=json", proxies=proxies_direct, timeout=5)
            if resp.status_code == 200:
                return resp.json().get("ip", resp.text.strip())
        except Exception:
            pass

        return "Error: Tor Offline"

    def rotate_tor_ip(self) -> bool:
        """
        Attempts to send IP rotation signal to Tor Control Port (127.0.0.1:9051).
        Opens socket to 9051, sends 'AUTHENTICATE ""\r\n' and 'SIGNAL NEWNYM\r\n'.
        Returns True on success, or False if port is closed/failed without crashing.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3.0)
                s.connect(("127.0.0.1", self.control_port))
                s.sendall(b'AUTHENTICATE ""\r\n')
                auth_resp = s.recv(1024).decode('utf-8', errors='ignore')

                if "250" in auth_resp:
                    s.sendall(b"SIGNAL NEWNYM\r\n")
                    signal_resp = s.recv(1024).decode('utf-8', errors='ignore')
                    return "250" in signal_resp
                return False
        except Exception:
            return False
