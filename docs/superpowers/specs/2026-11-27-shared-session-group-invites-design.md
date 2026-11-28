# Shared group-payment session and group invites — design

## Why
In the pub everyone pays rounds. Starting "Skupinová platba" should bring the friends in from the start, so that all of their card payments end up in one Group Settle. Being put into a group should also be the person's own choice: whoever is added to a group settle has to accept it.

## What (agreed with the user, 2026-11-27)
**Shared session (option A)**
- Tapping "Spustit skupinovou platbu" (in the widget or in Geoff) opens a small popup with the three friends as checkboxes and a "Spustit" button. Starting with nobody selected is allowed and works as before.
- Each invited friend gets a notification "<Jméno> tě zve do skupinové platby" with **Přijmout / Odmítnout**.
- Everyone who accepts starts recording their own card payments from the moment they accept. Their widget and app show the session (red dot, counter, who is in it).
- Only the starter can stop the session. Friends who never answered are not included.
- On Stop, the starter's popup lists everyone's card payments with names, and offers **Vytvořit skupinové vyrovnání** (with an editable name, by default "Skupinová platba <date>") or **Nic nedělat**.
  - Creating makes one group of all participants. They are already accepted, so nobody accepts again. Each person's payments become their own expenses in it.
  - When nobody accepted, the Stop popup stays exactly as it is today: create (with invites), add to one of my open groups, or Nic nedělat.

**Group invites** (for every way a group is created: the new-group screen, the WhatsApp suggestion, the solo Stop popup)
- Added people are **invited**. They get **Přijmout / Odmítnout** as a notification, and also in the Group Settle list, so a missed banner isn't lost.
- Declining removes them from the group. Invited people can't see the group's details or add expenses; the group card shows who is still invited.
- On approval, the split counts only accepted members, and open invites are cancelled.
- Seeded "Chata Krkonoše" has all members already accepted.

## Non-goals
- No leaving a session mid-way.
- No invite expiry other than the session stopping.
- No change to how the split is calculated.

## Approach
There is one sensible way: the state lives on the server, as recording does today, because invites must survive reloads and reach every phone live. A browser-only version would lose invites on reload.

Data model:
- `settle_members.status` ('invited'|'accepted'). Existing rows migrate to 'accepted'.
- `recordings` gains `session_starter` and `ended_at`.
- New `session_invites(starter, person)`.
- A session that ended with friends in it is kept until the starter creates the group or discards it. So "Vytvořit" is a server action (`create_group_from_session`), and the client never sends other people's payment ids.

## Left to the builder
Exact Czech wording beyond the strings above (with neutral gender), styling, and test structure.
