import sys

with open('src/pages/lagu_publish.py', 'r') as f:
    content = f.read()

# 1. Add Bahasa Judul and Instrumental
title_block = """        except:
            await self.fill_react("input[type='text']", payload.title)
        await asyncio.sleep(2)"""

new_title_block = """        except:
            await self.fill_react("input[type='text']", payload.title)
        await asyncio.sleep(2)

        # 3.1 Bahasa judul
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
        await asyncio.sleep(1)

        # 3.2 Instrumental
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

content = content.replace(title_block, new_title_block)

# 2. Fix Kontributor match
cont_match = """            const contBtn = btns.find(b => (b.innerText.includes('Add') || b.innerText.includes('Tambah')) && 
                (b.closest('div').innerText.includes('Contributor') || b.closest('div').innerText.includes('Kontributor')));"""
new_cont_match = """            const contBtn = btns.find(b => (b.innerText.toLowerCase().includes('add') || b.innerText.toLowerCase().includes('tambah')) && 
                (b.closest('div').innerText.toLowerCase().includes('contributor') || b.closest('div').innerText.toLowerCase().includes('kontributor')));"""
content = content.replace(cont_match, new_cont_match)

# 3. Add Produksi dan kontributor tambahan
after_contributor = """        # Click Kirim/Submit
        await self.page._page.evaluate('''() => {
            const modal = [...document.querySelectorAll("dialog")].find(d => d.querySelector("#artistRole") || d.querySelector("#artistProfile"));
            if (!modal) return;
            const btn = [...modal.querySelectorAll("button")].find(b => /kirim|submit/i.test(b.innerText));
            if (btn) btn.click();
        }''')
        await asyncio.sleep(2)"""

new_after_contributor = after_contributor + """

        # 6.5 Produksi dan kontributor tambahan
        await self.page.evaluate('''() => {
            const btns = [...document.querySelectorAll('button')];
            const prodBtn = btns.find(b => (b.innerText.toLowerCase().includes('add') || b.innerText.toLowerCase().includes('tambah')) && 
                (b.closest('div').innerText.toLowerCase().includes('produksi') || b.closest('div').innerText.toLowerCase().includes('production')));
            if(prodBtn) prodBtn.click();
        }''')
        await asyncio.sleep(2)
        
        await self.page._page.evaluate("() => document.getElementById('artistProfile')?.click()")
        await asyncio.sleep(1)
        await self.page._page.evaluate('''(name) => {
            const inset = document.getElementById("artistProfile")?.querySelector("input");
            if (inset) {
                inset.focus();
                const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
                setter.call(inset, name);
                inset.dispatchEvent(new Event("input", {bubbles: true}));
                inset.dispatchEvent(new Event("change", {bubbles: true}));
            }
        }''', payload.artist)
        await asyncio.sleep(2)
        await self.page._page.evaluate('''(name) => {
            const opts = [...document.querySelectorAll("[class*='target-option'], [class*='option']")];
            const match = opts.find(o => o.getAttribute("artistname")?.toLowerCase() === name.toLowerCase());
            const opt = match || opts[0];
            if (opt) opt.click();
        }''', payload.artist)
        await asyncio.sleep(1)
        
        await self.page._page.evaluate("() => document.getElementById('artistRole')?.click()")
        await asyncio.sleep(1)
        await self.page._page.evaluate('''() => {
            const opts = [...document.querySelectorAll("[role='listbox'] [role='option']")];
            const prodOpt = opts.find(o => o.innerText.toLowerCase().includes('producer') || o.innerText.toLowerCase().includes('produser'));
            if(prodOpt) prodOpt.click();
            else if(opts.length > 0) opts[0].click();
        }''')
        await asyncio.sleep(1)
        
        await self.page._page.evaluate('''() => {
            const modal = [...document.querySelectorAll("dialog")].find(d => d.querySelector("#artistRole") || d.querySelector("#artistProfile"));
            if (!modal) return;
            const btn = [...modal.querySelectorAll("button")].find(b => /kirim|submit/i.test(b.innerText));
            if (btn) btn.click();
        }''')
        await asyncio.sleep(2)"""
content = content.replace(after_contributor, new_after_contributor, 1)

# 4. Fix Songwriter match
sw_match = """            const swBtn = btns.find(b => (b.innerText.includes('Add') || b.innerText.includes('Tambah')) && 
                (b.closest('div').innerText.includes('Songwriter') || b.closest('div').innerText.includes('Penulis')));"""
new_sw_match = """            const swBtn = btns.find(b => (b.innerText.toLowerCase().includes('add') || b.innerText.toLowerCase().includes('tambah')) && 
                (b.closest('div').innerText.toLowerCase().includes('songwriter') || b.closest('div').innerText.toLowerCase().includes('penulis')));"""
content = content.replace(sw_match, new_sw_match)

# 5. Fix Konten Berlisensi match
kb_match = """                if ((l.innerText.trim() === 'Tidak' || l.innerText.trim() === 'No') && 
                    (parentText.includes('berlisensi') || parentText.includes('licensed'))) {"""
new_kb_match = """                if ((l.innerText.trim().toLowerCase().includes('tidak') || l.innerText.trim().toLowerCase().includes('no')) && 
                    (parentText.includes('berlisensi') || parentText.includes('licensed'))) {"""
content = content.replace(kb_match, new_kb_match)

# 6. Fix Sudah pernah dirilis match
spd_match = """                if (l.innerText.trim() === 'Tidak' || l.innerText.trim() === 'No') {
                    const text = l.closest('div').innerText.toLowerCase();
                    if (text.includes('pernah dirilis') || text.includes('previously released')) {
                        l.click();
                    }
                }"""
new_spd_match = """                if (l.innerText.toLowerCase().includes('tidak') || l.innerText.toLowerCase().includes('no')) {
                    const text = l.closest('div').innerText.toLowerCase();
                    if (text.includes('pernah dirilis') || text.includes('previously released')) {
                        l.click();
                    }
                }"""
content = content.replace(spd_match, new_spd_match)

with open('src/pages/lagu_publish.py', 'w') as f:
    f.write(content)

print("Patch applied successfully.")
