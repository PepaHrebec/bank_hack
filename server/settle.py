"""The split slot for Group Settle.

`settle` gets the group's member ids and its expenses ({"payer", "amount", ...}) and returns
who pays whom: a list of (payer, payee, amount) in whole CZK. Approving a group turns each
tuple into a payment request from payee to payer.

The equal-split algorithm is not implemented yet, so approving creates no requests.
"""


def settle(members, expenses):
    return []
