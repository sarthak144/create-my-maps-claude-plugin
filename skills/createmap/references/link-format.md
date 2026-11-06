# Link format

A map link looks like this. Write it on one line:

```
https://createmymaps.com/app?utm_source=claude&utm_medium=plugin&utm_campaign=createmap#p=1&map=MAP&mode=MODE&title=TITLE&legend=LEGEND&data=Region:value,Region:value
```

- Keep the `?utm_…` part as shown. If you are not Claude, put your own name in `utm_source` (for example `utm_source=chatgpt`).
- Everything after `#p=1` is a list of `name=value` parameters joined with `&`. Only `map` and `data` are required.

## Parameters

| Parameter | Meaning |
|---|---|
| `map` | The map id from `catalog.json`. Required. |
| `mode` | `tag` (categories), `number` (gradient), `logic` (threshold rules) or `flat` (a color per region). If you leave it out, it's guessed from the other parameters. |
| `data` | `Region:value` pairs separated by commas. Required. The value is a category name (`tag`), a plain number (`number`, `logic`), or a hex color without `#` (`flat`). |
| `cats` | `tag` mode: the categories and their colors, `Name:HEX,Name:HEX`. Every category used in `data` must be listed here. |
| `colors` | `number` mode: gradient stops from low to high, for example `FEF3C7,F59E0B,7C2D12`. Default: light to dark blue. |
| `min`, `max` | `number` mode: fix the ends of the scale. Default: the lowest and highest values in `data`. |
| `rules` | `logic` mode: rules checked in order, first match wins, for example `ge90:065F46:90+or+more,ge60:34D399:60-89,lt60:FDE68A:Under+60`. Operators: `ge` (≥), `gt` (>), `le` (≤), `lt` (<), `eq` (=). Put the highest band first. |
| `title` | The map title. |
| `legend` | The legend heading: the metric and its unit, for example `Population+(millions)`. |
| `desc` | One sentence describing the map. |
| `source` | Where the data comes from, for example `World+Bank+2023`. |
| `theme` | `default`, `midnight`, `parchment`, `neon`, `arctic`, `dusk`, `moss`, `sandstone`, `coral`, `slate`, `sunrise`, `ocean`, `forest`, `rose`, `lavender` or `blueprint`. |
| `labels` | `abbr` or `full` to print region names on the map. Leave it out for no labels. |

## Writing rules

- **Spaces** become `+`: `title=Population+by+state`.
- **Never** put `#`, `%`, `&` or `=` inside a value. They break the link. Write "pct" instead of "%", and "and" instead of "&".
- **Region names:** use the region's usual name or its exact name from the regions file. Small spelling slips are fine, because the app matches names leniently. If a name contains a comma, or two regions share a name, use the region's id from the regions file instead.
- **Colors** are 6-digit hex without `#`: `CC3433`.
- **Numbers** are plain: `52.3`, not `52.3%` or `1,200`.
- Regions you leave out of `data` stay uncolored. When the map opens, the app lists any names it couldn't match.
- Deliver the link as `[Open the map](…)`, never as a bare URL, with no spaces or line breaks inside it.

## Examples

Category (`tag`):

```
[Open the map](https://createmymaps.com/app?utm_source=claude&utm_medium=plugin&utm_campaign=createmap#p=1&map=usa-albers&mode=tag&title=2024+US+Presidential+Election&legend=Winner&cats=Republican:CC3433,Democratic:1F5AA6&data=Texas:Republican,Florida:Republican,California:Democratic,New+York:Democratic&source=AP)
```

Gradient (`number`):

```
[Open the map](https://createmymaps.com/app?utm_source=claude&utm_medium=plugin&utm_campaign=createmap#p=1&map=india-new&mode=number&title=India+population+by+state&legend=Population+(millions)&colors=FEF3C7,F59E0B,7C2D12&data=Uttar+Pradesh:240,Maharashtra:130,Bihar:125,Sikkim:0.7&source=Census+estimates+2024)
```

Threshold rules (`logic`):

```
[Open the map](https://createmymaps.com/app?utm_source=claude&utm_medium=plugin&utm_campaign=createmap#p=1&map=world&mode=logic&title=Internet+access&legend=Population+online+(pct)&rules=ge90:065F46:90+or+more,ge60:34D399:60-89,lt60:FDE68A:Under+60&data=Norway:99,Brazil:84,India:52)
```

A color per region (`flat`):

```
[Open the map](https://createmymaps.com/app?utm_source=claude&utm_medium=plugin&utm_campaign=createmap#p=1&map=europe&mode=flat&title=Countries+I+have+visited&data=France:10B981,Italy:10B981,Spain:10B981)
```

US counties need their ids, because every county name contains a comma:

```
[Open the map](https://createmymaps.com/app?utm_source=claude&utm_medium=plugin&utm_campaign=createmap#p=1&map=usa-all-counties&mode=number&title=Example&data=02185:12,02188:30)
```

## Very large maps

A link with more than about 300 regions gets too long to paste reliably. Instead, give the user an import file: a `.csv` file in this format.

```
# Map: usa-all-counties
# Mode: number
# Map Title: Median household income by county
# Legend Title: Income (US$ thousands)
# Gradient Stops: [{"position":0,"color":"#DBEAFE"},{"position":100,"color":"#1D4ED8"}]
# Gradient Value Mode: value
# Gradient Min: 20
# Gradient Max: 150
# REGION_DATA
id,name,value,visible
02185,"North Slope, AK",88.1,1
02188,"Northwest Arctic, AK",61.4,1
```

- `# Mode:` is `tag`, `number`, `logic` or `flat`. The `# REGION_DATA` columns are `id,name,value,visible` for `number` and `logic`, `id,name,tag,visible` for `tag`, and `id,name,color,visible` for `flat` (hex with `#`).
- For `tag` mode, list the categories before `# REGION_DATA`:

  ```
  # TAGS
  tag_id,tag_name,tag_color
  rep,Republican,#CC3433
  dem,Democratic,#1F5AA6
  ```

- For `logic` mode, list the rules before `# REGION_DATA`:

  ```
  # LOGIC_RULES
  operator,value,color,label
  >=,90,#065F46,90 or more
  <,60,#FDE68A,Under 60
  ```

- Use the ids and names from the regions file, and quote any name that contains a comma.
- Tell the user to open createmymaps.com/app, choose **Import → Import Excel data** on the dashboard, and pick the file. The app shows a preview, then creates the map from it.
