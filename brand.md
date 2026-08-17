# Cache — Brand Guidelines

_Living document. Visual identity: moodboard, color, type, imagery direction. Separate from `cache-roadmap.md` (technical build) and `strategy.md` (product strategy)._

---

## Moodboard

Sourced from the original brand moodboard. Organized into three throughlines rather than as a flat image dump — these are the actual directions the visuals point toward, not just a mood collage.

### 1. Retro / analog computing
The literal "cache" pun made physical — old terminals, CRT phosphor screens, computer labs bathed in afternoon light.

![CRT terminal, hands typing](brand-assets/crt-terminal-typing.jpg)
*Green phosphor terminal text — direct reference for "old computer screen green"*

![Vintage monitor on a desk in afternoon light](brand-assets/afternoon-light-desk.jpg)
*Warm, low-angle afternoon light — the "afternoon light" note, literally*

![Computer lab, row of green-screen monitors](brand-assets/computer-lab-row.jpg)
*Same warm light + green screens combined in one frame*

![Someone using an old computer alone in a grass field](brand-assets/grass-field-offline.jpg)
*The "play on offline" note — surreal, slightly funny, the tension between old tech and the natural/analog world*

![Red-walled room with two green CRT screens](brand-assets/red-room-crt.jpg)
*Bridges retro-tech and the warm red/orange notes in one image — useful reference for how the two throughlines can coexist*

![Vintage mainframe on red flooring, 1970s](brand-assets/vintage-mainframe-red.jpg)
*Same bridge — retro computing hardware, red as the dominant environmental color*

_Also in the original board, not reproduced here due to visible third-party branding/trademarks: a Macintosh 128K "Think Different" print ad, and an IBM 5100 Portable Computer (1975) promotional poster. Both reinforce the same retro-computing throughline — worth keeping as private reference, not as assets in a shared brand doc._

### 2. Treasure / hidden value
The emotional core of the product thesis — you own more value than you realize. Warmth, gold, things worth finding.

![Treasure chest full of gold coins by candlelight](brand-assets/treasure-chest-gold.jpg)
*Direct "treasure trove / pirates" reference*

![Honeycomb with bees](brand-assets/honeycomb-bees.jpg)
*"Beehive / honeycomb" — value that's been quietly, methodically accumulated*

![Squirrel hoarding a nut](brand-assets/squirrel-hoarding.jpg)
*Playful stand-in for the hoarding/accumulation instinct — the product's whole thesis is making that instinct visible and useful*

![Golden hallway lit by low sun](brand-assets/golden-hallway.jpg)
*"Luxury orange? red?" and "afternoon light" overlapping — warmth as a physical, architectural quality, not just a color swatch*

![Red tile shower, warm lighting](brand-assets/red-tile-shower.jpg)
*"Luxury orange? red?" at its most literal — saturated, warm, a little indulgent*

### 3. Browsing / discovery
Secondary theme — less directly actionable for color/type decisions, but worth keeping as texture reference for how "browsing what you own" could feel.

![Retro grocery store aisle, red stools](brand-assets/retro-store-aisle.jpg)

![Video/DVD rental store aisle](brand-assets/video-store.jpg)

![Grid of lit apartment windows at night](brand-assets/lit-windows-night.jpg)
*Many small, separately-lit "collections" — an interesting metaphor for a personal inventory, even if it doesn't map directly to color*

---

## Vibe notes (from the original board)

These were the loose annotations alongside the images — kept verbatim since they're the actual language to work from, not paraphrased:

- luxury orange? red?
- retro technology - play on "cache"
- play on offline
- afternoon light
- old computer screen green
- treasure trove / pirates....
- emerald green
- beehive / honeycomb
- gold

---

## Open: Color & Type Direction

**Extracted palette (from `colors1.pdf`, sampled directly from pixel values — no hex labels existed in the source file):**

- Reds/oranges/pinks: `#C91B46` (cherry), `#E14C1A`, `#E76607`, `#D64F7C`
- Greens: `#527162`, `#779781`, `#A1B89C`, `#3D5A48`, `#4F6753`, `#6E8243`
- Dark maroons/browns: `#260503`, `#50130E`, `#852B00`, `#420902`
- Tans/creams/golds: `#C7A872`, `#C7B585`, `#E3D9C9`, `#FDF6ED`, `#F4B652`, `#F4C968`, `#FEEF77`, `#F1C010`

**Keyword-driven directions (offline/physical world, safety, sharing/community), first pass:**
- **A — Hearth:** primary `#E14C1A`, secondary `#3D5A48`, accent `#F1C010`, base `#FDF6ED`. Community via warmth/hearth read.
- **B — Safety Amber:** primary `#F1C010`, secondary `#527162`, accent `#D64F7C`, base `#E3D9C9`. Leans into amber as a literal, distinctive "safety" read (most apps default to blue for trust — this is a deliberate departure).
- **C — Root & Canopy:** primary `#4F6753`, secondary `#852B00`, accent `#D64F7C`, base `#E3D9C9`. Green carries "safety" conventionally; safest/least surprising of the three.

**Cherry-forward directions (`#C91B46`), second pass:**
- **D — Cherry & Pine:** primary `#C91B46`, secondary `#3D5A48`, accent `#F1C010`, base `#FDF6ED`, text `#260503`. Cherry as dominant primary — bold, high-commitment.
- **E — Cherry & Gold:** primary `#C91B46`, secondary `#F4B652`, accent `#527162`, base `#E3D9C9`, text `#420902`. Jewel-tone pairing, ties to the treasure throughline. Gold-on-tan contrast needs verifying before finalizing.
- **F — Cherry as accent:** primary `#4F6753`, secondary `#852B00`, accent `#C91B46` (used rarely — key CTAs/highlights only), base `#E3D9C9`, text `#260503`. Avoids the error-state collision risk below entirely, since cherry never dominates.

**Real constraint on any cherry-forward direction:** saturated red is the near-universal error/danger signal in interfaces. If `#C91B46` becomes the dominant primary (D, E), the actual error/validation states (already spec'd — inline red border + icon) need to stay visually distinct from brand-red, or the two meanings blur. F sidesteps this by keeping cherry rare.

Rendered as login-screen mockups (D, E, F) — D reads cleanest at a glance; E's gold-on-tan base needs a contrast check; F makes cherry's rarity feel more intentional/higher-signal.

**Third pass — refined variations:**
- **F′:** primary `#3D5A48` (darker pine, swapped in for `#4F6753`), secondary `#852B00`, accent `#C91B46` (rare), base `#FDF6ED`, text `#260503`.
- **D′:** primary `#C91B46`, secondary `#3D5A48` (unchanged from D), accent swapped from gold `#F1C010` to `#6E8243` (olive-lime green) — gold and cherry are both warm hues and sit close together on the color wheel, so they read as *similar* rather than contrasting; green sits closer to cherry's complementary opposite, producing genuine optical pop rather than "another warm tone."

**Font pairing test, both variations rendered both ways:**
- Current fonts (Roboto Mono body + Rubik Mono One-style header): terminal/retro-tech identity is present in every line of text, not just the wordmark — reinforces the brand consistently but reads more technical throughout.
- Alt fonts (Roboto Mono header only + Archivo body): noticeably more approachable/scannable as a normal app; the wordmark still carries a technical accent, but body copy reads soft. Real tradeoff between full retro-tech immersion and everyday usability — not yet decided.

## FINAL: Visual Identity — used across all screens

**Color — D′:** primary `#C91B46` (cherry), secondary `#3D5A48` (pine), accent `#6E8243` (olive-lime), base `#FDF6ED` (cream), text `#260503` (near-black maroon), **error/danger `#E76607`** (vivid orange — deliberately separated from cherry on the color wheel, so brand-red and error-red never blur together).

**Type:**
- Body/UI text: **Inter**
- Brand wordmark: **"cache"**, always lowercase (wordmark AND any body-text mention), in **Unbounded** (Black/900 weight).

**User schema addition:** `profile_photo_url` (string, nullable) — tap the avatar on the Profile screen to change it, same compress-before-upload pattern (canvas resize + JPEG quality ~0.7) as item photos.

**Color role clarifications (post-mockup review):**
- Monetary figures (total cache value, resale estimates, price deltas) stay **cherry** `#C91B46` for now — pink-leaning red was flagged as a possible mismatch, alternatives (olive, pine, rust) were rendered for comparison, but decision is to keep cherry and revisit later rather than commit now.
- **Olive-lime `#6E8243`'s role:** category tags/badges (item detail, item cards) and filter checkbox selected-state. This was underused across the full mockup pass (only appeared twice — a link and a success delta) — giving it a consistent, repeated job across every screen with items fixes that without touching the money-color decision above.

---

## Type

- **Body/UI text — under evaluation, three options tested:**
  - **Roboto Mono:** current default. Terminal/retro-tech identity present in every line, not just the wordmark. Most "technical" feeling of the three.
  - **Archivo:** original system font. Most approachable/scannable; wordmark carries the technical accent alone, body reads soft.
  - **Inter:** neutral, screen-optimized, no strong personality of its own — lets the wordmark carry all the brand character. Middle ground between the other two.
- **Brand wordmark:** "cache," in a thick/blocky display face inspired by Rubik Mono One. This does not change regardless of which body font is chosen.
- **Standing rule:** "cache" is always lowercase — in the wordmark/logo treatment AND in any body-text mention of the brand name. Applies everywhere, not just the header.
