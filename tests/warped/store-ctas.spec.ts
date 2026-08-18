import { test, expect } from '@playwright/test';

const SITE = 'https://www.warped.games/';

// Store CTAs repeat across three sections; all three must survive a deploy
const SECTIONS = ['#home', '#info', '#call-to-action'];

for (const section of SECTIONS) {
  test(`store buttons render and are enabled in ${section}`, async ({ page }) => {
    await page.goto(SITE);

    const steam = page.locator(section).getByRole('button', { name: 'Play on Steam' });
    const epic = page.locator(section).getByRole('button', { name: 'Play on Epic' });

    await expect(steam).toBeVisible();
    await expect(steam).toBeEnabled();

    await expect(epic).toBeVisible();
    await expect(epic).toBeEnabled();
  });
}

test('Discord CTA is present', async ({ page }) => {
  await page.goto(SITE);
  await expect(page.getByRole('button', { name: 'Join our Discord' })).toBeVisible();
});