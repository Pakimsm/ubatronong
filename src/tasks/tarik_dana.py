from src.interfaces.browser import IPage
from src.models.account import Account
from src.models.task_result import TaskResult
from src.tasks._base import SoundOnTask
from src.pages.withdraw import WithdrawPage

class TarikDanaTask(SoundOnTask[TaskResult]):
    """Withdraws earnings."""

    async def execute(self, page: IPage, account: Account) -> TaskResult:
        try:
            from src.pages.login import LoginPage
            login_page = LoginPage(page)
            if not await login_page.login(account.email, account.password):
                return TaskResult(success=False, message="Login gagal")

            withdraw_page = WithdrawPage(page)
            balance = await withdraw_page.get_balance()
            
            # Simplified logic just showing the POM structure
            if float(balance.replace('$', '').replace(',', '')) > 0:
                success = await withdraw_page.withdraw_all()
                if success:
                    return TaskResult(success=True, message=f"Penarikan dana {balance} berhasil")
                else:
                    return TaskResult(success=False, message="Gagal menarik dana (kemungkinan modal tidak muncul)")
            else:
                return TaskResult(success=False, message="Saldo 0")
        except Exception as exc:
            return TaskResult(success=False, message=str(exc))
