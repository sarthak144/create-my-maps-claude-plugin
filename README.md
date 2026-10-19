# Create My Maps for Claude

Ask Claude for a map and get a link that opens it finished on [createmymaps.com](https://createmymaps.com). For example: "map India's population by state", "color the 2024 US election by winner", or "shade Europe by GDP per capita". You can then edit the map and export it as PNG, SVG or PDF.

## What it covers

- 458 maps, including the world, continents, countries, US states and counties, Indian states, assembly and parliamentary constituencies, and more.
- Four coloring styles: categories (for example election winners), gradients (for example population), threshold rules (for example percentage bands) and flat colors.
- Titles, legends, labels, source lines and pins.

## Use it

Install the plugin, then type `/createmap` or just ask Claude for a map in plain words. You can provide your own data, or ask Claude to research or estimate it. Claude picks the right map, matches every name to the exact regions, and replies with a link plus a short note on anything it couldn't match or had to estimate.

For very large maps where the link would be too long, Claude gives you a CSV instead. Open the app and use Import → Import Excel/CSV.

## Data

The skill runs entirely inside Claude. The map catalog and region lists are bundled, so it sends nothing to any server while it works. The map data lives in the link's `#` fragment, which browsers never send to the server. It reaches createmymaps.com only when you open the link, and the app reads it in your browser.

## Updating the bundled map data

The files in `skills/createmap/references/` are generated from the site's map assets by running `node tools/build-claude-plugin.js` in the site repo.
