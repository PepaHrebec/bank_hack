"""The split slot for Group Settle: an equal split with the fewest transfers.

`settle` gets the group's member ids and its expenses ({"payer", "amount", ...}) and returns
who pays whom: a list of (payer, payee, amount). All amounts are integer haléře (1 Kč = 100), so
the arithmetic is exact. Approving a group turns each tuple into a payment request from payee to payer.

Everyone owes an equal share of the total; a member's balance is what they paid minus their
share. The balances that aren't zero are split into as many disjoint zero-sum groups as
possible (exact search over subsets), and each group is settled on its own with |group| - 1
transfers. That gives the minimum number of transfers: people - groups.
"""


def shares(members, total):
    """Each member's equal share of `total` haléře, {person: haléře}.

    When the total doesn't divide evenly, the first `total % n` members by id owe 1 haléř more,
    so the shares always add up to the total exactly.
    """
    ids = sorted(set(members))
    base, extra = divmod(total, len(ids))
    return {p: base + (1 if i < extra else 0) for i, p in enumerate(ids)}


def balances(members, expenses):
    """Paid minus share per member, by id. Positive = is owed money, negative = owes."""
    paid = {p: 0 for p in sorted(set(members))}
    for e in expenses:
        paid[e["payer"]] += e["amount"]
    share = shares(paid, sum(paid.values()))
    return {p: paid[p] - share[p] for p in paid}


def _zero_sum_groups(people, bal):
    """Split `people` (balances summing to 0) into the most disjoint zero-sum groups.

    best[mask] is the most zero-sum groups the people in `mask` can be lined up into: add them
    one at a time, and every time the running sum hits 0 a group closes. Fine up to ~20 people.
    """
    n = len(people)
    full = (1 << n) - 1
    total = [0] * (1 << n)
    best = [0] * (1 << n)
    for mask in range(1, full + 1):
        low = mask & -mask
        total[mask] = total[mask ^ low] + bal[people[low.bit_length() - 1]]
        closes = 1 if total[mask] == 0 else 0
        best[mask] = max(best[mask ^ (1 << i)] for i in range(n) if mask >> i & 1) + closes
    # Walk back from everyone, taking off the lowest-id person that keeps the optimum.
    order, mask = [], full
    while mask:
        closes = 1 if total[mask] == 0 else 0
        i = next(i for i in range(n) if mask >> i & 1 and best[mask ^ (1 << i)] + closes == best[mask])
        order.append(people[i])
        mask ^= 1 << i
    groups, current, running = [], [], 0
    for p in reversed(order):
        current.append(p)
        running += bal[p]
        if running == 0:
            groups.append(current)
            current = []
    return groups


def _settle_group(group, bal):
    """Largest debtor pays largest creditor (ties to the lower id) until the group is even."""
    left = {p: bal[p] for p in group}
    transfers = []
    while any(left.values()):
        debtor = min(left, key=lambda p: (left[p], p))
        creditor = max(left, key=lambda p: (left[p], -p))
        amount = min(-left[debtor], left[creditor])
        transfers.append((debtor, creditor, amount))
        left[debtor] += amount
        left[creditor] -= amount
    return transfers


def settle(members, expenses):
    bal = balances(members, expenses)
    people = [p for p in bal if bal[p]]
    if not people:
        return []
    transfers = []
    for group in _zero_sum_groups(people, bal):
        transfers += _settle_group(group, bal)
    return sorted(transfers)
