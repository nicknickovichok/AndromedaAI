import shutil
import subprocess
import threading
import time
from collections.abc import Callable


class HydraRunner:
    """
    Hydra Bruteforce Engine for AndromedaAI.
    Executes background credential attacks with live log streaming and stop capability.
    """

    def __init__(self):
        self._process: subprocess.Popen | None = None
        self._is_running = False
        self._stop_requested = False
        self._lock = threading.Lock()

    @property
    def is_running(self) -> bool:
        return self._is_running

    def stop_attack(self) -> None:
        """Stops active Hydra attack immediately."""
        with self._lock:
            self._stop_requested = True
            if self._process and self._process.poll() is None:
                try:
                    self._process.terminate()
                    time.sleep(0.2)
                    if self._process.poll() is None:
                        self._process.kill()
                except OSError:
                    pass
            self._is_running = False

    def start_attack(
        self,
        target_host: str,
        port: int,
        service: str,
        username: str = "admin",
        wordlist: str = "fast_top100.txt",
        threads: int = 16,
        log_callback: Callable[[str], None] | None = None,
        done_callback: Callable[[str], None] | None = None,
    ) -> None:
        """Starts Hydra attack in background thread."""
        with self._lock:
            if self._is_running:
                if log_callback:
                    log_callback("[!] Ошибка: Атака брутфорса уже выполняется. Остановите текущую атаку перед запуском новой.\n")
                return
            self._is_running = True
            self._stop_requested = False

        def worker():
            target = target_host.strip()
            svc = service.lower().strip()
            user = username.strip() or "admin"
            wlist = wordlist.strip() or "fast_top100.txt"

            def send_log(msg: str):
                if log_callback:
                    log_callback(msg)

            send_log(f"[+] Инициализация брутфорса Hydra для {svc.upper()} ({target}:{port})...\n")
            send_log(f"[+] Параметры: Пользователь='{user}', Словарь='{wlist}', Потоков={threads}\n")

            hydra_bin = shutil.which("hydra")

            if not hydra_bin:
                send_log("[!] Внимание: Бинарник 'hydra' не найден в PATH. Запущен симулятор атаки.\n\n")
                simulated_passwords = [
                    "123456", "password", "admin", "admin123", "root",
                    "toor", "pass123", "letmein", "welcome", "qwerty"
                ]
                total = len(simulated_passwords)
                found = False

                for idx, pwd in enumerate(simulated_passwords, start=1):
                    if self._stop_requested:
                        send_log("\n[🛑] АТАКА БРУТФОРСА ОСТАНОВЛЕНА ПОЛЬЗОВАТЕЛЕМ.\n")
                        if done_callback:
                            done_callback("Остановлено пользователем")
                        with self._lock:
                            self._is_running = False
                        return

                    percent = int((idx / total) * 100)
                    send_log(f"[{percent:3d}%] [{idx}/{total}] Тестирование пары: {user}:{pwd} ...\n")
                    time.sleep(0.5)

                    if pwd in ("admin123", "password"):
                        send_log("\n🎉 [УСПЕХ] ВАЛИДНЫЕ УЧЕТНЫЕ ДАННЫЕ НАЙДЕНЫ!\n")
                        send_log(f"🔑 Хост: {target}:{port} | Логин: {user} | Пароль: {pwd}\n")
                        found = True
                        if done_callback:
                            done_callback(f"Найдено: {user}:{pwd}")
                        break

                if not found and not self._stop_requested:
                    send_log("\n[-] Завершено: Валидные пароли в указанном словаре не найдены.\n")
                    if done_callback:
                        done_callback("Пароль не найден")

                with self._lock:
                    self._is_running = False
                return

            # Real Hydra process execution
            cmd = [
                hydra_bin,
                "-l", user,
                "-P", wlist,
                "-t", str(threads),
                "-s", str(port),
                "-vV",
                target,
                svc,
            ]

            send_log(f"[+] Выполнение команды: {' '.join(cmd)}\n\n")

            try:
                self._process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )

                if self._process.stdout:
                    for line in iter(self._process.stdout.readline, ""):
                        if self._stop_requested:
                            send_log("\n[🛑] АТАКА БРУТФОРСА ОСТАНОВЛЕНА ПОЛЬЗОВАТЕЛЕМ.\n")
                            if done_callback:
                                done_callback("Остановлено пользователем")
                            break
                        send_log(line)

                self._process.wait()
                if not self._stop_requested and done_callback:
                    done_callback("Завершено")
            except (OSError, RuntimeError) as e:
                send_log(f"\n[!] Ошибка выполнения Hydra: {e!s}\n")
                if done_callback:
                    done_callback(f"Ошибка: {e!s}")
            finally:
                with self._lock:
                    self._is_running = False

        threading.Thread(target=worker, daemon=True).start()
