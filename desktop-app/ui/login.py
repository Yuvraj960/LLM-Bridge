"""
Login screen UI for LLM Bridge desktop application
Allows users to log in to ChatGPT or Claude via browser-based OAuth
"""
import flet as ft
from services.auth import login_chatgpt_headful, login_claude_headful


class LoginScreen(ft.Column):
    def __init__(self, on_login_success, switch_to_dashboard):
        self.on_login_success = on_login_success
        self.switch_to_dashboard = switch_to_dashboard
        self.is_logging_in = False
        self.status_text = ft.Text("", size=14, color=ft.Colors.RED)
        
        super().__init__(
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self._build_ui()

    def _safe_update(self):
        """Update the control only while it is still attached to the page."""
        try:
            self.update()
        except RuntimeError:
            pass
    
    def _build_ui(self):
        self.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "LLM Bridge",
                        size=40,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Connect your ChatGPT or Claude account",
                        size=16,
                        color=ft.Colors.GREY_700,
                    ),
                ], spacing=5, alignment=ft.MainAxisAlignment.CENTER),
                alignment=ft.Alignment.CENTER,
                margin=ft.margin.only(bottom=40),
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "ChatGPT",
                        size=20,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Text(
                        "Log in with your free ChatGPT account",
                        size=14,
                        color=ft.Colors.GREY_600,
                    ),
                    ft.ElevatedButton(
                        "Login with ChatGPT",
                        icon=ft.Icons.LOGIN,
                        on_click=self._handle_chatgpt_login,
                    ),
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=ft.Colors.WHITE,
                padding=30,
                border_radius=15,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=10,
                    color=ft.Colors.GREY_300,
                ),
                width=350,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Claude",
                        size=20,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Text(
                        "Log in with your free Claude account",
                        size=14,
                        color=ft.Colors.GREY_600,
                    ),
                    ft.ElevatedButton(
                        "Login with Claude",
                        icon=ft.Icons.LOGIN,
                        on_click=self._handle_claude_login,
                    ),
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=ft.Colors.WHITE,
                padding=30,
                border_radius=15,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=10,
                    color=ft.Colors.GREY_300,
                ),
                width=350,
            ),
            self.status_text,
        ]
    
    async def _handle_chatgpt_login(self, e):
        """Handle ChatGPT login button click"""
        await self._perform_login('chatgpt')
    
    async def _handle_claude_login(self, e):
        """Handle Claude login button click"""
        await self._perform_login('claude')
    
    async def _perform_login(self, provider):
        """Perform login for the specified provider"""
        switched_to_dashboard = False
        self.is_logging_in = True
        self.status_text.value = f"Opening {provider} login page..."
        self.status_text.color = ft.Colors.BLUE
        self._safe_update()
        
        try:
            waiting_name = "ChatGPT" if provider == "chatgpt" else "Claude"
            self.status_text.value = (
                f"Browser opened. Complete {waiting_name} login and any security verification there..."
            )
            self.status_text.color = ft.Colors.BLUE
            self._safe_update()

            if provider == 'chatgpt':
                result = await login_chatgpt_headful()
            else:
                result = await login_claude_headful()
            
            self.status_text.value = "Login successful!"
            self.status_text.color = ft.Colors.GREEN
            self._safe_update()
            
            # Notify parent of successful login
            await self.on_login_success(provider, result)
            
            # Switch to dashboard
            self.switch_to_dashboard()
            switched_to_dashboard = True
            
        except Exception as ex:
            self.status_text.value = f"Login failed: {str(ex)}"
            self.status_text.color = ft.Colors.RED
            self._safe_update()
        finally:
            self.is_logging_in = False
            if not switched_to_dashboard:
                self._safe_update()


def create_login_page(page: ft.Page, on_login_success, switch_to_dashboard):
    """Create the login page"""
    return ft.Container(
        content=LoginScreen(on_login_success, switch_to_dashboard),
        alignment=ft.Alignment.CENTER,
        expand=True,
        bgcolor=ft.Colors.GREY_100,
    )
