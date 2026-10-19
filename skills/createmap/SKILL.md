---
name: createmap
description: Make colored maps (choropleths, election maps, category maps, heat maps) of countries, states, provinces, districts, constituencies or world regions, and return a link that opens the finished, editable map on createmymaps.com. Use when the user asks to map, color, shade or visualize data by country/state/region, wants an election or results map, a "map of X by Y", or a blank map to color in.
---

# Create My Maps

You turn a request like "map India's population by state" or "color the 2024 US election results" into a link that opens the finished map on createmymaps.com, where the user can tweak and export it as PNG, SVG or PDF.

The skill ships with the full map catalog: 458 maps and the exact region ids for each. You never draw a map yourself. You produce a small JSON spec, and `scripts/make_map.py` validates it and builds the link.

The scripts are in this skill's folder: `${CLAUDE_SKILL_DIR}` in Claude, or the folder that contains this SKILL.md elsewhere. They need Python 3 and nothing else. If you are not Claude, add `--via <your name>` (for example `--via chatgpt`) when you run `make_map.py`.

## Workflow

1. **Find the candidate maps.** Run `python3 ${CLAUDE_SKILL_DIR}/scripts/find_map.py <words>` (for example `india states`, `usa counties`, `world`, `bihar assembly`). Keep the maps whose region level matches the data. State data goes on a states map, not on a districts map. If a label says "(Old)", the "(New)" or "(updated)" version is the default for current data, for example `india-new` over `india`.
2. **Ask before building, in one message.** Unless the user has already settled these points or said "just make it", ask up to three short questions, each with numbered options and your recommended default marked. Ask only the questions whose answer would change the map:
   - **Which map**, when the search found real alternatives. Examples: for the world, the standard view or a country-specific view (India-, China-, Russia- or Morocco-centric borders, or the Great Lakes variant). For India, current or older state boundaries, or states vs constituencies. For the USA, with or without territories, states or counties.
   - **Style**: color bands (clear, readable classes) or a smooth gradient, or the categories to use. Also the color scheme or theme if it matters.
   - **Data**: whether the user has data to paste, or you should use your own knowledge or research it, and for which year.

   End with "Reply with numbers, or say **go** for the defaults." If a tool for asking multiple-choice questions is available, use it instead of plain text. Ask only once: after the reply, build without further questions. Never ask about spelling or name matching.
3. **Get the data.** Use the user's data if they gave any. Otherwise research it or use your knowledge, and say which values are estimates and from roughly which year.
4. **Choose the coloring mode** (details in `references/spec.md`):
   - `tag` (categories) for distinct classes: party, winner, status, yes/no, membership.
   - `number` (gradient) for continuous quantities: population, GDP, rates, percentages.
   - `logic` (threshold rules) for fixed bands or tiers, such as "above 50% = green".
   - `flat` when the user picks each region's color themselves.
5. **Write the spec** to a file such as `spec.json`, following `references/spec.md`. In `regions`, key each entry by region name or region id. The script matches names fuzzily, so you don't need to look up ids for well-known regions. For dense maps (hundreds of districts or constituencies), check the exact names first with `find_map.py --regions <map_id>` or by reading `references/regions/<map_id>.csv`.
6. **Build it:** `python3 ${CLAUDE_SKILL_DIR}/scripts/make_map.py spec.json`. Read the report it prints. If any names show up as unmatched or wrongly fuzzy-matched, fix those keys in the spec and run the script again.
7. **Deliver:**
   - The script prints a line starting `[Open the map](`. Copy that whole line into your reply exactly as printed, character for character. Don't retype the link, don't reorder its parameters, and don't add spaces or line breaks inside it: one wrong character breaks the map. Never show the link as a bare URL; it must stay a clickable "Open the map" link.
   - Add one or two lines on what the map shows and the data source or year.
   - Briefly list any regions left blank and any values you estimated.
   - Don't paste the spec into the reply.

If the script reports that the link is too long (very large maps with every region filled), it writes a CSV instead. Give the user that CSV and tell them to open createmymaps.com/app, create a project on the same map, and use **Import → Import Excel/CSV**.

**If you can't run code**, don't stop and don't refuse: write a plain link by hand instead, following "Plain links" in `references/spec.md`. For example: `[Open the map](https://createmymaps.com/app#p=1&map=usa-mt&mode=number&title=Schools+by+county&data=Yellowstone:120,Missoula:85)`. The app matches the region names when the link opens. Never try to hand-encode the `#z=` format.

**If exact figures would need heavy processing** (for example, adding up hundreds of records by county) and you can't do it, still make the map. Use the best figures you can reasonably get, label them clearly as estimates in your reply, and offer to rebuild the map from exact data. A clearly labeled estimated map is more useful than no map.

## Design defaults

- **Title:** always set a short `title`. Put the metric and its unit in `legend_title` (for example "Population (millions)"), not in the values.
- **Missing data:** in `number` and `logic` modes the app colors a region with no value as if it were 0. On a world map, that would color every unlisted country with the lowest color. So either fill every region (research the full list), or switch to `tag` mode with value bands plus a grey "No data" category. Don't leave regions blank in these modes unless the lowest color is honest for them.
- **Values:** plain numbers only. No `%`, no units, no thousands separators.
- **Categories:** keep to about 8. Use the conventional colors where they exist, such as US parties (Republican `#CC3433`, Democratic `#1F5AA6`) and Indian parties (BJP saffron `#FF9933`, INC `#19AAED`).
- **Gradients:** run light to dark. For values that diverge around a midpoint, use a three-stop scale (red, white, blue).
- **Colors:** use 6-digit hex and colorblind-safe palettes. Dark themes (`midnight`, `neon`, `dusk`, `ocean`, `blueprint`, `sandstone`, `forest`) need bright fills.
- **Labels:** use `labels: "full"` or `"abbr"` only when there are fewer than about 30 regions. Keep `"none"` for dense maps.
- **Annotations:** add a `source` line at the bottom (`annotations` with `position: "bottom"`) when the data has a source. Use pins sparingly, for example to mark the highest and lowest regions. A pin can name a `region` and it will be placed automatically.

## Files

- `scripts/find_map.py`: search the catalog, list a category, or print one map's regions.
- `scripts/make_map.py`: validate a spec and build the link, plus an optional `--csv` import file.
- `references/spec.md`: full spec format with an example for each mode. Read it before writing your first spec.
- `references/catalog.csv`: every map with its id, label, category, region count and canvas size.
- `references/regions/<map_id>.csv`: the valid regions for each map (id, name, and center point in map units).
