from src.interfaces.browser import IPage
from src.models.account import Account
from src.models.task_result import TaskResult
from src.tasks._base import SoundOnTask
from src.pages.library import LibraryPage

class TarikDataTask(SoundOnTask[TaskResult]):
    """Pulls detailed track metadata (title, artist, yt_link) from library."""

    async def execute(self, page: IPage, account: Account) -> TaskResult:
        try:
            from src.pages.login import LoginPage
            login_page = LoginPage(page)
            if not await login_page.login(account.email, account.password):
                return TaskResult(success=False, message="Login gagal")

            library_page = LibraryPage(page)
            tracks = await library_page.extract_tracks_data()
            
            msg = f"Berhasil menarik {len(tracks)} data lagu."
            return TaskResult(success=True, message=msg, data=tracks)
        except Exception as exc:
            return TaskResult(success=False, message=str(exc))
