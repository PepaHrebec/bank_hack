# Card payment → Group Settle: design

Date: 2026-11-27 · Status: approved in conversation
Builds on: `2026-11-27-group-settle-design.md`

## Intent

You pay for something on behalf of friends (a round of beers) and want to ask
them for their share straight away. The bank notification for the card payment
carries a Group Settle button that opens a new group already holding that
expense, so you only pick the friends.

## Goals

- A presenter control fixed to the bottom-right corner of every phone page,
  outside the phone: "Card payment (demo)" with two fields, Amount and Note,
  and a Pay button. It simulates paying by card at a merchant.
- A card payment takes the amount from that person's balance (whole CZK > 0;
  insufficient funds refused with a message in the control). The note says
  where/what (e.g. "Pivnice U Tygra"); empty note is allowed.
- The person's History shows it as "Card · <note>" (or "Card payment") with
  a negative amount.
- The phone gets a bank notification "You paid 480 CZK · Pivnice U Tygra"
  with a Group Settle button, on the banner and on the item in the pull-down.
- Group Settle from the notification opens George on New group: name
  prefilled from the note (editable), the expense shown ("480 CZK · paid by
  you"), friends to tick. Create makes the group with that expense already in
  it (paid by me, description = note or "Card payment"), then opens the group.
- Settling is the existing Group Settle flow (approve → split slot → requests).

## Non-goals

- Real merchants, card numbers, the split algorithm, notifications with more
  than one action.

## Approaches

1. **Chosen:** card payments in their own table (they have no recipient),
   merged into History; `POST /api/groups` takes an optional starting expense
   so group + expense are created together.
2. Card payment as a payment to a fake "merchant" person. Rejected: breaks
   every place that assumes a payment goes to one of the four people.
3. Create the group, then add the expense with a second call. Rejected: a
   failure in between leaves an empty group.

## Decided how

- Table `card_payments` (person, amount, note, created_at); reset clears it.
- `POST /api/card-payments {amount, note}` → the payer's phones get
  `{"type": "card_payment", "payment": {...}, "text": "You paid 480 CZK · <note>"}`.
- History items gain `"kind": "transfer" | "card"`.
- `POST /api/groups` accepts optional `"expense": {"amount", "description"}`.
- Shell: `Phone.notify` takes an optional `action: {label, onClick}` shown as
  a button on the banner and the pull-down item; tapping it runs `onClick`
  and opens George.
- The presenter control lives in `index.html` outside `.phone`, styled in
  `phone.css`, and talks to the API directly.
