import asyncio
from src.pages.base import BasePage
from src.models.identity import Identity
from src.constants import BASE_URL as _BASE

_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

class ProfilePage(BasePage):
    async def fill_identity(self, identity: Identity) -> bool:
        await self.navigate(f"{_BASE}/library/profile?lang=id&region=ID&mode=edit&type=artist")
        await self.wait_for_element("#stageName")
        
        await self.fill("#stageName", identity.artist_name)
        
        await self.select_semi(0, str(identity.birth_day))
        await self.select_semi(1, _MONTHS[identity.birth_month - 1])
        await self.select_semi(2, str(identity.birth_year))
        
        await self.fill(".semi-input-wrapper__with-prefix input", identity.phone)
        await self.fill("#realName", identity.legal_name)
        await self.fill("#userAddress", identity.address)
        
        all_selects = await self.page.query_selector_all(".semi-select")
        id_type_idx = len(all_selects) - 1
        await self.select_semi(id_type_idx, identity.id_type)
        
        await self.fill("#idNumber", identity.id_number)
        
        if identity.id_image_path:
            await self.page.set_input_files('#idPhotoFrontSide input[type="file"]', str(identity.id_image_path))
            await asyncio.sleep(2)
            
        await self.page.evaluate("() => document.querySelectorAll('.semi-checkbox').forEach(el => el.click())")
        await asyncio.sleep(0.5)
        
        try:
            await self.click("button:has-text('Simpan sebagai draf')", timeout=3000)
        except Exception:
            try:
                await self.click("button:has-text('Save as draft')", timeout=3000)
            except Exception:
                pass
                
        await asyncio.sleep(4)
        return True
