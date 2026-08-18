import { test, expect } from '@playwright/test';

const SITE = 'https://breakpointmastering.com/';

const VIEWPORTS = [
  { name: 'phone', width: 390, height: 844 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1440, height: 900 },
];

for (const vp of VIEWPORTS) {
  test(`renders without horizontal overflow at ${vp.name} (${vp.width}px)`, async ({ page }) => {
    await page.setViewportSize({ width: vp.width, height: vp.height });
    await page.goto(SITE);

    const hasOverflow = await page.evaluate(() =>
      document.documentElement.scrollWidth > document.documentElement.clientWidth
    );

    expect(hasOverflow).toBe(false);
  });
}