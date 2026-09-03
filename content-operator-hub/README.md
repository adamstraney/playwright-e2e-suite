# The Content Operator Hub

A single-file mobile dashboard that deep-links straight into your engagement
surfaces — DMs, mentions, messages — without ever showing you a home feed.

Everything lives in `index.html`. No frameworks, no CDNs, no build step, no
internet dependencies. Open the file and it works.

## What's in it

**Batching window.** A 15-minute countdown. Green, amber under 5:00, flashing
red under 1:00, then a full-screen "close your tabs" overlay you have to
dismiss by hand. The countdown is anchored to the clock, not to a tick counter,
so it stays accurate when you tap out to a platform and come back — and it
survives the phone throwing the tab out of memory.

**Surgical gateways.** Four cards that skip the algorithmic feeds:

| Card | Destination |
| --- | --- |
| Instagram · DMs | `instagram.com/direct/inbox/` |
| X · Notifications | `x.com/notifications` |
| LinkedIn · Messages | `linkedin.com/messaging/` |
| TikTok · Activity | `tiktok.com/messages` |

Each card has a checkmark in its corner. Tap the card to go there; tap the
checkmark to mark that channel handled. The ticks reset on their own each new
day, because it's a daily routine.

**Idea sandbox.** A capture box for ideas, so a thought doesn't become a reason
to open an app. Ideas persist until you delete them — they are not cleared
daily.

## Deploying it

1. Drag this folder onto [netlify.com/drop](https://netlify.com/drop). You get
   a URL in about thirty seconds, free, no account needed to start.
2. Open that URL on your phone, then **Share → Add to Home Screen**. It gets an
   icon and opens without browser chrome, like a normal app.

To embed it in Notion, paste the same URL into a `/embed` block.

## Where your data lives

Ticks and ideas are stored in the browser's own storage, on the device, and go
nowhere else. There is no account, no server, and no analytics. Consequences
worth knowing:

- Your phone and your laptop keep separate lists. Nothing syncs between them.
- Clearing your browser data erases them.
- In a private window, or inside a sandboxed embed that blocks storage, the
  page still works fine but forgets everything when closed.

## Changing things

Everything is in one file, in three labelled blocks: `<style>` for appearance,
the markup in `<body>`, and `<script>` for behaviour.

- **A different link:** find the `href="..."` on the card you want and swap it.
- **A different length:** find `DEFAULT_SECONDS` near the top of the script.
  `15 * 60` is fifteen minutes.
- **Colour thresholds:** `AMBER_THRESHOLD` and `RED_THRESHOLD`, in seconds.

## A note on the icons

The card icons are deliberately generic line drawings, not the official
Instagram / X / LinkedIn / TikTok logos. Those logos are trademarks, and
shipping them inside a product you sell is the kind of thing that gets a
product pulled. Naming the platforms in text is fine; reproducing their brand
marks is not. Keep it that way if this is ever sold or distributed.
