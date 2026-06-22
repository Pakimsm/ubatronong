import asyncio
from src.pages.base import BasePage
from src.tasks._base import _BASE

class LoginPage(BasePage):
    async def login(self, email: str, password: str) -> bool:
        await self.navigate(f"{_BASE}/login")
        
        # Wait for page load
        await asyncio.sleep(5)
        
        # Check if already logged in (redirected to library or dashboard)
        url = await self.page.current_url()
        if "library" in url or "dashboard" in url:
            return True
            
        # Try to find username input safely
        is_username_visible = await self.is_visible("input[name='username'], input[type='email']")
        if not is_username_visible:
            return True # Probably already logged in but URL didn't match cleanly
            
        await self.page.fill("input[name='username'], input[type='email']", email)
        await self.page.fill("input[type='password']", password)
        await self.page.click("button:has-text('Log in'), button[type='submit']")
        
        # Verify state: check if URL changed to library
        for _ in range(15):
            await asyncio.sleep(1)
            url = await self.page.current_url()
            if "library" in url:
                return True
            
            if await self.is_visible(".semi-toast-error"):
                # Captcha or invalid credentials
                return False
                
        return False
