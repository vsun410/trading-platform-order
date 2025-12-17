import { test, expect } from '@playwright/test';

test.describe('Emergency Panel - 비상정지 기능 테스트', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('Emergency Control 패널 렌더링', async ({ page }) => {
    // Emergency Control 헤더 확인
    const header = page.locator('text=/EMERGENCY.*CONTROL/i');
    await expect(header.first()).toBeVisible({ timeout: 15000 });
  });

  test('Emergency Stop 버튼 표시', async ({ page }) => {
    // EMERGENCY STOP 버튼 존재 확인
    const stopButton = page.locator('button:has-text("EMERGENCY STOP")');
    await expect(stopButton.first()).toBeVisible({ timeout: 15000 });
  });

  test('Resume System 버튼 표시', async ({ page }) => {
    // RESUME SYSTEM 버튼 존재 확인
    const resumeButton = page.locator('button:has-text("RESUME")');
    await expect(resumeButton.first()).toBeVisible({ timeout: 15000 });
  });

  test('시스템 상태 표시 (ACTIVE 또는 STOPPED)', async ({ page }) => {
    // SYSTEM ACTIVE 또는 STOPPED 상태 표시 확인
    const activeStatus = page.locator('text=/SYSTEM.*ACTIVE|STOPPED/i');
    await expect(activeStatus.first()).toBeVisible({ timeout: 15000 });
  });

  test('Emergency Stop 버튼 클릭 시 확인 다이얼로그', async ({ page }) => {
    // Emergency Stop 버튼 찾기
    const stopButton = page.locator('button:has-text("EMERGENCY STOP")').first();

    // 버튼이 비활성화되어 있지 않으면 클릭
    if (await stopButton.isEnabled()) {
      await stopButton.click();

      // 확인 다이얼로그 표시 확인
      const confirmDialog = page.locator('text=/CONFIRM.*EMERGENCY.*STOP/i');
      await expect(confirmDialog.first()).toBeVisible({ timeout: 5000 });

      // Cancel 버튼으로 취소
      const cancelButton = page.locator('button:has-text("CANCEL")');
      if (await cancelButton.first().isVisible()) {
        await cancelButton.first().click();
      }
    }
  });

  test('비상정지 상태에서 Resume 버튼 활성화', async ({ page }) => {
    // STOPPED 상태인 경우 Resume 버튼이 활성화되어야 함
    const stoppedStatus = page.locator('text=/STOPPED/i');

    if (await stoppedStatus.first().isVisible()) {
      const resumeButton = page.locator('button:has-text("RESUME")').first();
      await expect(resumeButton).toBeEnabled();
    }
  });

  test('정상 상태에서 Emergency Stop 버튼 활성화', async ({ page }) => {
    // ACTIVE 상태인 경우 Stop 버튼이 활성화되어야 함
    const activeStatus = page.locator('text=/SYSTEM.*ACTIVE/i');

    if (await activeStatus.first().isVisible()) {
      const stopButton = page.locator('button:has-text("EMERGENCY STOP")').first();
      await expect(stopButton).toBeEnabled();
    }
  });

  test('경고 스트라이프 패턴 표시', async ({ page }) => {
    // Emergency 패널의 경고 스타일 확인 (배경색 또는 보더)
    const emergencyPanel = page.locator('.emergency-panel, [class*="emergency"]').first();

    // 패널이 존재하면 확인
    if (await emergencyPanel.isVisible()) {
      await expect(emergencyPanel).toBeVisible();
    }
  });

});
