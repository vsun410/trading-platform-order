"""
비상정지 서비스

Supabase 기반으로 비상정지 상태를 관리합니다.
PC/모바일 웹에서 공유되는 플래그입니다.
"""

from datetime import datetime, timezone
from typing import Optional

from loguru import logger

from src.database.supabase_client import SupabaseClient
from src.telegram.notifier import TelegramNotifier


class EmergencyStop:
    """
    비상정지 관리 서비스

    Supabase의 system_status 테이블을 사용하여
    비상정지 플래그를 저장하고 조회합니다.
    """

    TABLE_NAME = "system_status"
    STATUS_KEY = "emergency_stop"

    def __init__(self):
        self._db: Optional[SupabaseClient] = None
        self._notifier: Optional[TelegramNotifier] = None

    def _get_db(self) -> SupabaseClient:
        """DB 클라이언트 가져오기 (lazy init)"""
        if self._db is None:
            self._db = SupabaseClient()
        return self._db

    def _get_notifier(self) -> TelegramNotifier:
        """Telegram notifier 가져오기 (lazy init)"""
        if self._notifier is None:
            self._notifier = TelegramNotifier()
        return self._notifier

    async def is_active(self) -> bool:
        """
        비상정지 활성화 상태 확인

        Returns:
            True면 비상정지 활성화됨 (신규 진입 차단)
        """
        try:
            db = self._get_db()
            result = (
                db._client.table(self.TABLE_NAME)
                .select("value")
                .eq("key", self.STATUS_KEY)
                .single()
                .execute()
            )

            if result.data:
                return result.data.get("value", {}).get("active", False)
            return False

        except Exception as e:
            logger.error(f"[emergency] 상태 조회 실패: {e}")
            # 조회 실패 시 안전하게 True 반환 (진입 차단)
            return True

    async def activate(self, reason: str = "manual") -> bool:
        """
        비상정지 활성화

        Args:
            reason: 활성화 사유 (manual, api_error, position_mismatch 등)

        Returns:
            성공 여부
        """
        try:
            db = self._get_db()
            now = datetime.now(timezone.utc).isoformat()

            data = {
                "key": self.STATUS_KEY,
                "value": {
                    "active": True,
                    "activated_at": now,
                    "reason": reason,
                },
                "updated_at": now,
            }

            # Upsert (있으면 업데이트, 없으면 삽입)
            db._client.table(self.TABLE_NAME).upsert(data).execute()

            logger.warning(f"[emergency] 비상정지 활성화: {reason}")

            # Telegram 알림 발송
            try:
                notifier = self._get_notifier()
                await notifier.send_emergency_stop_activated(reason)
            except Exception as notify_error:
                logger.warning(f"[emergency] 알림 발송 실패: {notify_error}")

            return True

        except Exception as e:
            logger.error(f"[emergency] 활성화 실패: {e}")
            return False

    async def deactivate(self) -> bool:
        """
        비상정지 해제

        Returns:
            성공 여부
        """
        try:
            db = self._get_db()
            now = datetime.now(timezone.utc).isoformat()

            data = {
                "key": self.STATUS_KEY,
                "value": {
                    "active": False,
                    "deactivated_at": now,
                },
                "updated_at": now,
            }

            db._client.table(self.TABLE_NAME).upsert(data).execute()

            logger.info("[emergency] 비상정지 해제됨")

            # Telegram 알림 발송
            try:
                notifier = self._get_notifier()
                await notifier.send_emergency_stop_deactivated()
            except Exception as notify_error:
                logger.warning(f"[emergency] 알림 발송 실패: {notify_error}")

            return True

        except Exception as e:
            logger.error(f"[emergency] 해제 실패: {e}")
            return False

    async def get_status(self) -> dict:
        """
        상세 상태 조회

        Returns:
            {
                "active": bool,
                "activated_at": str (ISO format),
                "deactivated_at": str (ISO format),
                "reason": str
            }
        """
        try:
            db = self._get_db()
            result = (
                db._client.table(self.TABLE_NAME)
                .select("value, updated_at")
                .eq("key", self.STATUS_KEY)
                .single()
                .execute()
            )

            if result.data:
                return {
                    **result.data.get("value", {}),
                    "updated_at": result.data.get("updated_at"),
                }

            return {"active": False, "reason": "no_record"}

        except Exception as e:
            logger.error(f"[emergency] 상태 조회 실패: {e}")
            return {"active": True, "reason": f"error: {e}"}


# 싱글톤 인스턴스
_instance: Optional[EmergencyStop] = None


def get_emergency_stop() -> EmergencyStop:
    """싱글톤 인스턴스 반환"""
    global _instance
    if _instance is None:
        _instance = EmergencyStop()
    return _instance
