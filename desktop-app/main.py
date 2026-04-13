"""
Main application entry point for LLM Bridge Desktop Application
"""
import flet as ft
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import config
from database.db import init_db, close_db, db
from services.ipc import start_api_server, stop_api_server, is_api_server_running, get_api_url
from utils.encryption import encrypt_token, decrypt_token
from ui.login import create_login_page
from ui.dashboard import DashboardScreen


class LLMBridgeApp:
    """Main application class"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "LLM Bridge"
        self.page.window.width = 900
        self.page.window.height = 700
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.accounts = []
        self.api_keys = []
        self.dashboard = None
        self.dashboard_view = None
        self.server_status_task = None
        
        # Initialize database and UI
        asyncio.create_task(self._init())
    
    async def _init(self):
        """Initialize application"""
        await init_db()
        await self._load_data()
        self._show_login()
    
    async def _load_data(self):
        """Load accounts and API keys from database"""
        self.accounts = await db.get_all_accounts()
        self.api_keys = await db.get_all_api_keys()
        
        # Decrypt session tokens for display
        for account in self.accounts:
            if account.get('session_token'):
                account['session_token'] = decrypt_token(account['session_token'])
    
    def _show_login(self):
        """Show login screen"""
        self._cancel_server_status_task()
        self.dashboard = None
        self.dashboard_view = None
        self.page.controls.clear()
        self.page.add(create_login_page(
            self.page,
            self.on_login_success,
            self.switch_to_dashboard
        ))
        self.page.update()
    
    def switch_to_dashboard(self):
        """Switch to dashboard view"""
        self._cancel_server_status_task()
        self.page.controls.clear()
        self.dashboard = DashboardScreen(
            self.accounts,
            self.api_keys,
            self.refresh_data,
            self._show_login
        )
        self.dashboard_view = ft.Container(
            content=ft.Container(
                content=self.dashboard,
                padding=30,
                expand=True,
            ),
            bgcolor=ft.Colors.GREY_100,
            expand=True,
        )
        self.page.add(self.dashboard_view)
        self.page.update()
        self.dashboard.update_data(self.accounts, self.api_keys)
        
        # Check server status
        asyncio.create_task(self.dashboard.check_server_status())
        self.server_status_task = asyncio.create_task(self._auto_refresh_server_status())
    
    async def on_login_success(self, provider: str, result: dict):
        """Handle successful login"""
        # Encrypt the session token before storing
        encrypted_token = encrypt_token(result['session_token'])
        
        # Create account in database
        account_id = await db.create_account(
            provider=provider,
            email=result.get('email'),
            session_token=encrypted_token,
            refresh_token=result.get('refresh_token'),
        )
        
        # Sync to API server
        if is_api_server_running():
            await ipc.sync_account_to_api({
                'id': account_id,
                'provider': provider,
                'email': result.get('email'),
                'session_token': result['session_token'],
            })
        
        # Reload data
        await self._load_data()
    
    async def refresh_data(self):
        """Refresh accounts and API keys data"""
        await self._load_data()
        if self.dashboard:
            self.dashboard.update_data(self.accounts, self.api_keys)
    
    async def _auto_refresh_server_status(self):
        """Auto-refresh server status periodically"""
        while True:
            await asyncio.sleep(5)
            if self.dashboard:
                await self.dashboard.check_server_status()

    def _cancel_server_status_task(self):
        """Cancel the dashboard auto-refresh task if it exists."""
        if self.server_status_task and not self.server_status_task.done():
            self.server_status_task.cancel()
        self.server_status_task = None


async def main(page: ft.Page):
    """Main entry point"""
    app = LLMBridgeApp(page)


if __name__ == "__main__":
    # Import ipc after db is set up
    from services import ipc
    
    ft.run(main)
