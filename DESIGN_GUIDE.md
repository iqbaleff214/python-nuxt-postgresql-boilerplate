# UI/UX Design Guide

## Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `bg-base` | `#F5F7FA` | Page background |
| `bg-surface` | `#FFFFFF` | Cards, inputs, nav |
| `text-primary` | `#0F1117` | Headings, main text |
| `text-secondary` | `#6B7280` | Subtitles, URLs, muted labels |
| `btn-primary` | `#1A1F36` | Primary CTA (Analyze, View) |
| `btn-primary-text` | `#FFFFFF` | Text on dark buttons |
| `accent-link` | `#2563EB` | Inline links, "View All →" |
| `status-processing-bg` | `#DBEAFE` | Processing badge bg |
| `status-processing-text` | `#1D4ED8` | Processing badge text |
| `status-completed-bg` | `#D1FAE5` | Completed badge bg |
| `status-completed-text` | `#065F46` | Completed badge text |
| `status-archived-bg` | `#F3F4F6` | Archived badge bg |
| `status-archived-text` | `#6B7280` | Archived badge text |
| `border` | `#E5E7EB` | Input borders, dividers |

---

## Typography

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Logo wordmark | 16px | 700 | `text-primary` |
| Nav links | 14px | 500 | `text-primary` (active has underline) |
| Hero heading | 40–48px | 800 | `text-primary` |
| Hero subtitle | 16px | 400 | `text-secondary` |
| Section title | 20px | 700 | `text-primary` |
| Section subtitle | 13px | 400 | `text-secondary` |
| List item title | 14px | 600 | `text-primary` |
| List item URL | 12px | 400 | `text-secondary` |
| Status badge | 11px | 600 | (per status token) |
| Button text | 14px | 600 | `btn-primary-text` |

Font family: System UI stack — `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`

---

## Spacing System

Base unit: `4px`

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 4px | Tight gaps |
| `space-2` | 8px | Icon–label gap, badge padding |
| `space-3` | 12px | Input padding |
| `space-4` | 16px | Section inner padding |
| `space-6` | 24px | Between list items |
| `space-8` | 32px | Section vertical gap |
| `space-16` | 64px | Hero top/bottom padding |

---

## Border Radius

| Element | Radius |
|---------|--------|
| Search input | `9999px` (pill) |
| Primary button | `9999px` (pill) |
| Status badges | `9999px` (pill) |
| Secondary "Details" button | `6px` |
| Floating chat button | `9999px` (circle) |
| List item icon container | `6px` |

---

## Component Specs

### Navigation Bar

- Height: `56px`
- Layout: `logo | nav-links (center) | icons (right)`
- Background: `bg-surface`
- Bottom border: `1px solid border`
- Active nav link: underline, font-weight 700
- Right icons: bell (notification), user avatar — `24px`, `text-secondary`

### Hero Section

- Max width: `640px`, centered
- Vertical padding: `space-16` top and bottom
- Heading: centered, `40–48px`, bold
- Subtitle: centered, `16px`, `text-secondary`, max-width `420px`
- Gap heading → subtitle: `space-4`
- Gap subtitle → search input: `space-8`

### Search Input

- Full width within max-width container
- Height: `52px`
- Background: `bg-surface`
- Border: `1px solid border`
- Border radius: pill
- Left icon: chain-link icon, `text-secondary`, `space-3` padding
- Placeholder: `text-secondary`, `14px`
- Right: "Analyze →" button (pill, `btn-primary`, includes arrow icon)
- Gap below input → platform chips: `space-4`

### Platform Chips

- Layout: horizontal row, centered, `space-3` gap between chips
- Each chip: platform icon + uppercase label (`11px`, `600`)
- Color: `text-secondary` with brand icon
- No background/border — text-only style

### List Items (Recent Analyses)

- Layout: `[icon] [title + url] [spacer] [status badge] [action button]`
- Vertical padding: `space-4` per item
- Divider: `1px solid border` between items
- Icon container: `32×32px`, `6px` radius, platform brand color bg
- Title: `14px / 600 / text-primary`
- URL: `12px / 400 / text-secondary`, truncated with ellipsis
- Status badge: pill, `11px / 600`, padding `4px 10px`
- Action: "View" = `btn-primary` pill button; "Details" = ghost/text button

### Status Badges

```
PROCESSING → blue bg + blue text
COMPLETED  → green bg + green text
ARCHIVED   → gray bg + gray text
```

### Section Header

- Layout: `[title + subtitle (left)] [View All History → (right)]`
- Gap between section header and list: `space-4`
- "View All →": `accent-link`, `13px`, `500`

### Floating Chat Button

- Position: `fixed`, bottom-right, `space-6` margin
- Size: `auto`, pill shape with icon + label
- Background: `btn-primary`
- Icon: star/sparkle, `16px`
- Label: "CURATOR AI / Ask for insights", `11px / 600`

---

## Layout & Grid

- Max content width: `800px`
- Horizontal padding (mobile): `space-4` each side
- Section max-width: `640px` for hero, `full` for list
- All sections horizontally centered

---

## Interaction States

| State | Treatment |
|-------|-----------|
| Button hover | Lighten bg ~10%, cursor pointer |
| Input focus | `2px` outline `accent-link`, remove default |
| Nav link active | Underline + weight 700 |
| List item hover | Subtle bg `#F9FAFB` |
| Link hover | Underline |

---

## Do / Don't

| Do | Don't |
|----|-------|
| Use pill radius on all user-action elements | Use sharp corners on buttons/badges |
| Keep hero centered, generous whitespace | Crowd hero with extra elements |
| Truncate URLs with ellipsis | Show full long URLs in list |
| Use status token colors exactly | Use arbitrary colors for status |
| Icon + label for platform chips | Text-only platform labels |
