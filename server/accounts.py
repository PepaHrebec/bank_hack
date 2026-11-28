"""Mock secondary accounts (credit card, savings, pension) shown in Classic mode; fixed data per person."""

# person -> (credit limit, spent, savings balance, savings rate, pension balance, monthly, state contribution)
_PROFILES = {
    1: (50000, 12480, 184500, 4.1, 96200, 1500, 340),
    2: (30000, 7350, 62300, 3.8, 41800, 1000, 230),
    3: (80000, 23900, 312000, 4.3, 158400, 2000, 340),
    4: (40000, 3120, 95700, 4.0, 72500, 1200, 290),
}

_TRANSACTIONS = {
    1: [("Albert", 842, "2026-11-26"), ("Alza.cz", 3290, "2026-11-24"), ("Dopravní podnik", 550, "2026-11-22"),
        ("Rohlík.cz", 1268, "2026-11-20")],
    2: [("Datart", 4990, "2026-11-25"), ("Kavárna Slavia", 285, "2026-11-23"), ("Lékárna Dr.Max", 410, "2026-11-19")],
    3: [("Notino", 1890, "2026-11-27"), ("Kino Lucerna", 360, "2026-11-25"), ("Globus", 2140, "2026-11-21"),
        ("O2 Czech Republic", 699, "2026-11-18"), ("Tesco", 934, "2026-11-16")],
    4: [("Billa", 612, "2026-11-26"), ("Bolt", 245, "2026-11-24"), ("Knihy Dobrovský", 780, "2026-11-20")],
}


def other_accounts(person_id):
    limit, spent, savings, rate, pension, monthly, state = _PROFILES[person_id]
    return [
        {"kind": "credit", "name": "Kreditní karta", "balance": -spent, "limit": limit, "spent": spent,
         "transactions": [{"note": n, "amount": a, "date": d} for n, a, d in _TRANSACTIONS[person_id]]},
        {"kind": "savings", "name": "Spořicí účet", "balance": savings, "rate": rate},
        {"kind": "pension", "name": "Penzijní spoření", "balance": pension, "monthly": monthly,
         "state_contribution": state},
    ]
