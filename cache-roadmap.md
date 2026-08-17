# Cache — Product & Build Roadmap

_Living document. Update as decisions are made — don't let scope drift happen in chat only._
_Cross-reference: strategy-relevant items (problem/opportunity space, market thesis, positioning) also get mirrored into `strategy.md`, not just tracked here._

## Product Thesis

Cache is a consumer app for passive purchase capture, personal inventory management, and frictionless resale. Core bet: intercept the "dark window" between purchase and potential resale — before the user ever decides to catalog or list anything — using automated receipt parsing as the capture mechanic. Core value prop: understanding what you own is worth + capturing that value with minimal effort.

---

## Roadmap by Phase

### Phase 1 — CS50 MVP (current)
Scope: **register → login → see cache → add to cache (manual) → delete item**. Everything else is explicitly out, but the schema is designed so later phases don't require breaking migrations.

### Phase 2 — Concierge / Post-CS50 MVP
- Full onboarding: how-it-works carousel (original vision copy), "Build your Cache" profile form (name/DOB/gender/forwarding email), cache-email assignment screen, resale-account-linking screen
- Add to cache (auto): @cache email alias, SendGrid Inbound Parse, LLM receipt extraction (Claude Haiku)
- Listing creation, change item status, C2C direct-sell via Stripe
- Real resale-value estimation (replacing the flat category-multiplier placeholder)

**Sell flow reference (5 screens, mocked, not yet built):**
1. Vault picker — list of My Cache items to sell, plus "List New Item" / "Import from Orders"
2. Platform selection (radio: Grailed / Depop / eBay — ⚠️ inconsistent with onboarding's ThredUp/Depop/FB Marketplace list; reconcile before building)
3. Review & edit listing — photos, title, brand, price, condition, description, pre-filled from receipt data
4. Publish confirmation — summary card, editable asking price, Publish / Save as draft
5. Success — status + offer count, back to Cache / view listing

### Phase 3 — Later / Unscheduled
- Vertical expansion beyond fashion
- Brand subscriptions / data licensing
- V2 community/local peer-to-peer layer

---

## Architecture Decisions (Phase 1)

| Area | Decision | Why |
|---|---|---|
| Backend | Flask + SQLAlchemy + Flask-Migrate + Flask-Admin + Flask-Login | Full control, minimal framework overhead, Flask-Admin closes most of the gap with Django's admin panel |
| Database + storage | Supabase (Postgres + Storage) | One vendor for both DB and photo storage; free tier comfortably covers 100 users |
| Hosting | Render | Runs Flask as a normal long-lived process — fits a stateful, session-based, file-upload app. Vercel ruled out: serverless model with a 10s free-tier function timeout fights a login/CRUD app with no reason to be stateless |
| Auth | Phone number + password (hashed, werkzeug) | No OAuth, no SMS/OTP verification. Real limitation: phone number is unverified (a text field shaped like a phone number, not a confirmed one) — acceptable for a known concierge cohort, not for opening to strangers later |

---

## Data Model

**User**
- id, phone_number (unique, normalized), password_hash, created_at
- cache_email (nullable — reserved for Phase 2, not used yet)

**Item**
- id, user_id (FK), name, brand, date_purchased, price_purchased, photo_url, description, category
- status (enum: Captured / Surfaced / Listed / Sold — only Captured reachable in Phase 1)
- source (enum: manual / auto — always "manual" in Phase 1)
- created_at

**ResaleRate** (admin-configurable)
- category, multiplier (default 0.60)
- includes a "default" fallback row for any category without its own configured rate

**Key design call:** resale value is *computed live* (price_purchased × rate for the item's category, falling back to default) — never stored on the Item row. This means changing a multiplier in `/admin` updates every item's displayed value immediately, with no recompute job needed.

---

## Routes (Phase 1)

`GET/POST /register` · `GET/POST /login` · `GET /logout` · `GET /` (see cache, with category filter query param) · `GET/POST /add` · `GET /item/<id>` · `POST /item/<id>/delete` · `GET /sell` (stub) · `GET /profile` (stub)

---

## Journeys

### 1. Register
**CS50 build:** splash screen → phone + password form → success screen → redirect to see cache.
**Deferred to Phase 2** (keep original vision copy — accurate once auto-parse/listing exist): how-it-works carousel (3 slides), "Build your Cache" profile form (name/DOB/gender/forwarding email — not persisted, no schema for it yet), cache-email assignment screen, resale-account-linking screen (ThredUp/Depop/FB Marketplace).

### 2. Login
Phone + password → session → redirect to see cache. Logout clears session. Any protected route redirects to `/login` if unauthenticated.

### 3. See Cache (dashboard) — "My Cache"
- Header: page title + **filters button** (multi-select by category)
- **Total cache value** (sum of computed resale values across all items) — displayed at top of page, above the grid
- Grid, 2 cards per row: photo, name, date purchased, purchase value
- **Sticky "+ new item" button**, bottom-right, always visible → `/add`
- No "list" icon/button on cards — resolved as hidden for MVP (consistent with item-detail decision below; listing creation is deferred, so no partial listing UI anywhere in Phase 1)
- Click-through to item detail

**Item detail sub-screen:**
- Header: back button, "Cache" title, **⋮ menu → Delete item** (delete lives here rather than as a standalone button)
- Image, name, brand, date added
- Price: **both purchase price and estimated resale value, stacked**
- Description, category tag
- No "List for sale" / "Make visible to community" buttons, no public/private status pill — all deferred (listing creation + V2 community layer)

### 4. Add to Cache (Manual)
Form: name, brand, date bought, price bought, photo, description, category/type tag → photo uploads to Supabase Storage → creates Item (status=Captured, source=manual) → redirect to see cache.

### 5. Bottom Navigation
Three tabs: **My Cache** (functional, Journey 3) · **Sell** (muted stub, "Coming soon" tag — Phase 2) · **Profile** (functional, Journey 6 below).

---

### 6. Profile — NEW, in scope for Phase 1
Profile picture (placeholder icon for MVP, no upload flow), name, "Caching since [account creation date]", cache value (computed resale total), and **My Collections** section.

**Collections — Phase 1 scope:** create a named collection, view items in it, add items to it. **Not in Phase 1:** shareable links, Stripe payment info — both explicitly Phase 2.

**Schema addition:**
- `Collection`: id, user_id (FK), name, created_at
- `CollectionItem`: collection_id (FK), item_id (FK) — join table, many-to-many confirmed (an item can belong to multiple collections)

**New routes:** `GET /profile` · `POST /collections` · `GET /collections/<id>` · `POST /collections/<id>/add_item`

### 7. Supporting UI states (all screens)
- **Delete confirmation:** modal on top of item detail, "Delete item?" / "This can't be undone" — Delete (red) / Cancel
- **Error/validation states:** inline under the offending field (red border + icon + one-line message), not a top-of-page banner. Covers: wrong password, phone already registered, password too short. **Accessibility requirement:** error text/border color must meet WCAG AA contrast against its background — don't just reuse a light red fill with red text without checking the ratio.
- **Add-item success:** "Success!" screen — cache total counts up from the previous total to the new total (including the just-added item), with a settled "+$[item value] this item" line below the total once the animation completes, then "Back to my Cache"
- **Empty state (My Cache, 0 items):** same page shell (total value, filters, sticky add button) with center message "It's lonely in here..." / "Add your first item to see what it's worth."
- **Photo upload:** client-side compress/resize (canvas API, ~1200px wide, JPEG ~0.7 quality) before upload to Supabase Storage — confirmed approach, no Cloudinary needed for Phase 1. Spinner + "Uploading photo…" text, submit button disabled during upload, to prevent duplicate submissions.
- **Filters UI:** confirmed — dropdown panel anchored below a "Filters" button (not a full-screen bottom sheet), multi-select checkboxes, Clear/Apply actions.

## Open Decisions
_None currently — all Phase 1 screens and interactions are locked as of this update._

## Design Reference
Visual design system tracked separately in `DESIGN.md` (greyscale palette, Archivo typeface, 390px mobile frame, 12px card radius, flat/tonal elevation — no shadows). Journeys above describe page structure and data only, not visual styling.
