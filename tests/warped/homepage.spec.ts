import { test, expect } from '@playwright/test';

const SITE = 'https://www.warped.games/';

test.beforeEach(async ({ page }) => {
  await page.goto(SITE);
});

test('loads with correct document title', async ({ page }) => {
  await expect(page).toHaveTitle(/Warped/i);
});

test('hero section renders', async ({ page }) => {
  await expect(page.getByText('Warped Universe').first()).toBeVisible();
});

test('header shows Portal entry point', async ({ page }) => {
  await expect(page.getByRole('button', { name: 'Portal' })).toBeVisible();
});

test('contact email is present', async ({ page }) => {
  await expect(page.getByRole('link', { name: 'ops@warped.games' })).toBeVisible();
});