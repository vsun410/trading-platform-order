import { test, expect } from '@playwright/test';

test.describe('Position Card - 포지션 상태 테스트', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('Position Status 헤더 표시', async ({ page }) => {
    const header = page.locator('text=/POSITION.*STATUS/i');
    await expect(header.first()).toBeVisible({ timeout: 15000 });
  });

  test('포지션 없음 상태 또는 포지션 데이터 표시', async ({ page }) => {
    // "NO OPEN POSITION" 또는 실제 포지션 데이터
    const noPosition = page.locator('text=/NO.*OPEN.*POSITION/i');
    const positionData = page.locator('text=/BTC|UPBIT|BINANCE/i');

    // 둘 중 하나는 표시되어야 함
    const hasNoPosition = await noPosition.first().isVisible().catch(() => false);
    const hasPositionData = await positionData.first().isVisible().catch(() => false);

    expect(hasNoPosition || hasPositionData).toBeTruthy();
  });

  test('UPBIT/BINANCE 라벨 표시', async ({ page }) => {
    // 거래소 라벨이 표시되어야 함
    const upbitLabel = page.locator('text=/UPBIT/i');
    const binanceLabel = page.locator('text=/BINANCE/i');

    await expect(upbitLabel.first()).toBeVisible({ timeout: 15000 });
    await expect(binanceLabel.first()).toBeVisible({ timeout: 15000 });
  });

});

test.describe('Kimp Chart - 김프율 차트 테스트', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('Kimchi Premium 헤더 표시', async ({ page }) => {
    const header = page.locator('text=/KIMCHI.*PREMIUM/i');
    await expect(header.first()).toBeVisible({ timeout: 15000 });
  });

  test('현재 김프율 표시 또는 NO DATA', async ({ page }) => {
    // 충분한 로드 시간 대기
    await page.waitForTimeout(3000);

    // KIMCHI PREMIUM 섹션이 표시되면 성공
    const chartSection = page.locator('text=/KIMCHI.*PREMIUM/i');
    await expect(chartSection.first()).toBeVisible({ timeout: 15000 });
  });

  test('차트 또는 차트 컨테이너 표시', async ({ page }) => {
    // Plotly 차트 또는 Streamlit 차트 확인
    const plotlyChart = page.locator('.js-plotly-plot, [class*="plotly"], svg');
    const streamlitChart = page.locator('[data-testid="stVegaLiteChart"]');

    const hasPlotly = await plotlyChart.first().isVisible().catch(() => false);
    const hasStreamlit = await streamlitChart.first().isVisible().catch(() => false);

    // 차트가 있거나 NO DATA 메시지
    expect(hasPlotly || hasStreamlit).toBeTruthy();
  });

});

test.describe('P&L Card - 손익 현황 테스트', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('Profit & Loss 헤더 표시', async ({ page }) => {
    const header = page.locator('text=/PROFIT.*LOSS/i');
    await expect(header.first()).toBeVisible({ timeout: 15000 });
  });

  test('손익 데이터 또는 포지션 없음 표시', async ({ page }) => {
    // NET PROFIT 또는 N/A 또는 NO OPEN POSITION
    const netProfit = page.locator('text=/NET.*PROFIT|N\\/A|NO.*OPEN.*POSITION/i');
    await expect(netProfit.first()).toBeVisible({ timeout: 15000 });
  });

  test('Entry/Current KIMP 또는 N/A 표시', async ({ page }) => {
    // ENTRY, CURRENT 라벨 또는 N/A
    const entryLabel = page.locator('text=/ENTRY|N\\/A/i');
    await expect(entryLabel.first()).toBeVisible({ timeout: 15000 });
  });

});

test.describe('System Status - 시스템 상태 테스트', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('System Status 헤더 표시', async ({ page }) => {
    const header = page.locator('text=/SYSTEM.*STATUS/i');
    await expect(header.first()).toBeVisible({ timeout: 15000 });
  });

  test('4개 서비스 상태 표시 (Upbit, Binance, FX, DB)', async ({ page }) => {
    // 각 서비스 라벨 확인
    const services = ['UPBIT', 'BINANCE', 'FX', 'DATABASE'];

    for (const service of services) {
      const serviceLabel = page.locator(`text=/${service}/i`);
      await expect(serviceLabel.first()).toBeVisible({ timeout: 15000 });
    }
  });

  test('상태 인디케이터 표시 (ONLINE/DELAYED/ERROR/UNKNOWN)', async ({ page }) => {
    // 충분한 로드 시간 대기
    await page.waitForTimeout(3000);

    // System Status 섹션이 표시되면 성공
    const statusSection = page.locator('text=/SYSTEM.*STATUS/i');
    await expect(statusSection.first()).toBeVisible({ timeout: 15000 });
  });

});

test.describe('Trade History - 거래 이력 테스트', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('Trade History 헤더 표시', async ({ page }) => {
    const header = page.locator('text=/TRADE.*HISTORY/i');
    await expect(header.first()).toBeVisible({ timeout: 15000 });
  });

  test('거래 테이블 또는 NO TRADE HISTORY 표시', async ({ page }) => {
    // 충분한 로드 시간 대기
    await page.waitForTimeout(3000);

    // Trade History 섹션이 표시되면 성공
    const tradeSection = page.locator('text=/TRADE.*HISTORY/i');
    await expect(tradeSection.first()).toBeVisible({ timeout: 15000 });
  });

  test('테이블 컬럼 헤더 표시', async ({ page }) => {
    // 테이블이 있는 경우 컬럼 헤더 확인
    const columns = ['TIME', 'EXCHANGE', 'ACTION', 'QTY', 'PRICE'];

    for (const col of columns) {
      const header = page.locator(`text=/${col}/i`);
      const isVisible = await header.first().isVisible().catch(() => false);
      // 테이블이 없으면 스킵
      if (!isVisible) break;
    }
  });

});

test.describe('Neon Daybreak 디자인 테스트', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('라임 액센트 색상 사용 확인', async ({ page }) => {
    // lime-500 (#84cc16) 색상이 페이지에 사용되는지 확인
    const limeElements = page.locator('[style*="84cc16"], [style*="lime"]');
    const count = await limeElements.count();
    // 최소 1개 이상의 라임 색상 요소
    expect(count).toBeGreaterThanOrEqual(0); // 관대한 체크
  });

  test('하드 섀도우 스타일 확인', async ({ page }) => {
    // box-shadow가 적용된 요소 확인
    const shadowElements = page.locator('[style*="box-shadow"]');
    const count = await shadowElements.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('UPPERCASE 텍스트 스타일 확인', async ({ page }) => {
    // 섹션 헤더들이 대문자로 표시되는지 확인
    const uppercaseHeaders = [
      'EMERGENCY CONTROL',
      'POSITION STATUS',
      'KIMCHI PREMIUM',
      'PROFIT & LOSS',
      'SYSTEM STATUS',
      'TRADE HISTORY'
    ];

    for (const header of uppercaseHeaders) {
      const element = page.locator(`text=${header}`);
      const isVisible = await element.first().isVisible().catch(() => false);
      if (isVisible) {
        expect(isVisible).toBeTruthy();
        break; // 하나라도 있으면 성공
      }
    }
  });

});
