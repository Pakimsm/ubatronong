from src.interfaces.browser import IPage
from src.models.account import Account
from src.models.task_result import TaskResult
from src.tasks._base import SoundOnTask

class TesLoginTask(SoundOnTask[TaskResult]):
    """Tests if the account credentials are valid by logging in."""

    async def execute(self, page: IPage, account: Account) -> TaskResult:
        try:
            success = await self._login(page, account)
            if success:
                return TaskResult(success=True, message="Login berhasil")
            else:
                return TaskResult(success=False, message="Login gagal (kredensial salah atau captcha)")
        except Exception as exc:
            return TaskResult(success=False, message=f"Error saat login: {exc}")
