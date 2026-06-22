import re

with open('src/pages/lagu_publish.py', 'r') as f:
    content = f.read()

# 1. Fix the cover upload selector from 'image' to '.jpg'
content = content.replace(
    'file_inputs = await self.page._page.locator("input[type=\'file\'][accept*=\'image\']").all()',
    'file_inputs = await self.page._page.locator("input[type=\'file\'][accept*=\'.jpg\']").all()'
)

# 2. Fix the "Next" button click which timed out
old_next = """        await self.page._page.locator("button:has-text('Next'), button:has-text('Selanjutnya')").evaluate("el => el.click()")
        await asyncio.sleep(2)"""

new_next = """        await self.page._page.evaluate('''() => {
            const btns = [...document.querySelectorAll('button, div, span, a')];
            const btn = btns.find(b => b.innerText && (b.innerText.trim() === 'Next' || b.innerText.trim() === 'Selanjutnya'));
            if (btn) btn.click();
        }''')
        await asyncio.sleep(2)"""

content = content.replace(old_next, new_next)

with open('src/pages/lagu_publish.py', 'w') as f:
    f.write(content)
