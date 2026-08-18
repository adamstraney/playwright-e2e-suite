# Playwright E2E Suite

End-to-end regression tests for two production sites, built with Playwright and TypeScript. Tests run in parallel across Chromium, Firefox, and WebKit.

## Sites covered

**warped.games** — game studio site for Warped Universe (Steam / Epic Early Access)
- Page load, document title, hero content
- Store conversion CTAs across three page sections (`#home`, `#info`, `#call-to-action`)
- Menu navigation, gallery routing, change log reachability
- Responsive layout at phone, tablet, and desktop widths

**breakpointmastering.com** — mastering studio site
- Page load, header branding, primary conversion CTA
- All primary nav destinations resolve
- Responsive layout at three viewport widths

## Scope decisions

Coverage is deliberately scoped to what breaks and what costs money when it breaks.

- **Store and contact CTAs are asserted present and enabled, not clicked through.** Following a store button sends the run to Steam or Epic, which makes the suite dependent on third-party uptime and produces failures that say nothing about the site under test.
- **Copy text, video, and animation are not tested.** Marketing copy changes often and media playback is inherently flaky; tests over either produce noise that trains you to ignore the suite.
- **External release links are not individually verified.** Third-party pages move for reasons unrelated to this site.
- **Repeated components use data-driven generation.** Store sections and viewport widths are defined as arrays and looped, so extending coverage is one line rather than a duplicated block.

## Running