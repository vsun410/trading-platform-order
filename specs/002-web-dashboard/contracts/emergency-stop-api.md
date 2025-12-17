# Emergency Stop API Contract

**Feature**: 002-web-dashboard
**Date**: 2025-12-17

## Overview

비상정지 서비스는 Supabase `system_status` 테이블을 통해 상태를 관리한다.
대시보드와 collector가 동일한 테이블을 참조하여 상태를 공유한다.

## Service Interface

### EmergencyStopService

```python
class EmergencyStopService:
    """비상정지 서비스 (Supabase 기반)"""

    async def activate(self, reason: str = "manual") -> bool:
        """
        비상정지 활성화.

        Args:
            reason: 활성화 사유 (기본값: "manual")

        Returns:
            bool: 성공 여부

        Side Effects:
            - system_status 테이블 업데이트
            - Telegram 알림 발송
        """
        pass

    async def deactivate(self) -> bool:
        """
        비상정지 해제.

        Returns:
            bool: 성공 여부

        Side Effects:
            - system_status 테이블 업데이트
            - Telegram 알림 발송
        """
        pass

    async def is_active(self) -> bool:
        """
        현재 비상정지 상태 확인.

        Returns:
            bool: True if 비상정지 활성화
        """
        pass

    async def get_status(self) -> dict:
        """
        상세 상태 조회.

        Returns:
            dict: {
                "active": bool,
                "activated_at": Optional[str],
                "deactivated_at": Optional[str],
                "reason": Optional[str]
            }
        """
        pass
```

## Database Operations

### Read Status

```sql
SELECT value FROM system_status WHERE key = 'emergency_stop';
```

**Response**:
```json
{
  "active": false,
  "deactivated_at": "2025-12-17T10:30:00Z"
}
```

### Activate

```sql
UPDATE system_status
SET value = jsonb_build_object(
    'active', true,
    'activated_at', NOW()::text,
    'reason', 'manual'
),
updated_at = NOW()
WHERE key = 'emergency_stop';
```

### Deactivate

```sql
UPDATE system_status
SET value = jsonb_build_object(
    'active', false,
    'deactivated_at', NOW()::text
),
updated_at = NOW()
WHERE key = 'emergency_stop';
```

## Test Scenarios

### Unit Tests

```python
# tests/unit/test_emergency_stop.py

async def test_activate_sets_active_true():
    """비상정지 활성화 시 active=true로 설정"""
    service = EmergencyStopService(mock_client)
    await service.activate(reason="test")
    status = await service.get_status()
    assert status["active"] == True
    assert status["reason"] == "test"

async def test_deactivate_sets_active_false():
    """비상정지 해제 시 active=false로 설정"""
    service = EmergencyStopService(mock_client)
    await service.activate()
    await service.deactivate()
    status = await service.get_status()
    assert status["active"] == False

async def test_is_active_returns_correct_state():
    """is_active()가 현재 상태 정확히 반환"""
    service = EmergencyStopService(mock_client)
    assert await service.is_active() == False
    await service.activate()
    assert await service.is_active() == True

async def test_activate_is_idempotent():
    """중복 활성화 시 멱등성 보장"""
    service = EmergencyStopService(mock_client)
    await service.activate()
    await service.activate()  # 두 번째 호출
    assert await service.is_active() == True  # 여전히 활성화
```

### Integration Tests

```python
# tests/integration/test_emergency_stop_supabase.py

async def test_activate_persists_to_supabase():
    """활성화 상태가 Supabase에 영속 저장"""
    service = EmergencyStopService(real_client)
    await service.activate(reason="integration_test")

    # 새 서비스 인스턴스로 조회
    service2 = EmergencyStopService(real_client)
    status = await service2.get_status()
    assert status["active"] == True
    assert status["reason"] == "integration_test"

    # Cleanup
    await service2.deactivate()
```
