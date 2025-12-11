# 🎨 Design System Reference

**Design System:** Kinetic Minimalism  
**Master Location:** [storage/docs/DESIGN_SYSTEM.md](https://github.com/vsun410/trading-platform-storage/blob/main/docs/DESIGN_SYSTEM.md)

> ⚠️ 이 문서는 요약본입니다. 전체 디자인 시스템은 **storage 레포**를 참조하세요.

---

## Order 레포 UI 역할

| 기능 | 설명 |
|------|------|
| 실시간 모니터링 | 포지션, 주문 현황 |
| 체결 알림 | 토스트/노티피케이션 |
| 긴급 정지 대시보드 | 리스크 상태, 킬 스위치 |

---

## 핵심 디자인 토큰 (Quick Reference)

### 색상

```css
/* 중립 */
--bg-primary: #FFFFFF;
--bg-secondary: #F8F9FA;
--text-primary: #0A0A0B;
--text-secondary: #5F6368;

/* 액센트 */
--accent-primary: #0066FF;
--color-long: #00D4AA;    /* 롱 포지션, 매수 */
--color-short: #FF3366;   /* 숏 포지션, 매도 */
--color-warning: #FFB800; /* 경고 */
--color-error: #FF3366;   /* 에러, 긴급 */
```

### 그림자 (방향성: 우하단)

```css
--shadow-md: 4px 8px 16px rgba(0, 0, 0, 0.08);
--shadow-long: 4px 8px 24px rgba(0, 212, 170, 0.20);
--shadow-short: 4px 8px 24px rgba(255, 51, 102, 0.20);
```

---

## Order UI 컴포넌트

### 1. 포지션 카드

```tsx
<div className="
  relative bg-white rounded-xl
  shadow-[4px_8px_16px_rgba(0,0,0,0.08)]
  overflow-hidden
">
  {/* Side indicator */}
  <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#00D4AA]" />
  
  <div className="p-6 pl-5">
    <div className="flex justify-between items-start">
      <div>
        <p className="text-xs text-[#9AA0A6] uppercase tracking-wider">Position</p>
        <p className="text-xl font-bold tracking-tight">BTC/USDT</p>
      </div>
      <span className="
        px-3 py-1 bg-[#E6FBF6] text-[#00D4AA]
        text-sm font-semibold rounded
        -skew-x-6
      ">
        LONG
      </span>
    </div>
    
    <div className="mt-4 grid grid-cols-2 gap-4">
      <div>
        <p className="text-xs text-[#9AA0A6]">Entry</p>
        <p className="font-mono font-medium">$43,250.00</p>
      </div>
      <div>
        <p className="text-xs text-[#9AA0A6]">PnL</p>
        <p className="font-mono font-medium text-[#00D4AA]">+$1,245.50</p>
      </div>
    </div>
  </div>
</div>
```

### 2. 체결 토스트 (Success)

```tsx
<div className="
  relative flex items-center gap-4
  px-6 py-4 bg-white rounded-lg
  shadow-[4px_8px_24px_rgba(0,212,170,0.20)]
  border-l-4 border-[#00D4AA]
">
  <div className="w-2 h-2 bg-[#00D4AA] rounded-full animate-pulse" />
  <div>
    <p className="text-sm font-medium">주문 체결 완료</p>
    <p className="text-xs text-[#5F6368]">BTC 0.05 @ $43,521.00</p>
  </div>
  
  {/* Motion streak */}
  <div className="absolute right-4 top-1/2 -translate-y-1/2
    w-6 h-0.5 bg-gradient-to-r from-[#00D4AA]/50 to-transparent" />
</div>
```

### 3. 긴급 정지 버튼

```tsx
<button className="
  relative px-8 py-4
  bg-[#FF3366] text-white
  font-bold tracking-tight uppercase
  rounded-lg
  shadow-[4px_8px_24px_rgba(255,51,102,0.30)]
  hover:shadow-[6px_12px_32px_rgba(255,51,102,0.40)]
  transition-all duration-200
  overflow-hidden
">
  {/* Directional hover effect */}
  <span className="absolute inset-0 bg-gradient-to-r 
    from-transparent via-white/20 to-transparent
    -translate-x-full hover:translate-x-full 
    transition-transform duration-500" />
  
  ⚠️ Emergency Stop
</button>
```

### 4. 주문 상태 배지

```tsx
{/* Pending */}
<span className="px-3 py-1 bg-[#E6F0FF] text-[#0066FF] 
  text-xs font-semibold uppercase tracking-wider rounded -skew-x-6">
  Pending
</span>

{/* Filled */}
<span className="px-3 py-1 bg-[#E6FBF6] text-[#00D4AA]
  text-xs font-semibold uppercase tracking-wider rounded -skew-x-6">
  Filled
</span>

{/* Cancelled */}
<span className="px-3 py-1 bg-[#FFE6EC] text-[#FF3366]
  text-xs font-semibold uppercase tracking-wider rounded -skew-x-6">
  Cancelled
</span>
```

---

## 체크리스트

- [ ] 방향성 요소 1개 이상 포함
- [ ] 그림자 단일 방향 (우하단)
- [ ] 색상: 중립 90% + 액센트 10%
- [ ] 롱/숏 색상 명확히 구분
- [ ] 긴급 상황 시 강렬한 빨간색 사용
- [ ] 숫자는 Monospace 폰트

---

*전체 가이드: [storage/docs/DESIGN_SYSTEM.md](https://github.com/vsun410/trading-platform-storage/blob/main/docs/DESIGN_SYSTEM.md)*
