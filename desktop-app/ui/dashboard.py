"""
Dashboard UI for LLM Bridge desktop application
Shows account list, API keys, quota status, and server controls
"""
import flet as ft
from services.ipc import ipc, start_api_server, stop_api_server, is_api_server_running, get_api_url

class DashboardScreen(ft.Column):
    def __init__(self, accounts, api_keys, on_refresh, on_switch_to_login):
        super().__init__()
        self.accounts = accounts
        self.api_keys = api_keys
        self.on_refresh = on_refresh
        self.on_switch_to_login = on_switch_to_login
        self.spacing = 20
        self.scroll = ft.ScrollMode.AUTO
        self._build_ui()
    
    def _build_ui(self):
        # Header
        header = ft.Container(
            content=ft.Row([
                ft.Text("Dashboard", size=30, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    on_click=lambda e: self.on_refresh(),
                    tooltip="Refresh",
                ),
            ], alignment=ft.MainAxisAlignment.START),
            margin=ft.margin.only(bottom=20),
        )
        
        # Server status card
        server_card = self._build_server_card()
        
        # Accounts section
        accounts_section = self._build_accounts_section()
        
        # API Keys section
        api_keys_section = self._build_api_keys_section()
        
        self.controls = [
            header,
            server_card,
            accounts_section,
            api_keys_section,
        ]
    
    def _build_server_card(self):
        self.server_status = ft.Text("Checking...", size=16)
        self.server_url_text = ft.Text("", size=14, color=ft.Colors.GREY_600)
        
        return ft.Container(
            content=ft.Column([
                ft.Text("API Server", size=20, weight=ft.FontWeight.W_500),
                ft.Row([
                    ft.Text("Status: "),
                    self.server_status,
                ]),
                self.server_url_text,
                ft.Row([
                    ft.ElevatedButton(
                        "Start Server",
                        icon=ft.Icons.PLAY_ARROW,
                        on_click=self._start_server,
                    ),
                    ft.ElevatedButton(
                        "Stop Server",
                        icon=ft.Icons.STOP,
                        on_click=self._stop_server,
                    ),
                ], spacing=10),
            ], spacing=10),
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=10,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.Colors.GREY_300),
        )
    
    def _build_accounts_section(self):
        self.accounts_list = ft.Column(spacing=10)
        
        add_account_btn = ft.ElevatedButton(
            "Add Account",
            icon=ft.Icons.ADD,
            on_click=lambda e: self.on_switch_to_login(),
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Accounts", size=20, weight=ft.FontWeight.W_500),
                    add_account_btn,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.accounts_list,
            ], spacing=10),
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=10,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.Colors.GREY_300),
        )
    
    def _build_api_keys_section(self):
        self.api_keys_list = ft.Column(spacing=10)
        
        return ft.Container(
            content=ft.Column([
                ft.Text("API Keys", size=20, weight=ft.FontWeight.W_500),
                self.api_keys_list,
            ], spacing=10),
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=10,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.Colors.GREY_300),
        )
    
    async def _start_server(self, e):
        try:
            self.server_status.value = "Starting..."
            self.server_status.color = ft.Colors.BLUE
            self.update()
            
            await start_api_server()
            
            self.server_status.value = "Running"
            self.server_status.color = ft.Colors.GREEN
            self.server_url_text.value = f"URL: {get_api_url()}"
        except Exception as ex:
            self.server_status.value = f"Error: {str(ex)}"
            self.server_status.color = ft.Colors.RED
        self.update()
    
    async def _stop_server(self, e):
        try:
            await stop_api_server()
            self.server_status.value = "Stopped"
            self.server_status.color = ft.Colors.GREY
            self.server_url_text.value = ""
        except Exception as ex:
            self.server_status.value = f"Error: {str(ex)}"
            self.server_status.color = ft.Colors.RED
        self.update()
    
    def update_data(self, accounts, api_keys):
        """Update accounts and API keys data"""
        self.accounts = accounts
        self.api_keys = api_keys
        self._update_lists()
    
    def _update_lists(self):
        # Update accounts list
        self.accounts_list.controls.clear()
        
        if not self.accounts:
            self.accounts_list.controls.append(
                ft.Text("No accounts connected", color=ft.Colors.GREY_600)
            )
        else:
            for account in self.accounts:
                # Build quota warning if needed
                quota_warning = ""
                if account.get('messages_used', 0) >= 32:
                    quota_warning = " ⚠️ Low quota"
                
                self.accounts_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(
                                ft.Icons.ACCOUNT_CIRCLE,
                                size=40,
                            ),
                            ft.Column([
                                ft.Text(f"{account.get('email', 'Unknown')}", weight=ft.FontWeight.W_500),
                                ft.Text(f"Provider: {account.get('provider', 'Unknown')}{quota_warning}", 
                                       size=12, color=ft.Colors.GREY_600),
                            ], spacing=2),
                        ], spacing=10),
                        bgcolor=ft.Colors.GREY_100,
                        padding=10,
                        border_radius=8,
                    )
                )
        
        # Update API keys list
        self.api_keys_list.controls.clear()
        
        if not self.api_keys:
            self.api_keys_list.controls.append(
                ft.Text("No API keys generated", color=ft.Colors.GREY_600)
            )
        else:
            for key_data in self.api_keys:
                self.api_keys_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.KEY, size=40),
                            ft.Column([
                                ft.Text(f"Key: {key_data.get('key', '')}", weight=ft.FontWeight.W_500),
                                ft.Text(f"Account: {key_data.get('email', 'Unknown')}", 
                                       size=12, color=ft.Colors.GREY_600),
                            ], spacing=2),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.Icons.COPY,
                                on_click=lambda e, k=key_data['key']: self._copy_key(k),
                                tooltip="Copy to clipboard",
                            ),
                        ], spacing=10),
                        bgcolor=ft.Colors.GREY_100,
                        padding=10,
                        border_radius=8,
                    )
                )
        
        self.update()
    
    def _copy_key(self, key):
        # This will be handled by the page
        pass
    
    async def check_server_status(self):
        """Check and update server status"""
        if is_api_server_running():
            self.server_status.value = "Running"
            self.server_status.color = ft.Colors.GREEN
            self.server_url_text.value = f"URL: {get_api_url()}"
        else:
            self.server_status.value = "Stopped"
            self.server_status.color = ft.Colors.GREY
            self.server_url_text.value = ""
        self.update()


def create_dashboard_page(dashboard: DashboardScreen):
    """Wrap the dashboard screen in the page container styling."""
    return ft.Container(
        content=ft.Container(
            content=dashboard,
            padding=30,
            expand=True,
        ),
        bgcolor=ft.Colors.GREY_100,
        expand=True,
    )
