---
name: createmap
description: Make colored maps (choropleths, election maps, category maps, heat maps) of countries, states, provinces, districts, constituencies or world regions, and return a link that opens the finished, editable map on createmymaps.com. Use when the user asks to map, color, shade or visualize data by country/state/region, wants an election or results map, a "map of X by Y", or a blank map to color in.
---

# Create My Maps

You turn a request like "map India's population by state" or "color the 2024 US election results" into a link that opens the finished map on createmymaps.com, where the user can tweak it and export it as PNG, SVG or PDF.

You never draw a map yourself. You write one link that names the map, the coloring and each region's value, following `references/link-format.md`. When the link opens, the app matches the region names and builds the map. No code is needed.

This skill ships with the full map catalog in this skill's folder: 458 maps and the exact regions of each.

## Workflow

1. **Find the candidate maps.** Search `references/catalog.json` by keyword (for example "India", "Counties", "Assembly", "World"). Each line is one map: its id, label, category, region count and the regions file that lists its regions. Keep the maps whose region level matches the data. State data goes on a states map, not on a districts map. If a label says "(Old)", the "(New)" or "(updated)" version is the default for current data, for example `india-new` over `india`.
2. **Ask before building, in one message.** Unless the user has already settled these points or said "just make it", ask up to three short questions, each with numbered options and your recommended default marked. Ask only the questions whose answer would change the map:
   - **Which map**, when the search found real alternatives. Examples: for the world, the standard view or a country-specific view (India-, China-, Russia- or Morocco-centric borders, or the Great Lakes variant). For India, current or older state boundaries, or states vs constituencies. For the USA, with or without territories, states or counties.
   - **Style**: color bands (clear, readable classes) or a smooth gradient, or the categories to use. Also the color scheme or theme if it matters.
   - **Data**: whether the user has data to paste, or you should use your own knowledge or research it, and for which year.

   End with "Reply with numbers, or say **go** for the defaults." If a tool for asking multiple-choice questions is available, use it instead of plain text. Ask only once: after the reply, build without further questions. Never ask about spelling or name matching.
3. **Get the data.** Use the user's data if they gave any. Otherwise research it or use your knowledge, and say which values are estimates and from roughly which year.
4. **Choose the coloring mode** (details in `references/link-format.md`):
   - `tag` (categories) for distinct classes: party, winner, status, yes/no, membership.
   - `number` (gradient) for continuous quantities: population, GDP, rates, percentages.
   - `logic` (threshold rules) for fixed bands or tiers, such as "above 50% = green".
   - `flat` when the user picks each region's color themselves.
5. **Check the region names.** For well-known regions (countries, US states, Indian states) use their usual names. For dense or unfamiliar maps (counties, districts, constituencies), look up the map's regions in its regions file (named in `catalog.json`) and use those exact names. Use the region's id instead when its name contains a comma (all US county names do, such as "North Slope, AK") or when two regions share a name.
6. **Write the link** following `references/link-format.md`.
7. **Deliver:**
   - Give the link as a clickable markdown link, `[Open the map](https://createmymaps.com/app?…#p=1&…)`. Never show it as a bare URL, and keep it on one line with no spaces inside.
   - Add one or two lines on what the map shows and the data source or year.
   - Briefly list any regions left blank and any values you estimated.

**If the map has hundreds of regions with data**, a link gets too long to paste reliably. Past about 300 regions, give the user an import file instead, as described under "Very large maps" in `references/link-format.md`.

**If exact figures would need heavy processing** (for example, adding up hundreds of records by county) and you can't do it, still make the map. Use the best figures you can reasonably get, label them clearly as estimates in your reply, and offer to rebuild the map from exact data. A clearly labeled estimated map is more useful than no map.

## Design defaults

- **Title, description and source:** always set a short `title`. Add a one-sentence `desc` and the data `source` when you have them. Put the metric and its unit in `legend` (for example "Population (millions)"), not in the values.
- **Missing data:** in `number` and `logic` modes the app colors a region with no value as if it were 0. On a world map, that would color every unlisted country with the lowest color. So either fill every region (research the full list), or switch to `tag` mode with value bands plus a grey "No data" category. Don't leave regions blank in these modes unless the lowest color is honest for them.
- **Unlisted regions in `tag` mode** keep the map's default fill (light blue in the default theme). Don't give a category a similar light blue, or add a grey "No data" category for the rest.
- **Values:** plain numbers only. No `%`, no units, no thousands separators.
- **Categories:** keep to about 8. Use the conventional colors where they exist, such as US parties (Republican `CC3433`, Democratic `1F5AA6`) and Indian parties (BJP saffron `FF9933`, INC `19AAED`).
- **Gradients:** run light to dark. For values that diverge around a midpoint, use a three-stop scale (red, white, blue).
- **Colors:** use 6-digit hex and colorblind-safe palettes. Dark themes (`midnight`, `neon`, `dusk`, `ocean`, `blueprint`, `sandstone`, `forest`) need bright fills.
- **Labels:** use `labels=full` or `labels=abbr` only when there are fewer than about 30 regions. Leave labels off for dense maps.

## Files

- `references/link-format.md`: the link format, with an example for each mode and the import-file format for very large maps. Read it before writing your first link.
- `references/catalog.json`: every map, one per line, with its id, label, category, region count and regions file.
- `references/regions/*.json`: the regions of every map as `[id, name]` pairs, one per line, grouped by category. India is split over three files.
