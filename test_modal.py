import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.models.browser_config import BrowserConfig
from src.core.account_manager import JsonAccountRepository
from src.tasks.upload_lagu import UploadLaguTask
from src.pages.login import LoginPage
from src.pages.lagu_publish import LaguPublishPage
from src.models.upload_payload import UploadPayload

async def main():
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    repo = JsonAccountRepository(Path("config/accounts.json"))
    account = repo.get_all()[0]
    page = await browser.new_page()
    lp = LoginPage(page)
    await lp.login(account.email, account.password)
    pp = LaguPublishPage(page)
    await pp.go_to_single_publish()
    
    await pp.page._page.evaluate('''() => {
        const labels = [...document.querySelectorAll('div, span, label')];
        const target = labels.find(l => l.innerText && (l.innerText.toLowerCase() === 'kontributor' || l.innerText.toLowerCase() === 'contributor'));
        if (!target) return;
        let p = target.parentElement;
        for (let i = 0; i < 6 && p; i++) {
            const btns = [...p.querySelectorAll('button')];
            const addBtn = btns.find(b => b.innerText && (b.innerText.toLowerCase().includes('tambah') || b.innerText.toLowerCase().includes('add')));
            if (addBtn) { addBtn.click(); return; }
            p = p.parentElement;
        }
    }''')
    await asyncio.sleep(3)
    html = await pp.page._page.content()
    with open("debug_modal.html", "w") as f:
        f.write(html)
    print("Modal HTML dumped.")
    await browser.close()

asyncio.run(main())
