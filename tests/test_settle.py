import random

import pytest

from server.db import add_expense, approve_group, create_group, get_balance, init_db, open_requests_for
from server.settle import settle, shares


def ex(payer, amount):
    return {"payer": payer, "amount": amount}


def nets(members, expenses):
    """Paid minus share, straight from the brief, independent of settle's own helpers."""
    paid = {p: 0 for p in members}
    for e in expenses:
        paid[e["payer"]] += e["amount"]
    share = shares(members, sum(paid.values()))
    return {p: paid[p] - share[p] for p in members}


def check(members, expenses, transfers):
    """Every rule a split must follow; returns the nets after applying it."""
    before = nets(members, expenses)
    after = dict(before)
    for payer, payee, amount in transfers:
        assert type(amount) is int and amount > 0
        assert payer != payee and payer in members and payee in members
        assert before[payer] < 0 and before[payee] > 0  # only debtors pay, only creditors receive
        after[payer] += amount
        after[payee] -= amount
    assert all(v == 0 for v in after.values())


def max_zero_groups(values):
    """Brute force: the most disjoint zero-sum groups the values (summing to 0) split into."""
    if not values:
        return 0
    first, rest = values[0], values[1:]
    best = 0
    for mask in range(1 << len(rest)):
        picked = [rest[i] for i in range(len(rest)) if mask >> i & 1]
        if first + sum(picked) == 0:
            left = [rest[i] for i in range(len(rest)) if not mask >> i & 1]
            best = max(best, 1 + max_zero_groups(left))
    return best


def greedy_count(balances):
    """Plain largest-debtor-pays-largest-creditor, to show it can lose."""
    bal = dict(balances)
    count = 0
    while any(bal.values()):
        d = min(bal, key=lambda p: bal[p])
        c = max(bal, key=lambda p: bal[p])
        amount = min(-bal[d], bal[c])
        bal[d] += amount
        bal[c] -= amount
        count += 1
    return count


def test_one_payer_for_three():
    assert settle([1, 2, 3], [ex(1, 900)]) == [(2, 1, 300), (3, 1, 300)]


def test_two_payers():
    # 1200 total, 300 each: 1 is owed 600, 2 paid exactly its share and is left out.
    out = settle([1, 2, 3, 4], [ex(1, 900), ex(2, 300)])
    assert out == [(3, 1, 300), (4, 1, 300)]


def test_two_creditors():
    # Nets +300, +300, -300, -300: two pairs, two transfers.
    assert settle([1, 2, 3, 4], [ex(1, 600), ex(2, 600)]) == [(3, 1, 300), (4, 2, 300)]
    # Nets +400, +200, -300, -300: no pair cancels out, so three is the least.
    out = settle([1, 2, 3, 4], [ex(1, 700), ex(2, 500)])
    check([1, 2, 3, 4], [ex(1, 700), ex(2, 500)], out)
    assert out == [(3, 1, 300), (4, 1, 100), (4, 2, 200)]


def test_uneven_total_first_members_by_id_owe_the_extra_crown():
    assert shares([3, 1, 2], 100) == {1: 34, 2: 33, 3: 33}
    assert shares([2, 4], 7) == {2: 4, 4: 3}
    # 100 paid by 3: 1 owes 34, 2 owes 33, 3 keeps its own 33.
    assert settle([3, 1, 2], [ex(3, 100)]) == [(1, 3, 34), (2, 3, 33)]


def test_everyone_even_and_no_expenses():
    assert settle([1, 2, 3], [ex(1, 100), ex(2, 100), ex(3, 100)]) == []
    assert settle([1, 2], []) == []


def test_beats_greedy():
    # Nets: 1 -8, 2 -7, 3 -7, 4 +8, 5 +14. Zero-sum groups {1,4} and {2,3,5}: 3 transfers.
    # Greedy pays 1 -> 5 (8), 2 -> 4 (7), 3 -> 5 (6), 3 -> 4 (1): 4 transfers.
    members = [1, 2, 3, 4, 5]
    expenses = [ex(1, 2), ex(2, 3), ex(3, 3), ex(4, 18), ex(5, 24)]
    assert nets(members, expenses) == {1: -8, 2: -7, 3: -7, 4: 8, 5: 14}
    assert greedy_count(nets(members, expenses)) == 4
    out = settle(members, expenses)
    check(members, expenses, out)
    assert out == [(1, 4, 8), (2, 5, 7), (3, 5, 7)]


def test_deterministic_regardless_of_member_order():
    expenses = [ex(1, 500), ex(3, 101), ex(2, 77)]
    assert settle([1, 2, 3, 4], expenses) == settle([4, 3, 2, 1], expenses)


@pytest.mark.parametrize("seed", range(400))
def test_random_splits_are_exact_and_minimal(seed):
    rng = random.Random(seed)
    n = rng.randint(2, 7)
    members = rng.sample(range(1, 20), n)
    if seed % 2:
        expenses = [ex(rng.choice(members), rng.randint(1, rng.choice([6, 30, 2000]))) for _ in range(rng.randint(0, 8))]
    else:
        # Small nets near an even share of 50 make zero-sum subgroups (non-trivial minima) common.
        expenses = [ex(p, 50 + rng.randint(-6, 6)) for p in members]
        drift = sum(e["amount"] for e in expenses) - 50 * n  # at most 36, so every amount stays > 0
        expenses[0]["amount"] -= drift
    total = sum(e["amount"] for e in expenses)
    assert sum(shares(members, total).values()) == total
    out = settle(members, expenses)
    check(members, expenses, out)
    nonzero = [v for v in nets(members, expenses).values() if v]
    assert len(out) == len(nonzero) - max_zero_groups(nonzero)
    assert settle(list(reversed(members)), list(expenses)) == out


def test_fifteen_members():
    rng = random.Random(7)
    members = list(range(1, 16))
    expenses = [ex(rng.choice(members), rng.randint(1, 40)) for _ in range(30)]
    out = settle(members, expenses)
    check(members, expenses, out)


def test_approve_uses_the_equal_split(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    g = create_group(db, 1, "Chata", [2, 3], accepted=True)
    add_expense(db, g["id"], 1, 900, "Cabin")
    add_expense(db, g["id"], 2, 101, "Beer")
    # 1001 total: 1 and 2 owe 334 (the leftover crowns), 3 owes 333. Nets: 1 +566, 2 -233, 3 -333.
    done = approve_group(db, g["id"], 1)
    assert sorted((r["payer"], r["requester"], r["amount"]) for r in done["requests"]) == [(2, 1, 233), (3, 1, 333)]
    assert [(r["requester"], r["amount"]) for r in open_requests_for(db, 3)] == [(1, 333)]
    assert [get_balance(db, n) for n in (1, 2, 3)] == [10000] * 3
