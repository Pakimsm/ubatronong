from src.interfaces.browser import IPage
from src.models.account import Account
from src.models.task_result import TaskResult
from src.models.identity import Identity
from src.tasks._base import SoundOnTask
from src.pages.profile import ProfilePage

class VerifikasiAkunTask(SoundOnTask[TaskResult]):
    """Verifies the account using identity data."""

    def __init__(self, identity: Identity) -> None:
        self._identity = identity

    async def execute(self, page: IPage, account: Account) -> TaskResult:
        try:
            if not await self._login(page, account):
                return TaskResult(success=False, message="Login gagal")

            profile_page = ProfilePage(page)
            success = await profile_page.fill_identity(self._identity)
            
            if success:
                return TaskResult(success=True, message="Verifikasi tersimpan sebagai draf")
            else:
                return TaskResult(success=False, message="Gagal menyimpan draf verifikasi")
        except Exception as exc:
            return TaskResult(success=False, message=str(exc))
