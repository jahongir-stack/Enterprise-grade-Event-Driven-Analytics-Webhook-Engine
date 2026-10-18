from decimal import Decimal
from threading import RLock

class Ledger:
    def __init__(self):
        self._balances = {}
        self._posted = {}
        self._lock = RLock()

    def open(self, account, balance='0'):
        with self._lock:
            if account in self._balances: raise ValueError('duplicate account')
            self._balances[account] = Decimal(balance)

    def post(self, key, entries):
        entries = tuple((account, Decimal(str(amount))) for account, amount in entries)
        if not entries or sum((delta for _,delta in entries), Decimal(0)) != 0:
            raise ValueError('unbalanced journal')
        with self._lock:
            if key in self._posted:
                if self._posted[key] != entries: raise ValueError('conflicting key')
                return dict(self._balances)
            draft = self._balances.copy()
            for account, delta in entries:
                if account not in draft: raise KeyError(account)
                draft[account] += delta
            self._balances = draft
            self._posted[key] = entries
            return dict(draft)
