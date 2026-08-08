import threading
# pyrefly: ignore [missing-import]
import flet as ft
from db.database import DatabaseManager
from core.anonymizer import NetworkAnonymizer
from core.recon_scanner import ReconScanner

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
    page.window.width = 1200
    page.window.height = 850
    page.window.min_width = 950
    page.window.min_height = 650

    # Initialize Services
    db = DatabaseManager()
    anonymizer = NetworkAnonymizer()
    scanner = ReconScanner()

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
                # System Status Badges
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Container(width=8, height=8, border_radius=4, bgcolor=COLOR_GREEN),
                                    ft.Text("DB: ONLINE", size=11, color=COLOR_TEXT, weight=ft.FontWeight.BOLD),
                                ],
                                spacing=6,
                            ),
                            padding=ft.Padding(10, 5, 10, 5),
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
                            padding=ft.Padding(10, 5, 10, 5),
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
                            padding=ft.Padding(10, 5, 10, 5),
                            border_radius=8,
                            bgcolor="#250D1C",
                            border=ft.Border.all(1, COLOR_PINK),
                        ),
                    ],
                    spacing=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=15,
        border_radius=10,
        bgcolor=COLOR_PANEL,
        border=ft.Border.all(1, COLOR_PANEL_BORDER),
    )

    # ==========================================
    # TAB 1: DASHBOARD (NETWORK & TARGET CONTROL)
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
            except Exception as ex:
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

    # Targets list ui element
    targets_list_column = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO)

    def refresh_targets():
        targets_list_column.controls.clear()
        try:
            targets = db.get_all_targets()
            if not targets:
                targets_list_column.controls.append(ft.Text("Целей пока нет", color=COLOR_SUBTEXT, size=12))
            for t in targets:
                targets_list_column.controls.append(
                    ft.Text(f"• {t}", color=COLOR_TEXT, size=13)
                )
        except Exception:
            targets_list_column.controls.append(ft.Text("Не удалось загрузить список", color=COLOR_PINK, size=12))

        # Also update Recon Dropdown options
        refresh_recon_dropdown()
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
                ft.Text("Текущие цели в расследовании:", size=12, color=COLOR_SUBTEXT, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=targets_list_column,
                    height=150,
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
    # TAB 2: RECONNAISSANCE MODULE (NMAP & AI)
    # ==========================================
    recon_target_dropdown = ft.Dropdown(
        label="Выберите цель для сканирования",
        hint_text="Загрузка целей...",
        border_color=COLOR_CYAN,
        focused_border_color=COLOR_CYAN,
        label_style=ft.TextStyle(color=COLOR_CYAN),
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

    nmap_progress = ft.ProgressRing(width=16, height=16, stroke_width=2, color=COLOR_BG, visible=False)

    terminal_logs_tf = ft.TextField(
        multiline=True,
        read_only=True,
        min_lines=12,
        max_lines=16,
        value="[SYSTEM] Терминал Nmap готов к работе. Выберите цель и нажмите 'Запустить сканирование'.\n",
        bgcolor="#050811",
        border_color=COLOR_CYAN,
        focused_border_color=COLOR_CYAN,
        text_style=ft.TextStyle(font_family="monospace", color=COLOR_GREEN, size=12),
        expand=True,
    )

    ai_analysis_text = ft.Text(
        "Ожидание результатов сканирования для анализа микро-шагов...",
        size=12,
        color=COLOR_SUBTEXT,
    )

    ai_analysis_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, color=COLOR_CYAN, size=20),
                        ft.Text("Анализ ИИ (Микро-шаг)", size=14, weight=ft.FontWeight.BOLD, color=COLOR_CYAN),
                    ],
                    spacing=8,
                ),
                ft.Divider(color=COLOR_PANEL_BORDER, height=1),
                ai_analysis_text,
            ],
            spacing=8,
        ),
        padding=15,
        border_radius=10,
        bgcolor="#0C1424",
        border=ft.Border.all(1, COLOR_CYAN),
    )

    def on_run_nmap_click(e):
        target = recon_target_dropdown.value
        if not target:
            show_snackbar("Выберите цель для сканирования!", is_error=True)
            return

        use_proxy = recon_proxy_switch.value
        nmap_progress.visible = True
        run_scan_btn.disabled = True
        terminal_logs_tf.value = f"[+] Запуск сканирования Nmap для цели: {target} (Proxychains: {use_proxy})...\nПожалуйста, подождите...\n"
        ai_analysis_text.value = "⏳ ИИ анализирует порты и формирует микро-шаг..."
        page.update()

        def background_scan():
            raw_output = scanner.run_nmap_scan(target, use_proxychains=use_proxy)
            terminal_logs_tf.value = raw_output

            ai_res = scanner.analyze_ports(raw_output)
            ai_analysis_text.value = ai_res

            # Save step log in DB
            db.save_ai_log(
                step_name=f"NmapScan_{target}",
                raw_input=f"nmap -sV -F {target} (proxy={use_proxy})",
                ai_output=ai_res
            )

            nmap_progress.visible = False
            run_scan_btn.disabled = False
            page.update()
            show_snackbar(f"✅ Сканирование цели {target} завершено")

        threading.Thread(target=background_scan, daemon=True).start()

    run_scan_btn = ft.Button(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color=COLOR_BG, size=18),
                ft.Text("Запустить сканирование Nmap", color=COLOR_BG, weight=ft.FontWeight.BOLD),
                nmap_progress,
            ],
            spacing=8,
        ),
        bgcolor=COLOR_CYAN,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=on_run_nmap_click,
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
                        ft.Text("ТЕРМИНАЛ NMAP ЛОГОВ", size=13, weight=ft.FontWeight.BOLD, color=COLOR_GREEN),
                        terminal_logs_tf,
                    ],
                    spacing=8,
                ),
                padding=15,
                bgcolor=COLOR_PANEL,
                border_radius=10,
                border=ft.Border.all(1, COLOR_PANEL_BORDER),
            ),
            ai_analysis_card,
        ],
        spacing=15,
        scroll=ft.ScrollMode.AUTO,
    )

    # ==========================================
    # TABS 3 & 4 PLACEHOLDERS
    # ==========================================
    views = [
        dashboard_view,
        recon_view,
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.PASSWORD_ROUNDED, size=48, color=COLOR_PINK),
                    ft.Text("МОДУЛЬ АВТОМАТИЗИРОВАННОГО БРУТФОРСА", size=18, weight=ft.FontWeight.BOLD, color=COLOR_PINK),
                    ft.Text("Интерактивная Hydra через Tor прокси-цепочки", color=COLOR_SUBTEXT, size=13),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=30,
            bgcolor=COLOR_PANEL,
            border_radius=10,
            border=ft.Border.all(1, COLOR_PANEL_BORDER),
        ),
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.TERMINAL_ROUNDED, size=48, color=COLOR_GREEN),
                    ft.Text("МОДУЛЬ ЭКСПЛОИТАЦИИ И ВАЛИДАЦИИ", size=18, weight=ft.FontWeight.BOLD, color=COLOR_GREEN),
                    ft.Text("Searchsploit & Пошаговые сценарии в SQLite", color=COLOR_SUBTEXT, size=13),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=30,
            bgcolor=COLOR_PANEL,
            border_radius=10,
            border=ft.Border.all(1, COLOR_PANEL_BORDER),
        ),
    ]

    content_area = ft.Container(content=views[0], expand=True)

    def on_tab_click(e):
        try:
            idx = int(e.data)
            if 0 <= idx < len(views):
                content_area.content = views[idx]
                page.update()
        except Exception:
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

    # Tabs control wrapping tab_bar and views in ft.Tabs and ft.Container
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

    # Wrap tabs_control in ft.Container(expand=True)
    tabs_container = ft.Container(
        content=tabs_control,
        expand=True,
    )

    # Assemble Layout
    page.add(header, tabs_container)
    refresh_targets()


if __name__ == "__main__":
    ft.run(main)
