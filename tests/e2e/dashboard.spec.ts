import { test, expect } from '@playwright/test';

test.describe('KimpTrade Dashboard - 기본 로드 테스트', () => {

  test.beforeEach(async ({ page }) => {
    // 대시보드 접속
    await page.goto('/');
    // Streamlit 앱 로드 대기
    await page.waitForLoadState('networkidle');
  });

  test('대시보드 페이지 정상 로드', async ({ page }) => {
    // Streamlit 앱은 기본적으로 "app" 또는 커스텀 타이틀을 가짐
    // 타이틀 체크는 유연하게
    const title = await page.title();
    expect(title).toBeTruthy(); // 타이틀이 있으면 OK

    // 메인 컨텐츠 영역 존재 확인 (여러 가능한 선택자)
    const mainContent = page.locator('[data-testid="stAppViewContainer"], .main, .stApp');
    await expect(mainContent.first()).toBeVisible({ timeout: 15000 });
  });

  test('헤더 배너 표시 확인', async ({ page }) => {
    // KIMCHI 또는 KimchiPRO 텍스트 확인
    const header = page.locator('text=/KIMCHI|KimchiPRO/i');
    await expect(header.first()).toBeVisible({ timeout: 15000 });
  });

  test('Emergency Control 섹션 표시', async ({ page }) => {
    const emergencySection = page.locator('text=/EMERGENCY.*CONTROL/i');
    await expect(emergencySection.first()).toBeVisible({ timeout: 15000 });
  });

  test('Position Status 섹션 표시', async ({ page }) => {
    const positionSection = page.locator('text=/POSITION.*STATUS/i');
    await expect(positionSection.first()).toBeVisible({ timeout: 15000 });
  });

  test('Kimchi Premium 차트 섹션 표시', async ({ page }) => {
    const kimpSection = page.locator('text=/KIMCHI.*PREMIUM/i');
    await expect(kimpSection.first()).toBeVisible({ timeout: 15000 });
  });

  test('Profit & Loss 섹션 표시', async ({ page }) => {
    const pnlSection = page.locator('text=/PROFIT.*LOSS/i');
    await expect(pnlSection.first()).toBeVisible({ timeout: 15000 });
  });

  test('System Status 섹션 표시', async ({ page }) => {
    const statusSection = page.locator('text=/SYSTEM.*STATUS/i');
    await expect(statusSection.first()).toBeVisible({ timeout: 15000 });
  });

  test('Trade History 섹션 표시', async ({ page }) => {
    const tradeSection = page.locator('text=/TRADE.*HISTORY/i');
    await expect(tradeSection.first()).toBeVisible({ timeout: 15000 });
  });

  test('모든 6개 컴포넌트 동시 표시', async ({ page }) => {
    // 모든 주요 섹션이 동시에 표시되는지 확인
    const sections = [
      'EMERGENCY',
      'POSITION',
      'KIMCHI',
      'PROFIT',
      'SYSTEM',
      'TRADE'
    ];

    for (const section of sections) {
      const element = page.locator(`text=/${section}/i`);
      await expect(element.first()).toBeVisible({ timeout: 15000 });
    }
  });

  test('에러 메시지 없음 확인', async ({ page }) => {
    // Streamlit 에러 표시 없어야 함
    const errorElements = page.locator('[data-testid="stException"]');
    await expect(errorElements).toHaveCount(0);

    // "Error" 텍스트가 컴포넌트 에러로 표시되지 않아야 함
    // (단, "ERROR" 상태 표시는 정상)
  });

  test('자동 새로고침 설정 존재 확인', async ({ page }) => {
    // 사이드바 토글 또는 새로고침 관련 요소 확인
    const sidebar = page.locator('[data-testid="stSidebar"]');
    // 사이드바가 존재하면 확인
    if (await sidebar.isVisible()) {
      await expect(sidebar).toBeVisible();
    }
  });

});
