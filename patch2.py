import sys
import re

with open('src/pages/lagu_publish.py', 'r') as f:
    content = f.read()

# Replace Bahasa judul block
bj_old = """        # 3.1 Bahasa judul
        await self.page._page.evaluate('''() => {
            const labels = [...document.querySelectorAll('label, div')];
            const titleLang = labels.find(l => l.innerText && l.innerText.toLowerCase() === 'bahasa judul');
            if(titleLang) {
                const select = titleLang.parentElement.querySelector('.semi-select');
                if(select) select.click();
            }
        }''')
        await asyncio.sleep(1)
        await self.page._page.evaluate('''() => {
            const opts = [...document.querySelectorAll('.semi-select-option')];
            const indo = opts.find(o => o.innerText.toLowerCase().includes('indonesia'));
            if(indo) indo.click();
        }''')
        await asyncio.sleep(1)"""

bj_new = """        # 3.1 Bahasa judul
        try:
            field = self.page._page.locator(".semi-form-field").filter(has_text=re.compile(r"Bahasa judul|Title language", re.I))
            await field.locator(".semi-select").evaluate("el => el.click()")
            await asyncio.sleep(1)
            await self.page._page.locator(".semi-select-option").filter(has_text=re.compile(r"Indonesia", re.I)).first.evaluate("el => el.click()")
        except Exception:
            pass
        await asyncio.sleep(1)"""
content = content.replace(bj_old, bj_new)

# Replace Instrumental block
inst_old = """        # 3.2 Instrumental
        await self.page._page.evaluate('''() => {
            const labels = [...document.querySelectorAll('label')];
            labels.forEach(l => {
                if (l.innerText.trim().toLowerCase() === 'tidak' || l.innerText.trim().toLowerCase() === 'no') {
                    const text = l.closest('div').innerText.toLowerCase();
                    if (text.includes('instrumental') || text.includes('instramental')) {
                        l.click();
                    }
                }
            });
        }''')
        await asyncio.sleep(1)"""

inst_new = """        # 3.2 Instrumental
        try:
            field = self.page._page.locator(".semi-form-field").filter(has_text=re.compile(r"Instrumental", re.I)).first
            await field.locator("label").filter(has_text=re.compile(r"^Tidak$|^No$", re.I)).evaluate("el => el.click()")
        except Exception:
            pass
        await asyncio.sleep(1)"""
content = content.replace(inst_old, inst_new)

# Replace Kontributor block
cont_old = """        # 6. Kontributor (Vokalis)
        await self.page.evaluate('''() => {
            const btns = [...document.querySelectorAll('button')];
            const contBtn = btns.find(b => (b.innerText.toLowerCase().includes('add') || b.innerText.toLowerCase().includes('tambah')) && 
                (b.closest('div').innerText.toLowerCase().includes('contributor') || b.closest('div').innerText.toLowerCase().includes('kontributor')));
            if(contBtn) contBtn.click();
        }''')
        await asyncio.sleep(2)"""

cont_new = """        # 6. Kontributor (Vokalis)
        try:
            field = self.page._page.locator(".semi-form-field").filter(has_text=re.compile(r"Contributor|Kontributor", re.I)).first
            await field.locator("button").filter(has_text=re.compile(r"tambah|add", re.I)).evaluate("el => el.click()")
        except Exception:
            pass
        await asyncio.sleep(2)"""
content = content.replace(cont_old, cont_new)

# Replace Produksi block
prod_old = """        # 6.5 Produksi dan kontributor tambahan
        await self.page.evaluate('''() => {
            const btns = [...document.querySelectorAll('button')];
            const prodBtn = btns.find(b => (b.innerText.toLowerCase().includes('add') || b.innerText.toLowerCase().includes('tambah')) && 
                (b.closest('div').innerText.toLowerCase().includes('produksi') || b.closest('div').innerText.toLowerCase().includes('production')));
            if(prodBtn) prodBtn.click();
        }''')
        await asyncio.sleep(2)"""

prod_new = """        # 6.5 Produksi dan kontributor tambahan
        try:
            field = self.page._page.locator(".semi-form-field").filter(has_text=re.compile(r"produksi|production", re.I)).first
            await field.locator("button").filter(has_text=re.compile(r"tambah|add", re.I)).evaluate("el => el.click()")
        except Exception:
            pass
        await asyncio.sleep(2)"""
content = content.replace(prod_old, prod_new)

# Replace Penulis Lagu block
sw_old = """        # 7. Penulis lagu (Songwriter)
        await self.page.evaluate('''() => {
            const btns = [...document.querySelectorAll('button')];
            const swBtn = btns.find(b => (b.innerText.toLowerCase().includes('add') || b.innerText.toLowerCase().includes('tambah')) && 
                (b.closest('div').innerText.toLowerCase().includes('songwriter') || b.closest('div').innerText.toLowerCase().includes('penulis')));
            if(swBtn) swBtn.click();
        }''')
        await asyncio.sleep(2)"""

sw_new = """        # 7. Penulis lagu (Songwriter)
        try:
            field = self.page._page.locator(".semi-form-field").filter(has_text=re.compile(r"Songwriter|Penulis lagu", re.I)).first
            await field.locator("button").filter(has_text=re.compile(r"tambah|add", re.I)).evaluate("el => el.click()")
        except Exception:
            pass
        await asyncio.sleep(2)"""
content = content.replace(sw_old, sw_new)

# Replace Konten berlisensi block
kb_old = """        # 8. Konten berlisensi -> Tidak
        await self.page.evaluate('''() => {
            const labels = [...document.querySelectorAll('label')];
            labels.forEach(l => {
                if ((l.innerText.trim().toLowerCase().includes('tidak') || l.innerText.trim().toLowerCase().includes('no')) && 
                    (parentText.includes('berlisensi') || parentText.includes('licensed'))) {
                    l.click();
                }
            });
        }''')
        await asyncio.sleep(1)"""

kb_new = """        # 8. Konten berlisensi -> Tidak
        try:
            field = self.page._page.locator(".semi-form-field").filter(has_text=re.compile(r"berlisensi|licensed", re.I)).first
            await field.locator("label").filter(has_text=re.compile(r"^Tidak$|^No$", re.I)).evaluate("el => el.click()")
        except Exception:
            pass
        await asyncio.sleep(1)"""
content = content.replace(kb_old, kb_new)

# Replace Sudah pernah dirilis block
spd_old = """        # 10. Sudah pernah dirilis? -> Tidak
        await self.page._page.evaluate('''() => {
            const labels = [...document.querySelectorAll('label')];
            labels.forEach(l => {
                if (l.innerText.toLowerCase().includes('tidak') || l.innerText.toLowerCase().includes('no')) {
                    const text = l.closest('div').innerText.toLowerCase();
                    if (text.includes('pernah dirilis') || text.includes('previously released')) {
                        l.click();
                    }
                }
            });
        }''')
        await asyncio.sleep(1)"""

spd_new = """        # 10. Sudah pernah dirilis? -> Tidak
        try:
            field = self.page._page.locator(".semi-form-field").filter(has_text=re.compile(r"pernah dirilis|previously released", re.I)).first
            await field.locator("label").filter(has_text=re.compile(r"Tidak|No", re.I)).first.evaluate("el => el.click()")
        except Exception:
            pass
        await asyncio.sleep(1)"""
content = content.replace(spd_old, spd_new)

with open('src/pages/lagu_publish.py', 'w') as f:
    f.write(content)

print("Patch 2 applied successfully.")
