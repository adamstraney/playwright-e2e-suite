import { test, expect } from '@playwright/test';

const SITE = 'https://breakpointmastering.com/';

const NAV_ITEMS = [
  'Send Your Music',
  'About BreakPoint Mastering',
  'Studio',
  'Testimonials',
];

test('all primary nav links are present', async ({ page }) => {
  await page.goto(SITE);

  for (const item of NAV_ITEMS) {
    await expect(page.getByRole('link', { name: item }).first()).toBeVisible();
  }
});

for (const item of NAV_ITEMS) {
  test(`nav destination resolves: ${item}`, async ({ page }) => {
    await page.goto(SITE);
    await page.getByRole('link', { name: item }).first().click();

    // A 404 or dead route would leave us without a rendered header
    await expect(page.locator('#main-header')).toBeVisible();
  });
}

test('external credits link is present', async ({ page }) => {
  await page.goto(SITE);
  await expect(page.getByRole('link', { name: 'Hundreds of releases' })).toBeVisible();
});