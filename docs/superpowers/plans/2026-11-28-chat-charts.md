# Chat charts, Classic mode removed — Implementation Plan

**Goal:** Remove the Interaktivní/Klasický switch. The extra accounts stay available through the chatbot (the `accounts_overview` tool already exists). The chatbot gains charts: the LLM picks a plotting tool — a time series (line chart over weeks/months) or a pie chart — and the app renders the chart in the chat.

**User's request (2026-11-28):** "remove the classic mode, but keep the accounts and savings. You will implement that asking in the chatbot. Also implement a graphing feature in the chatbot. Some chats will return a list of numbers. The harness should be able to call a tool for plotting, one will be for plotting over the period of months/weeks whatever and the another will be a piechart. That selection should be made by the llm. But the rendering should be by something in the app."

## Global Constraints
- Czech copy, neutral gender, amounts as "1 234 Kč".
- `uv run pytest -q` passes; `node --check web/app.js` clean. Commits end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Never touch servers on 3001–3004 or `bank.db`.
- Two agents work in the same checkout at once. Agent A owns `server/` + `tests/`; Agent B owns `web/`. Each stages only its own paths (`git add <paths>`, never `-A`). If `git commit` hits `index.lock`, wait a few seconds and retry.

## Contract (fixed up front)
`POST /api/chat` response: `{"reply": str, "charts": [chart, ...]}`. `charts` is always present, possibly empty, in the order the tools were called.

A chart is one of:
```json
{"type": "line", "title": "Výdaje po měsících", "unit": "Kč",
 "labels": ["září", "říjen", "listopad"],
 "series": [{"name": "Výdaje", "values": [12000, 9800, 14350]}, {"name": "Příjmy", "values": [30000, 30000, 31000]}]}
{"type": "pie", "title": "Výdaje tento měsíc", "unit": "Kč",
 "labels": ["Albert", "Lidl", "Převody přátelům", "Ostatní"],
 "values": [3200, 2100, 1800, 950]}
```
- Values are numbers ≥ 0 for pie; line values may be negative.
- Server-side limits:
  - line: 2–24 labels, 1–3 series, each `values` the same length as `labels`;
  - pie: 2–8 slices, all values ≥ 0 with a sum > 0;
  - titles ≤ 60 chars, labels ≤ 30 chars;
  - `unit` is optional (default "Kč").
- Invalid charts are rejected with a tool error the model can read and retry from. They never reach the client.

---

### Agent A — backend (server/chat.py, server/chat_tools.py, server/app.py, tests)
1. **Data tools** in `chat_tools.py` (read-only, registered in `TOOLS` and dispatched in `call()`), so the model has lists of numbers to plot:
   - `money_series(unit: "week"|"month", count: int 2–12, default 6)` → `{"unit", "buckets": [{"label", "from", "to", "income", "card", "to_accounts", "transfers_in", "transfers_out", "total_in", "total_out", "net"}]}`, oldest first, ending with the current week/month.
     - Week labels: e.g. "23. 11." (the Monday). Month labels: Czech month names ("září", or "září 2026" when the year differs from today's).
     - Reuse `money_flow`'s counting logic, so the numbers agree with it.
   - `spending_breakdown(period)` (the same `PERIODS` as `money_flow`) → `{"from", "to", "total", "items": [{"label", "amount"}]}`.
     - Outgoing money grouped by card merchant (the card note, or "Platba kartou"), "Převod: <friend first name>" per friend, and "Na účet <account>".
     - Sorted descending. The top 7 are kept; the rest are summed into "Ostatní".
2. **Plot tools**: `plot_line` and `plot_pie`, with JSON-schema parameters matching the contract (minus `type`).
   - Their Czech descriptions tell the model when to use each: line for development over time (weeks, months), pie for shares of a whole (e.g. what the spending went to).
   - Implement them as `chat_tools.chart(name, args) -> (spec | None, result_for_model)`, which validates against the contract limits. `chat.run` intercepts these two names instead of passing them to `call()`. A valid chart is appended to the charts list, and the model gets `{"ok": true, "shown": "graf je zobrazen uživateli"}`. An invalid one gets `{"error": "..."}`.
3. **`chat.run`** gains a keyword `charts=None`. When it is a list, valid charts are appended to it. Its return value stays the reply string, so existing tests keep passing. The `/api/chat` endpoint passes a list and returns `{"reply", "charts"}`.
4. **System prompt:** mention that it can draw a graph (line over time, pie for shares) when the user asks for one or when a trend or breakdown is clearer as a picture. It must get the numbers from the data tools first, then call a plot tool, and keep the text answer short without repeating every number. Also mention it can tell the user about their other accounts (credit card, savings, pension) via `accounts_overview`.
5. **Tests** (TDD), with a fake `complete`:
   - `money_series` week and month buckets agree with `money_flow` for the same span;
   - `spending_breakdown` groups and caps with "Ostatní";
   - a valid `plot_pie` / `plot_line` call ends up in `charts` and in the endpoint response;
   - invalid charts are rejected (mismatched lengths, too many slices, negative pie value, unknown fields ignored or rejected);
   - the endpoint always returns `charts: []` when no chart was drawn.

### Agent B — frontend (web/app.js, web/app.css)
1. **Remove Classic mode:** `buildClassic`, the mode switch, the accounts list, the credit-card detail view, their CSS, and the `geoff-mode` localStorage use. The balance label is always "Zůstatek". Keep the "Moje účty" chat chip.
   - The chat goes back to the full height it had before. Check the main-view layout with the three tiles (Kontakty, QR kód, Zaplatit).
2. **Render charts** from the `charts` array of the `/api/chat` response, under the assistant's text bubble, as inline SVG built with `document.createElementNS`. No library; text goes in via `textContent` only.
   - **line:** axes with 3–4 gridlines and tick labels formatted with `toLocaleString("cs-CZ")`; x labels, thinned out when there are many; one polyline with dot markers per series; a legend when there is more than one series. It handles negative values and all-zero values.
   - **pie:** a donut with the total in the centre (`czk`-style, using `unit`) and a legend with label, value and percentage. A single 100% slice is drawn correctly (a full ring, not an empty arc).
   - Fixed palette of up to 8 distinguishable colours that look good on the light chat background. The chart title goes above the chart.
   - Charts fit the chat bubble width (viewBox plus `width: 100%`).
   - Charts stay in the chat history DOM. Only the text goes into the `chatHistory` sent back to the server, as today.
3. Add a chip "Graf výdajů" (sends e.g. "Ukaž mi graf výdajů po měsících"). Keep the existing chips.
4. Verify in headless Chrome by stubbing `fetch` for `/api/chat` to return the contract examples above (no real LLM needed). Take screenshots of both chart types and check there are no JS exceptions.
