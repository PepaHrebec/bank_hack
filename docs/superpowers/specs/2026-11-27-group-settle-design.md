# Group Settle: design

Date: 2026-11-27 · Status: draft, awaiting approval
Builds on: `2026-11-27-four-phone-mockup-design.md` (payment requests, To be paid)

## Intent

Splitwise-style shared expenses inside the bank app. A person creates a group
(e.g. "Chata"), adds some of the other three people, and everyone in it records
what they paid for the group. When the creator approves, the group is settled:
who owes whom is worked out and turned into ordinary payment requests, so the
money moves through To be paid like any other request.

The split algorithm (equal split) is the next piece of work. This step builds
everything around it and leaves one clearly marked slot for it.

## Goals

- Group Settle (icon on Contacts) opens a list of every group I'm in: ones I
  created and ones I was added to. Each shows name, "Created by me" or
  "Added by <name>", status (Open / Approved), total spent, member avatars.
- "+ New group": name the group, tick people from the other three (at least
  one), create. The creator is always a member. Added people get a
  notification ("Štěpán Pressl added you to Chata") and see the group at once.
- Group screen: members, total, list of expenses (who paid, what for, amount,
  time). While Open, any member can add an expense they paid (amount + what
  for) and delete their own expenses. Everyone in the group sees changes live.
- Only the creator sees Approve, available any time while Open (the creator
  decides when everyone is done). Approving locks the group (no more adding
  or deleting) and runs the split slot.
- Each result of the split, "X pays Y n CZK", becomes a normal request from Y
  to X, linked to the group: X sees it in Requested from me (Pay / Decline),
  Y in Requested from others. Notifications as for any request.

## Added 2026-11-27

- The creator can delete a group at any time (with a confirmation). It
  disappears for everyone and members get a notification. Settlement
  requests from it that are still open become `cancelled` (they leave
  Requested from me and show as Cancelled in Requested from others); paid
  ones stay paid, since that money really moved.
- Besides typing an expense, a member can pick one of their own outgoing
  payments from history (card payments and transfers they sent). It becomes
  an expense with that amount and its note (or "Card payment" / "Payment to
  <name>"). Each payment can be added to a group only once, and only by its
  payer.

## Non-goals

- The split algorithm itself (next step).
- Editing expenses, removing members, leaving groups, unequal
  shares, expenses paid on someone else's behalf, "I'm done" flags.

## Anti-goals

- Adding an expense must never change a balance. Money moves only when a
  settlement request is paid.
- No second place where debts live: settlement output is requests, shown in
  To be paid like every other request.

## Approaches

1. **Chosen: settle groups with members and expenses; approval reuses
   requests.** New tables for groups, members, expenses. Approval turns the
   split into request rows linked to the group.
2. Separate "debts" list for settled groups. Rejected: duplicates To be paid
   and its Pay/Decline, debts would show in two places.
3. Each group stored as one JSON blob. Rejected: harder for the split and for
   listing to query expenses.

## Decided how

- Tables: `settle_groups` (name, creator, status open|approved, timestamps),
  `settle_members` (group, person), `expenses` (group, payer, amount whole
  CZK > 0, description, created_at). The person adding an expense is its payer.
- Settlement requests reuse `request_groups` / `requests`; a request group gets
  a link to its settle group, and its requests may have different requesters
  (today a group request has one requester).
- The split slot: `server/settle.py`, `settle(members, expenses)` returning a
  list of (payer, payee, amount). Until the algorithm exists it returns an
  empty list, so approving locks the group and creates no requests; the group
  screen says so ("Approved: split algorithm not implemented yet").
- `/api/state` gains `groups`: every group I'm in with members, expenses,
  totals, status, creator.
- Live updates over the existing WebSocket: members refresh when a group they
  are in changes; new members get a notification.
- Reset (`run.py --reset`) also clears groups and expenses.

## Left to the builder (Claude's calls, correctable)

- Group name required, up to 40 characters; "what for" required, up to 60.
- Endpoints: `POST /api/groups`, `POST /api/groups/{id}/expenses`,
  `DELETE /api/groups/{id}/expenses/{expense_id}`, `POST /api/groups/{id}/approve`.
- Validation errors come back as 400 with a message, like payments.
- Layout follows the existing app screens (white cards, back arrow, black
  primary button, status pills as in Requested from others).
