import { test, expect, type Page } from '@playwright/test';

const SITE = 'https://www.warped.games/';

const menuButton = (page: Page) =>
  page.getByRole('banner').getByRole('button').filter({ hasText: /^$/ });

const NAV_ITEMS = [
  'What is Warped?',
  'Space at your pace',
  'Team',
  'Gallery',
  'Codex',
  'Game Updates',
  'Lore',
];

test('menu opens and exposes all nav items', async ({ page }) => {
  await page.goto(SITE);
  await menuButton(page).click();

  for (const item of NAV_ITEMS) {
    await expect(page.getByRole('link', { name: item }).first()).toBeVisible();
  }
});

test('gallery route resolves', async ({ page }) => {
  await page.goto('https://www.warped.games/gallery/photos');
  await expect(page).toHaveURL(/gallery/);
  await expect(page.getByRole('button', { name: 'Photos' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Videos' })).toBeVisible();
});

test('change log link is reachable', async ({ page }) => {
  await page.goto(SITE);
  await expect(page.getByRole('link', { name: 'Change log' })).toBeVisible();
});