from src.interfaces.browser import IPage
from src.models.account import Account
from src.models.task_result import TaskResult
from src.models.upload_payload import UploadPayload
from src.tasks._base import SoundOnTask
from src.pages.album_publish import AlbumPublishPage

class UploadAlbumTask(SoundOnTask[TaskResult]):
    """Uploads an album release."""

    def __init__(self, payload: UploadPayload) -> None:
        self._payload = payload

    async def execute(self, page: IPage, account: Account, draft_url: str = None) -> TaskResult:
        try:
            if not await self._login(page, account):
                return TaskResult(success=False, message="Login gagal")

            publish_page = AlbumPublishPage(page)
            await publish_page.go_to_album_publish(url=draft_url)
            await publish_page.fill_album_information(self._payload)
            await publish_page.upload_tracks(self._payload)
            
            return TaskResult(success=True, message=f"Upload Album '{self._payload.title}' berhasil disimpan di draf", data=self._payload.title)
        except Exception as exc:
            return TaskResult(success=False, message=str(exc))
