from src.interfaces.browser import IPage
from src.models.account import Account
from src.models.task_result import TaskResult
from src.tasks._base import SoundOnTask
from src.pages.login import LoginPage
from src.pages.analytics import AnalyticsPage

class TarikAnalitikTask(SoundOnTask[TaskResult]):
    """Pulls total streams analytics."""

    async def execute(self, page: IPage, account: Account) -> TaskResult:
        try:
            login_page = LoginPage(page)
            if not await login_page.login(account.email, account.password):
                return TaskResult(success=False, message="Login gagal")

            analytics_page = AnalyticsPage(page)
            data = await analytics_page.extract_streams()
            
            msg = f"Total Streams: {data['total_streams']}"
            return TaskResult(success=True, message=msg, data=data)
        except Exception as exc:
            return TaskResult(success=False, message=str(exc))
