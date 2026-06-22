from src.interfaces.browser import IPage
from src.models.account import Account
from src.models.task_result import TaskResult
from src.tasks._base import SoundOnTask
from src.pages.login import LoginPage

class TesLoginTask(SoundOnTask[TaskResult]):
    """Tests if the account credentials are valid by logging in."""

    async def execute(self, page: IPage, account: Account) -> TaskResult:
        try:
            login_page = LoginPage(page)
            success = await login_page.login(account.email, account.password)
            if success:
                return TaskResult(success=True, message="Login berhasil")
            else:
                return TaskResult(success=False, message="Login gagal (kredensial salah atau captcha)")
        except Exception as exc:
            return TaskResult(success=False, message=f"Error saat login: {exc}")
