import re
import os

with open('src/pages/lagu_publish.py', 'r') as f:
    content = f.read()

# Replace the AI cover logic with local image generation and upload
old_ai_cover = """        await self.click("button:has-text('Buat sampul ai'), button:has-text('Buat sampul AI'), button:has-text('Generate AI cover')")
        except Exception as e:
            await self.page._page.screenshot(path="/home/aaa/soundonbot/debug_cover_error.png", full_page=True)
            html = await self.page._page.content()
            with open("/home/aaa/soundonbot/debug_cover_error.html", "w") as f:
                f.write(html)
            raise e
        await asyncio.sleep(2)
        await self.page._page.locator("text='Animasi 2D'").click()
        await asyncio.sleep(1)
        await self.click("button:has-text('Hasilkan'), button:has-text('Generate')")
        
        try:
            await self.page._page.locator("button:has-text('Setuju dan lanjutkan'), button:has-text('Agree and continue')").click(timeout=5000, force=True)
            await asyncio.sleep(1)
        except Exception:
            pass
        
        try:
            await self.page._page.wait_for_function('''() => {
                const btns = [...document.querySelectorAll('button')];
                const btn = btns.find(b => b.innerText.includes('Gunakan ini') || b.innerText.includes('Use this'));
                return btn && !btn.disabled && btn.getAttribute('aria-disabled') !== 'true' && !btn.className.includes('disabled');
            }''', timeout=120000)
            await asyncio.sleep(2)
            btn_loc = self.page._page.locator("button:has-text('Gunakan ini'), button:has-text('Use this')")
            await btn_loc.evaluate("el => el.click()")
        except Exception as e:
            await self.page.screenshot("/home/aaa/soundonbot/debug_cover_fail.png", full_page=True)
            raise e
        await asyncio.sleep(2)"""

new_cover_upload = """        try:
            cover_path = "/home/aaa/soundonbot/generated_cover.jpg"
            # Generate a solid color cover with PIL
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (3000, 3000), color = (73, 109, 137))
            d = ImageDraw.Draw(img)
            # Try to get a basic font, fallback to default
            try:
                fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 150)
            except:
                fnt = ImageFont.load_default()
            d.text((1500, 1500), payload.title, font=fnt, fill=(255, 255, 0), anchor="mm")
            d.text((1500, 1800), payload.artist, font=fnt, fill=(255, 255, 255), anchor="mm")
            img.save(cover_path)
            
            # Find the image file input
            file_inputs = await self.page._page.locator("input[type='file'][accept*='image']").all()
            if file_inputs:
                await file_inputs[-1].set_input_files(cover_path)
                # Wait for upload to complete
                await asyncio.sleep(10)
            else:
                print("DEBUG: No image file input found!")
        except Exception as e:
            print(f"DEBUG: Cover upload failed: {e}")"""

# Because of the try block I added in patch5, I'll use regex to replace it properly
pattern = r"try:\s+await self\.click\(\"button:has-text\('Buat sampul ai'\).*?await asyncio\.sleep\(2\)"
content = re.sub(pattern, new_cover_upload, content, flags=re.DOTALL)

with open('src/pages/lagu_publish.py', 'w') as f:
    f.write(content)
