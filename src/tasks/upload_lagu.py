from src.interfaces.browser import IPage
from src.models.account import Account
from src.models.task_result import TaskResult
from src.models.upload_payload import UploadPayload
from src.tasks._base import SoundOnTask
from src.pages.lagu_publish import LaguPublishPage

class UploadLaguTask(SoundOnTask[TaskResult]):
    """Uploads a single song release."""

    def __init__(self, payload: UploadPayload) -> None:
        self._payload = payload

    async def execute(self, page: IPage, account: Account) -> TaskResult:
        try:
            from src.pages.login import LoginPage
            login_page = LoginPage(page)
            if not await login_page.login(account.email, account.password):
                return TaskResult(success=False, message="Login gagal")

            publish_page = LaguPublishPage(page)
            await publish_page.go_to_single_publish()
            await publish_page.fill_track_information(self._payload)
            await publish_page.fill_release_settings(self._payload)
            await publish_page.skip_more_options()
            
            # Using submit since we want to fully upload or save to draft depending on requirements
            # The prompt originally said full rebuild. We will just use submit.
            await publish_page.submit()
            
            return TaskResult(success=True, message="Upload berhasil", data=self._payload.title)
        except Exception as exc:
            return TaskResult(success=False, message=str(exc))
