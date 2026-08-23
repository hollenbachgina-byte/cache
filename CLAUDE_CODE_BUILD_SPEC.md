# Cache — CS50 Build Specification

_Consolidated, execution-ready spec for Claude Code. Full scope as designed — nothing trimmed. Source docs: `cache-roadmap.md` (decision history/rationale) and `brand.md` (visual identity history) — this file is the buildable summary of both; if anything here conflicts with those, this file wins since it's the most recent consolidation._

---

## 1. Overview

Cache is a consumer app for passive purchase capture and personal inventory value tracking. This build covers full Phase 1 scope: register, login, see cache (dashboard + filters), add to cache (manual), item detail, delete, profile + collections, and a stubbed Sell tab. Auto-parse, real listing creation, and Stripe are explicitly out of scope — see Section 9.

---

## 2. Tech Stack

- **Backend:** Flask, SQLAlchemy, Flask-Migrate (Alembic), Flask-Admin, Flask-Login, Werkzeug (password hashing)
- **Database + storage:** Supabase (Postgres + Storage bucket for item photos)
- **Hosting:** Render (long-running Flask/gunicorn process)
- **Frontend:** Jinja2 templates, vanilla JS (canvas-based image compression, count-up animation on the success screen). No frontend framework/build step.
- **Fonts:** Google Fonts CDN — Inter (body), Unbounded (wordmark only)
- **Key Python packages:** `flask`, `flask-sqlalchemy`, `flask-migrate`, `flask-admin`, `flask-login`, `psycopg2-binary`, `python-dotenv`, `phonenumbers` (phone normalization), `Pillow` (server-side image validation/safety net)

---

## 3. Environment Setup

**.env variables:**
```
DATABASE_URL=<Supabase Postgres connection string>
SUPABASE_URL=<project URL>
SUPABASE_SERVICE_KEY=<service role key, for storage uploads from the server>
SUPABASE_STORAGE_BUCKET=item-photos
SECRET_KEY=<Flask session secret>
```

**Suggested folder structure:**
```
/app
  /models       (user.py, item.py, resale_rate.py, collection.py)
  /routes       (auth.py, cache.py, items.py, profile.py, collections.py, sell.py)
  /templates    (base.html + one template per screen, see Section 6)
  /static
    /css        (tokens.css — brand variables from Section 7)
    /js         (image-compress.js, count-up.js, filters.js)
  admin.py      (Flask-Admin ModelViews)
  config.py
  __init__.py   (app factory, extensions init)
/migrations     (Flask-Migrate)
requirements.txt
run.py
```

---

## 4. Data Model

**User**
- `id` (PK)
- `phone_number` (string, unique, indexed — normalized via `phonenumbers` before save/lookup)
- `password_hash` (string)
- `created_at` (datetime, default now)
- `cache_email` (string, nullable — reserved for Phase 2, do not build UI for it)
- `profile_photo_url` (string, nullable — Supabase Storage public URL; tap avatar on Profile screen to upload/change, same client-side compression pattern as item photos)

**Item**
- `id` (PK)
- `user_id` (FK → User)
- `name` (string)
- `brand` (string, nullable)
- `date_purchased` (date)
- `price_purchased` (decimal)
- `photo_url` (string — Supabase Storage public URL)
- `description` (text, nullable)
- `category` (string — matches `ResaleRate.category`)
- `status` (enum: `Captured`, `Surfaced`, `Listed`, `Sold` — always `Captured` in Phase 1, but define all four now)
- `source` (enum: `manual`, `auto` — always `manual` in Phase 1)
- `created_at` (datetime, default now)

**ResaleRate** (admin-managed via Flask-Admin, not user-facing)
- `category` (string, unique — include a `default` row as fallback)
- `multiplier` (float, default `0.60`)

**Collection**
- `id` (PK)
- `user_id` (FK → User)
- `name` (string)
- `created_at` (datetime, default now)

**CollectionItem** (join table, many-to-many)
- `collection_id` (FK → Collection)
- `item_id` (FK → Item)

**Resale value calculation (not stored):** for a given item, `resale_value = item.price_purchased * ResaleRate.multiplier` where the multiplier is looked up by `item.category`, falling back to the `default` row if no match exists. Compute this at render time everywhere it's displayed (item cards, item detail, total cache value, success screen) — never persist it, so admin changes to `ResaleRate` apply retroactively with no recompute job.

---

## 5. Routes

| Method | Path | Auth | Behavior |
|---|---|---|---|
| GET/POST | `/register` | No | Splash → phone+password form. On submit: validate uniqueness + password length, hash password, create User, log in, redirect to success screen → `/` |
| GET/POST | `/login` | No | Phone+password form. On success: create session, redirect to `/`. On failure: inline error (see Section 8) |
| GET | `/logout` | Yes | Clear session, redirect to `/login` |
| GET | `/` | Yes | See Cache dashboard. Accepts `?category=` query param(s) for filtering (multi-select) |
| GET/POST | `/add` | Yes | Add-item form. On submit: compress+upload photo to Supabase Storage, create Item (`status=Captured`, `source=manual`), show success screen with count-up animation, redirect to `/` |
| GET | `/item/<id>` | Yes, owner only | Item detail — both purchase price and computed resale value shown |
| POST | `/item/<id>/delete` | Yes, owner only | Delete after confirmation modal, redirect to `/` |
| GET | `/profile` | Yes | Profile picture (placeholder icon), name, "Caching since [date]", cache value, My Collections list |
| POST | `/collections` | Yes | Create a named collection |
| GET | `/collections/<id>` | Yes, owner only | View items in a collection |
| POST | `/collections/<id>/add_item` | Yes, owner only | Add an item to a collection (item can belong to multiple) |
| GET | `/sell` | Yes | Stub page — muted styling, "Coming soon" tag, no functionality |

Any protected route hit while logged out redirects to `/login`.

---

## 6. Screens (build one Jinja2 template per row)

| Screen | Route | Key elements |
|---|---|---|
| Splash | part of `/register` | Wordmark, tagline, "Create my Cache" / "Sign in" |
| Register form | `/register` | Phone, password, confirm password |
| Register success | `/register` (post-submit) | Confirmation, redirect to `/` |
| Login | `/login` | Phone, password, inline error states |
| See Cache (dashboard) | `/` | Total cache value (top), filters dropdown, 2-col item grid, sticky "+" button (bottom-right), empty state when 0 items |
| Add item | `/add` | Photo upload (with compression + spinner), name, brand, category, date, price, description |
| Add-item success | `/add` (post-submit) | "Success!" header, count-up animation from previous total → new total, "+$[value] this item" settled below, "Back to my Cache" |
| Item detail | `/item/<id>` | Back/⋮ header (⋮ → Delete), image, name/brand/date, purchase price + resale value stacked, description, category tag |
| Delete confirmation | modal on item detail | "Delete item?" / "This can't be undone" — Delete / Cancel |
| Profile | `/profile` | Avatar placeholder, name, "Caching since," cache value, My Collections list |
| Collection detail | `/collections/<id>` | Items in that collection |
| Sell (stub) | `/sell` | Muted/greyed styling, "Coming soon" tag |
| Bottom nav | all authenticated screens | My Cache / Sell / Profile |

---

## 7. Visual Identity — apply to every screen above

**Color tokens:**
```css
--color-primary: #C91B46;    /* cherry — primary CTAs AND monetary figures (total value, resale price, deltas) */
--color-secondary: #3D5A48;  /* pine — secondary elements, links, navigation */
--color-accent: #6E8243;     /* olive-lime — category tags/badges, filter checkbox selected-state */
--color-base: #FDF6ED;       /* cream — page background */
--color-text: #260503;       /* near-black maroon — primary text */
--color-error: #E76607;      /* vivid orange — validation/error states, deliberately distinct from primary */
```

**Color role discipline — each color has one job, don't mix them:**
- Cherry: primary actions (buttons) + money (totals, prices, deltas)
- Pine: secondary/structural (links, nav icons, secondary buttons)
- Olive: category taxonomy (item category tags, filter chip selected-state) — this is a deliberate, repeated role, not a decorative accent used at random
- Error orange: validation/danger only, never anything else

**Type:**
- Body/UI text: **Inter** (all weights as needed)
- Brand wordmark "cache": **Unbounded, weight 900**, always lowercase — in the header/logo treatment AND any body-text mention of the brand name. Do not vary this by screen.

**Layout & responsiveness:** mobile-first, not split evenly with desktop. Every screen's layout, spacing, and touch-target sizing is designed for a phone-width viewport first — matches the mockups (all phone-frame layouts) and the actual use case (casual, on-the-go capture). Desktop just needs to flex reasonably (content stays centered/capped in a mobile-width column via `.app-shell`, nothing stretches or breaks) — it is not a co-equal design target and doesn't get its own layout pass. Confirmed with Gina during Step 3 review.

---

## 8. Supporting UI Behaviors

- **Photo upload:** compress/resize client-side via canvas API (~1200px max width, JPEG quality ~0.7) before uploading to Supabase Storage. Show a spinner + "Uploading photo…" and disable the submit button during upload to prevent duplicate submissions.
- **Filters:** dropdown panel anchored below a "Filters" button (not a full-screen modal), multi-select checkboxes by category, Clear/Apply actions.
- **Validation/error states:** inline under the offending field — colored border + icon + one-line message using `--color-error`, not a page-level banner. Covers: wrong password, phone already registered, password under 8 characters. Verify WCAG AA contrast on the error border/text against the field background.
  - **Resolved during Step 3 build:** the mockup's literal styling (`--color-error` text on the tinted error background) measures ~2.9:1 contrast — below the 4.5:1 AA threshold for body-size text. Fix applied everywhere inline errors appear: border + alert icon stay `--color-error` (passes the 3:1 non-text/UI-component threshold), but the error *message text* renders in `--color-text` (near-black maroon) instead, which has excellent contrast on cream/white. No new token introduced — still just the 6 colors in Section 7.
- **Delete confirmation:** modal, not an immediate destructive action.
- **Add-item success animation:** total counts up from the previous total to the new total (ease-out, ~1.2–1.4s), settling into a "+$[item value] this item" line below once complete.
- **Empty state:** same dashboard shell (total value showing $0, filters, sticky add button) with centered message: "It's lonely in here..." / "Add your first item to see what it's worth."

---

## 9. Explicitly Out of Scope (Phase 2/3 — do not build)

- Auto-parse: @cache email alias, SendGrid Inbound Parse, LLM receipt extraction
- Real listing creation / Sell flow functionality (the 5-screen flow is designed but not built — `/sell` is a stub only)
- Stripe / C2C payments
- Collection sharing links
- Full onboarding carousel, profile form (name/DOB/gender), cache-email assignment screen, resale-account-linking screen
- Real resale-value estimation (the flat category-multiplier via `ResaleRate` is the Phase 1 placeholder, by design)

---

## 10. Recommended Build Sequence

1. Scaffold Flask app factory, config, Supabase Postgres connection, base `requirements.txt`
2. Define all models (Section 4) + initial Alembic migration
3. Auth: register/login/logout routes + templates, session handling
4. Base template: bottom nav, brand CSS tokens (Section 7), Google Fonts import
5. See Cache dashboard + empty state + filters
6. Add to Cache form + photo compression/upload + success animation
7. Item detail + delete confirmation modal
8. Profile + Collections (create, view, add item)
9. Sell stub page
10. Flask-Admin: register User, Item, ResaleRate, Collection as ModelViews; seed default `ResaleRate` rows
11. Deploy to Render, connect Supabase, verify end-to-end on a real phone
