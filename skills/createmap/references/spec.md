# Map spec format

`make_map.py` reads one JSON object. Only `map`, `mode` and `regions` are required.

| Field | Type | Notes |
|---|---|---|
| `map` | string | Map id from `find_map.py` or `catalog.csv`. |
| `mode` | `flat` \| `tag` \| `number` \| `logic` | Aliases also work: `category` = `tag`, `gradient` = `number`, `rules` = `logic`. |
| `title` | string | Map title. |
| `name` | string | Project name in the user's dashboard. Defaults to `title`. |
| `legend_title` | string | The metric and its unit, for example "GDP (US$ bn)". |
| `legend` | bool | Show the legend. Default is on for every mode except `flat`. |
| `theme` | string | `default`, `midnight`, `parchment`, `neon`, `arctic`, `dusk`, `moss`, `sandstone`, `coral`, `slate`, `sunrise`, `ocean`, `forest`, `rose`, `lavender`, `blueprint`. |
| `labels` | `none` \| `abbr` \| `full` | Region names printed on the map. Default `none`. |
| `label_display` | `label` \| `value` \| `both` | What each label shows. |
| `default_color` | hex | Fill for regions with no data. |
| `regions` | object | Keyed by region **name or id**. Values depend on the mode (below). |
| `categories` | list | `tag` mode only: `[{"name", "color", "id"?}]`. |
| `gradient` | object | `number` mode only: `{"stops": [...], "min"?, "max"?}`. |
| `rules` | list | `logic` mode only: `[{"op", "value", "color", "label"}]`. |
| `annotations` | list | Text on the map: `[{"text", "position": "top" or "bottom"}]`. You can give `x`/`y` instead of `position`, plus optional `size`, `color`, `bold` and `italic`. |
| `pins` | list | `[{"label", "region": "<name or id>", "color"?}]`, or `x`/`y` in place of `region`. |

Values in `regions`:

- `flat`: a hex color, for example `"Texas": "#CC3433"`.
- `tag`: a category name or id, for example `"Texas": "Republican"`.
- `number` and `logic`: a plain number, for example `"Texas": 30.5`.
- Any mode: an object form also works, for example `{"value": 3, "hidden": true}`. Set `"hidden": true` to remove a region from the map.

Coordinates (`x`, `y`, `size`) are in the map's own units, not pixels. Each map's canvas size is in `catalog.csv`. Prefer `position` and `region` and let the script place things. It already sizes text and pins to fit the map.

## Examples

### Category: election winner
```json
{
  "map": "usa-albers", "mode": "tag",
  "title": "2024 US Presidential Election", "legend_title": "Winner",
  "categories": [
    {"name": "Republican", "color": "#CC3433"},
    {"name": "Democratic", "color": "#1F5AA6"}
  ],
  "regions": {"Texas": "Republican", "California": "Democratic", "New York": "Democratic"},
  "annotations": [{"text": "Source: AP", "position": "bottom"}]
}
```

### Gradient: population
```json
{
  "map": "india", "mode": "number",
  "title": "India — Population by State", "legend_title": "Population (millions)",
  "gradient": {"stops": ["#FEF3C7", "#F59E0B", "#7C2D12"]},
  "regions": {"Uttar Pradesh": 240, "Maharashtra": 130, "Bihar": 125, "Sikkim": 0.7},
  "pins": [{"label": "Most populous", "region": "Uttar Pradesh"}]
}
```
Gradient `stops` can be a plain color list, which is spaced evenly, or `[{"position": 0-100, "color"}]`. The scale runs from the data's min to its max unless you set `min` and `max`.

### Logic rules: thresholds
```json
{
  "map": "world", "mode": "logic",
  "title": "Internet access", "legend_title": "Population online (%)",
  "rules": [
    {"op": ">=", "value": 90, "color": "#065F46", "label": "90%+"},
    {"op": ">=", "value": 60, "color": "#34D399", "label": "60–89%"},
    {"op": "<",  "value": 60, "color": "#FDE68A", "label": "Under 60%"}
  ],
  "regions": {"Norway": 99, "India": 52, "Brazil": 84}
}
```
Rules are checked from top to bottom and the first match wins, so put the highest band first.

### Flat colors
```json
{
  "map": "europe", "mode": "flat", "title": "Countries I've visited",
  "default_color": "#E5E7EB",
  "regions": {"France": "#10B981", "Italy": "#10B981", "Spain": "#10B981"}
}
```

## Reading the report

`make_map.py` prints a ready-made `[Open the map](…)` line to paste exactly as printed, followed by:

- **Fuzzy-matched**: names it resolved approximately. Check that they're right. For example, "Georgia" could be the US state or the country.
- **NOT matched**: names it dropped. Rename them using the region list and run the script again.
- **No data**: regions left blank. Mention these to the user if they matter.
