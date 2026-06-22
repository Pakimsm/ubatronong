from typing import Any, List, Optional

from src.interfaces.account_repo import IAccountRepository
from src.interfaces.browser import IBrowser
from src.interfaces.notifier import INotifier
from src.interfaces.task import ITask
from src.models.account import Account


class AppRunner:
    """Orchestrates task execution across multiple accounts."""

    def __init__(
        self,
        browser: IBrowser,
        account_repo: IAccountRepository,
        notifier: INotifier,
    ) -> None:
        self._browser = browser
        self._account_repo = account_repo
        self._notifier = notifier

    async def run(
        self,
        task: ITask[Any],
        account_ids: Optional[List[int]] = None,
        accounts: Optional[List[Account]] = None,
    ) -> List[Any]:
        if accounts is None:
            if type(task).__name__ == "TesLoginTask":
                repo_accounts = self._account_repo.get_active()
            else:
                repo_accounts = [a for a in self._account_repo.get_active() if a.status == "Berhasil Login"]
                
            if account_ids:
                accounts = [a for a in repo_accounts if a.id in account_ids]
            else:
                accounts = repo_accounts

        if not accounts:
            self._notifier.console.print("[yellow]Tidak ada akun yang memenuhi syarat untuk task ini.[/]")
            return []

        results: List[Any] = []
        total = len(accounts)

        async with self._browser:
            for idx, account in enumerate(accounts, start=1):
                self._notifier.progress(idx, total, account.email)
                page = await self._browser.new_page()
                try:
                    result = await task.execute(page, account)
                    results.append(result)
                    
                    if type(task).__name__ == "TesLoginTask":
                        account.status = "Berhasil Login" if result.success else "Gagal Login"
                        self._account_repo.save(account)

                    if result.success:
                        self._notifier.success(f"[{account.email}] {result.message}")
                        if result.data:
                            # Use info to print the data nicely
                            import json
                            if isinstance(result.data, (dict, list)):
                                self._notifier.info(f"Data:\n{json.dumps(result.data, indent=2)}")
                            else:
                                self._notifier.info(f"Data: {result.data}")
                    else:
                        self._notifier.error(f"[{account.email}] Gagal: {result.message}")
                except Exception as exc:
                    self._notifier.error(f"[{account.email}] Error Sistem", exc)
                    if type(task).__name__ == "TesLoginTask":
                        account.status = "Error Sistem"
                        self._account_repo.save(account)
                finally:
                    await page.close()

        return results
