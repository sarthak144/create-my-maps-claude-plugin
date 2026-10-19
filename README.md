# Create My Maps for Claude and ChatGPT

Ask Claude for a map and get a link that opens it finished on [createmymaps.com](https://createmymaps.com). For example: "map India's population by state", "color the 2024 US election by winner", or "shade Europe by GDP per capita". You can then edit the map and export it as PNG, SVG or PDF.

## What it covers

- 458 maps, including the world, continents, countries, US states and counties, Indian states, assembly and parliamentary constituencies, and more.
- Four coloring styles: categories (for example election winners), gradients (for example population), threshold rules (for example percentage bands) and flat colors.
- Titles, legends, labels, source lines and pins.

## Use it

The same plugin works in Claude (`.claude-plugin/plugin.json`) and ChatGPT (`plugin.json`). Both use the skill in `skills/createmap/`.


Install the plugin, then type `/createmap` or just ask Claude for a map in plain words. You can provide your own data, or ask Claude to research or estimate it. Claude picks the right map, matches every name to the exact regions, and replies with a link plus a short note on anything it couldn't match or had to estimate.

For very large maps where the link would be too long, Claude gives you a CSV instead. Open the app and use Import → Import Excel/CSV.

## Data

The plugin itself sends nothing anywhere. The map catalog and region lists are bundled, the scripts run inside Claude's sandbox with no network calls, and the plugin stores no data. Claude's only output is a link.

The map's contents are carried in the link's `#` fragment, which browsers don't send to servers. When you open the link, createmymaps.com builds the map in your browser. From then on, the site's own practices apply as for any visitor: it records anonymous usage analytics (including that the visit came from Claude), and if you export or share a map, it saves a copy of that map on its server.

## Updating the bundled map data

The files in `skills/createmap/references/` are generated from the site's map assets by running `node tools/build-claude-plugin.js` in the site repo.
