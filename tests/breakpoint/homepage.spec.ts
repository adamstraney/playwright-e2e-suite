import { test, expect } from '@playwright/test';

const SITE = 'https://breakpointmastering.com/';

test.beforeEach(async ({ page }) => {
  await page.goto(SITE);
});

test('loads with correct document title', async ({ page }) => {
  await expect(page).toHaveTitle(/BreakPoint/i);
});

test('header branding is present', async ({ page }) => {
  await expect(
    page.locator('#main-header').getByRole('link', { name: 'BreakPoint Mastering', exact: true })
  ).toBeVisible();
});

test('primary conversion CTA is present', async ({ page }) => {
  await expect(page.getByRole('link', { name: 'Send Your Music' }).first()).toBeVisible();
});