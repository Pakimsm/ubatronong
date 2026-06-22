import asyncio
from src.pages.base import BasePage
from src.constants import BASE_URL as _BASE

class LibraryPage(BasePage):
    async def extract_tracks_data(self) -> list:
        await self.navigate(f"{_BASE}/library")
        await self.wait_for_element(".semi-table", timeout=15000)
        
        if not await self.is_visible(".semi-table-row"):
            return []
            
        return await self.page.evaluate("""() => {
            const rows = [...document.querySelectorAll('.semi-table-row')].slice(1); // Skip header
            return rows.map(row => {
                const cells = row.querySelectorAll('.semi-table-cell');
                if (cells.length < 3) return null;
                
                // Exact parsing depends on SoundOn's DOM structure
                // Assume title is in 1st cell, artist in 2nd
                const titleEl = cells[0].querySelector('.title') || cells[0];
                const artistEl = cells[1].querySelector('.artist') || cells[1];
                const isrcEl = cells[2] || null; // Usually ISRC or ID is listed
                
                return {
                    title: titleEl.innerText.trim(),
                    artist: artistEl.innerText.trim(),
                    youtube_id: "TBD", // Needs actual DOM inspection of the live page
                    youtube_link: "TBD"
                };
            }).filter(Boolean);
        }""")
