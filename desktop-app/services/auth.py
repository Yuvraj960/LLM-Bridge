"""
Authentication service using Playwright for OAuth login
Handles login to ChatGPT and Claude web interfaces to extract session tokens
"""
import asyncio
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

class AuthService:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    async def init_browser(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
    
    async def close_browser(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def _click_if_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Click a selector if it becomes visible within timeout."""
        try:
            await self.page.locator(selector).first.wait_for(state="visible", timeout=timeout)
            await self.page.locator(selector).first.click()
            return True
        except PlaywrightTimeoutError:
            return False

    async def _get_cookie_value(self, cookie_names: list[str]) -> str | None:
        """Return the first matching cookie value from the current browser context."""
        cookies = await self.context.cookies()
        for cookie in cookies:
            if cookie["name"] in cookie_names:
                return cookie["value"]
        return None

    async def _wait_for_cookie(self, cookie_names: list[str], timeout_ms: int = 600000) -> str:
        """
        Wait until one of the expected cookies appears.

        This is more reliable than waiting for a specific selector because providers
        often interpose security verification or A/B-tested login pages.
        """
        deadline = asyncio.get_running_loop().time() + (timeout_ms / 1000)
        challenge_notice_shown = False

        while asyncio.get_running_loop().time() < deadline:
            cookie_value = await self._get_cookie_value(cookie_names)
            if cookie_value:
                return cookie_value

            current_url = self.page.url.lower()
            if not challenge_notice_shown and any(
                marker in current_url
                for marker in ["challenge", "captcha", "verify", "redirect"]
            ):
                print(
                    "Security verification detected. Complete it in the browser window "
                    "and the app will continue automatically."
                )
                challenge_notice_shown = True

            await asyncio.sleep(1)

        raise Exception(
            "Timed out waiting for login to complete. If a security verification page "
            "appeared, complete it in the browser and try again."
        )
    
    async def login_chatgpt(self):
        """
        Login to ChatGPT and extract session token
        
        Returns:
            dict: { session_token, email }
        """
        if not self.browser:
            await self.init_browser()
        
        print("Opening ChatGPT login page...")
        await self.page.goto('https://chat.openai.com/auth/login', wait_until='domcontentloaded')

        # Some builds show a landing page with a Log in button; others jump directly
        # into an auth flow or a security checkpoint.
        await self._click_if_visible('button:has-text("Log in")')

        print("Please complete ChatGPT login in the browser window...")
        session_token = await self._wait_for_cookie(
            ['__Secure-next-auth.session-token', 'next-auth.session-token']
        )
        
        # Navigate to chat to ensure session is fully established
        await self.page.goto('https://chat.openai.com/', wait_until='networkidle')
        await asyncio.sleep(2)
        
        email = None
        
        # Try to get email from page
        try:
            email_element = await self.page.query_selector('[data-testid="user-menu"]')
            if email_element:
                email = await email_element.get_attribute('data-email')
        except:
            pass
        
        if not session_token:
            raise Exception("Failed to obtain session token from ChatGPT")
        
        print(f"Successfully logged in to ChatGPT: {email or 'unknown email'}")
        
        return {
            'session_token': session_token,
            'email': email,
        }
    
    async def login_claude(self):
        """
        Login to Claude and extract session token
        
        Returns:
            dict: { session_token, email }
        """
        if not self.browser:
            await self.init_browser()
        email = None
        
        print("Opening Claude login page...")
        await self.page.goto('https://claude.ai/login', wait_until='domcontentloaded')

        # Claude may redirect to a challenge page before exposing the login UI.
        await self._click_if_visible('button:has-text("Log in")')

        print("Please complete Claude login and any security verification in the browser window...")
        session_token = await self._wait_for_cookie(['sessionKey', 'sessionToken'])

        # Give Claude a moment to settle on the authenticated app after login.
        await asyncio.sleep(2)
        
        if not session_token:
            raise Exception("Failed to obtain session token from Claude")
        
        # Try to get email
        try:
            await self.page.goto('https://claude.ai/settings', wait_until='networkidle')
            email_element = await self.page.query_selector('[class*="email"]')
            if email_element:
                email = await email_element.text_content()
        except:
            pass
        
        print(f"Successfully logged in to Claude: {email or 'unknown email'}")
        
        return {
            'session_token': session_token,
            'email': email,
        }

async def login_chatgpt_headful():
    """
    Convenience function for headful ChatGPT login
    Opens browser for user to log in, then returns tokens
    """
    service = AuthService()
    try:
        result = await service.login_chatgpt()
        return result
    finally:
        await service.close_browser()

async def login_claude_headful():
    """
    Convenience function for headful Claude login
    Opens browser for user to log in, then returns tokens
    """
    service = AuthService()
    try:
        result = await service.login_claude()
        return result
    finally:
        await service.close_browser()
