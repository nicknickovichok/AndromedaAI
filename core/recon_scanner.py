import re
import shutil
import subprocess


class ReconScanner:
    """
    Reconnaissance Scanner for AndromedaAI.
    Executes Nmap, Nikto, and Gobuster scans (with optional Proxychains wrapper
    and custom flags) and performs AI micro-step port analysis.
    """

    def __init__(self):
        pass

    def run_nmap_scan(self, target_host: str, use_proxychains: bool = False, custom_args: str = "") -> str:
        """
        Executes Nmap scan against target_host with optional custom args.
        Wraps in proxychains4 if use_proxychains is True.
        """
        target_host = target_host.strip()
        if not target_host:
            return "[!] Error: No target host provided."

        nmap_path = shutil.which("nmap")
        if not nmap_path:
            extra = f" (Опции: {custom_args})" if custom_args else ""
            return (
                f"[!] Nmap execution simulated for target: {target_host}{extra}\n"
                "[!] Note: 'nmap' binary was not found in system PATH.\n\n"
                f"Starting Nmap 7.94 ( https://nmap.org ) at 2026-08-09 10:35\n"
                f"Nmap scan report for {target_host}\n"
                "Host is up (0.012s latency).\n"
                "Not shown: 98 closed tcp ports (reset)\n"
                "PORT   STATE SERVICE VERSION\n"
                "22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5\n"
                "80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))\n"
                "443/tcp open ssl/http Apache httpd 2.4.41 ((Ubuntu))\n"
                "3306/tcp open mysql   MySQL 8.0.25\n"
                "Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .\n"
                "Nmap done: 1 IP address (1 host up) scanned in 2.15 seconds"
            )

        cmd_parts = []
        if use_proxychains:
            proxychains_bin = shutil.which("proxychains4") or shutil.which("proxychains")
            if proxychains_bin:
                cmd_parts.extend([proxychains_bin, "-q"])
            else:
                return "[!] Error: 'proxychains' binary not found on host system."

        cmd_parts.append(nmap_path)
        if custom_args.strip():
            cmd_parts.extend(custom_args.strip().split())
        else:
            cmd_parts.extend(["-sV", "-F"])
        cmd_parts.append(target_host)

        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=180,
                check=False
            )
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr
            return output.strip() if output.strip() else "[!] Nmap returned empty output."
        except subprocess.TimeoutExpired:
            return f"[!] Error: Nmap scan timed out for target '{target_host}' (180s limit)."
        except (OSError, RuntimeError) as e:
            return f"[!] Error executing Nmap scan: {e!s}"

    def run_nikto_scan(self, target_host: str, use_proxychains: bool = False, custom_args: str = "") -> str:
        """
        Executes Nikto Web Vulnerability Scanner against target_host.
        """
        target_host = target_host.strip()
        if not target_host:
            return "[!] Error: No target host provided for Nikto scan."

        nikto_path = shutil.which("nikto")
        if not nikto_path:
            extra = f" (Опции: {custom_args})" if custom_args else ""
            return (
                f"[!] Nikto execution simulated for target: {target_host}{extra}\n"
                "[!] Note: 'nikto' binary was not found in system PATH.\n\n"
                f"- Nikto v2.5.0\n"
                f"+ Target IP: {target_host}\n"
                f"+ Target Hostname: {target_host}\n"
                f"+ Target Port: 80\n"
                f"+ Server: Apache/2.4.41 (Ubuntu)\n"
                f"+ [CVE-2021-41773] The X-Frame-Options header is not set in HTTP response.\n"
                f"+ [SECURITY] Anti-clickjacking X-Frame-Options header is missing.\n"
                f"+ [INFO] Allowed HTTP Methods: GET, HEAD, POST, OPTIONS\n"
                f"+ [INFO] OSVDB-3092: /admin/: Admin directory found with potential weak access.\n"
                f"+ [INFO] OSVDB-3268: /config.php: Configuration script exposes database parameters.\n"
                f"+ 7654 requests made, 0 error(s) and 4 item(s) reported on remote host"
            )

        cmd_parts = []
        if use_proxychains:
            proxychains_bin = shutil.which("proxychains4") or shutil.which("proxychains")
            if proxychains_bin:
                cmd_parts.extend([proxychains_bin, "-q"])

        cmd_parts.extend([nikto_path, "-h", target_host])
        if custom_args.strip():
            cmd_parts.extend(custom_args.strip().split())
        else:
            cmd_parts.extend(["-Tuning", "123b"])

        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=180,
                check=False
            )
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr
            return output.strip() if output.strip() else "[!] Nikto returned empty output."
        except subprocess.TimeoutExpired:
            return f"[!] Error: Nikto scan timed out for target '{target_host}' (180s limit)."
        except (OSError, RuntimeError) as e:
            return f"[!] Error executing Nikto scan: {e!s}"

    def run_gobuster_scan(self, target_host: str, use_proxychains: bool = False, custom_args: str = "") -> str:
        """
        Executes Gobuster directory brute-force scan against target_host.
        """
        target_host = target_host.strip()
        if not target_host:
            return "[!] Error: No target host provided for Gobuster scan."

        url = target_host if target_host.startswith("http") else f"http://{target_host}"
        gobuster_path = shutil.which("gobuster")

        if not gobuster_path:
            extra = f" (Опции: {custom_args})" if custom_args else ""
            return (
                f"[!] Gobuster execution simulated for target: {url}{extra}\n"
                "[!] Note: 'gobuster' binary was not found in system PATH.\n\n"
                f"===============================================================\n"
                f"Gobuster v3.6\n"
                f"by OJ Reeves (@TheAnigma) & Christian Mehlmauer (@firefart)\n"
                f"===============================================================\n"
                f"[+] Url:                     {url}\n"
                f"[+] Method:                  GET\n"
                f"[+] Threads:                 10\n"
                f"[+] Wordlist:                top100_common.txt\n"
                f"===============================================================\n"
                f"/admin                (Status: 301) [Size: 312] [--> {url}/admin/]\n"
                f"/login                (Status: 200) [Size: 1420]\n"
                f"/api                  (Status: 200) [Size: 840]\n"
                f"/config.json          (Status: 200) [Size: 512]\n"
                f"/uploads              (Status: 403) [Size: 278]\n"
                f"===============================================================\n"
                f"Finished"
            )

        cmd_parts = []
        if use_proxychains:
            proxychains_bin = shutil.which("proxychains4") or shutil.which("proxychains")
            if proxychains_bin:
                cmd_parts.extend([proxychains_bin, "-q"])

        cmd_parts.extend([gobuster_path, "dir", "-u", url])
        if custom_args.strip():
            cmd_parts.extend(custom_args.strip().split())
        else:
            cmd_parts.extend(["-w", "/usr/share/wordlists/dirb/common.txt", "-q"])

        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=120,
                check=False
            )
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr
            return output.strip() if output.strip() else "[!] Gobuster returned empty output."
        except subprocess.TimeoutExpired:
            return f"[!] Error: Gobuster scan timed out for target '{url}' (120s limit)."
        except (OSError, RuntimeError) as e:
            return f"[!] Error executing Gobuster scan: {e!s}"

    def analyze_ports(self, raw_nmap_output: str) -> str:
        """
        Parses raw Nmap output, identifies open ports/services,
        and generates an AI Micro-step assessment.
        """
        if not raw_nmap_output or ("[!]" in raw_nmap_output and "Nmap scan report" not in raw_nmap_output):
            return "ИИ Анализ: Сканирование не дало доступных результатов для обработки."

        lines = raw_nmap_output.splitlines()
        open_ports: list[str] = []

        port_pattern = re.compile(r"^\d+/(tcp|udp)\s+open\s+.*")

        for line in lines:
            line_clean = line.strip()
            if port_pattern.match(line_clean) or ("/tcp" in line_clean and "open" in line_clean):
                open_ports.append(line_clean)

        if not open_ports:
            return (
                "🤖 [ИИ МИКРО-ШАГ АНАЛИЗ]\n"
                "├─ Статус: Открытых портов не обнаружено (Все порты фильтруются или закрыты).\n"
                "└─ Рекомендация: Выполнить более глубокий SYN scan (-sS -p-) или прошерстить UDP порты."
            )

        analysis = "🤖 [ИИ МИКРО-ШАГ АНАЛИЗ РАЗВЕДКИ]\n"
        analysis += f"├─ Обнаружено открытых сервисов: {len(open_ports)}\n"
        for p in open_ports:
            analysis += f"│  • {p}\n"
        analysis += "├─ Оценка векторов атаки:\n"

        has_http = any("http" in p.lower() or "web" in p.lower() or "80" in p or "443" in p for p in open_ports)
        has_ssh = any("ssh" in p.lower() or "22" in p for p in open_ports)
        has_ftp = any("ftp" in p.lower() or "21" in p for p in open_ports)

        if has_http:
            analysis += "│  [+] WEB Вектор: Рекомендуется запустить Nikto / Gobuster фаззинг и искать CVE административных панелей.\n"
        if has_ssh:
            analysis += "│  [+] SSH Вектор: Проверить версию на известные уязвимости и передать хост в модуль 'Брутфорс'.\n"
        if has_ftp:
            analysis += "│  [+] FTP Вектор: Проверить возможность анонимного входа (anonymous login) и слабые учетные данные.\n"

        analysis += "└─ Следующий рекомендуемый микро-шаг: Передать найденные версии в модуль 'Эксплоиты'."
        return analysis
