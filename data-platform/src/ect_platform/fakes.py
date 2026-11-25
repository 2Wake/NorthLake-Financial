"""Deterministic random streams and fictional identity values.

All values are synthetic. Phone numbers use the 555 exchange, emails use reserved
.example / example.com domains, and card numbers use a test-style 400000 prefix.

From generator 0.4.0 full card numbers, SSNs and bank account numbers are still drawn (so
every other value keeps the same random draws) but are never output: only the last 4 digits
and a provider token leave the generator (POL-11; owner decision 2026-11-25, see WORKLOG). Tokens come from their own random
stream keyed by the record ID, never from the full value, so they can't be joined back to it.
"""
import hashlib
import math
import random

from faker import Faker

from .config import SEED

_fk = Faker("en_US")

BOROUGHS = [("Manhattan", "100"), ("Brooklyn", "112"), ("Queens", "113"),
            ("Bronx", "104"), ("Staten Island", "103")]
AREA_CODES = ["212", "332", "347", "646", "718", "917", "929"]


def seed_int(*parts) -> int:
    digest = hashlib.sha256("|".join([SEED, *map(str, parts)]).encode()).digest()
    return int.from_bytes(digest[:8], "big")


def rng(*parts) -> random.Random:
    """A random stream fixed by its name and date, independent of every other stream."""
    return random.Random(seed_int(*parts))


def poisson(r: random.Random, lam: float) -> int:
    limit, k, p = math.exp(-lam), 0, r.random()
    while p > limit:
        k += 1
        p *= r.random()
    return k


def person(r: random.Random) -> tuple[str, str]:
    _fk.seed_instance(r.getrandbits(64))
    return _fk.first_name(), _fk.last_name()


def nyc_address(r: random.Random) -> str:
    _fk.seed_instance(r.getrandbits(64))
    borough, zip3 = r.choice(BOROUGHS)
    return f"{_fk.building_number()} {_fk.street_name()}, {borough}, NY {zip3}{r.randint(0, 99):02d}"


def phone(r: random.Random) -> str:
    return f"{r.choice(AREA_CODES)}-555-{r.randint(1000, 9999)}"


def ssn(r: random.Random) -> str:
    area = r.randint(100, 899)
    if area == 666:
        area = 667
    return f"{area:03d}-{r.randint(10, 99):02d}-{r.randint(1000, 9999):04d}"


def _luhn_check_digit(payload: list[int]) -> int:
    total = 0
    for i, digit in enumerate(reversed(payload)):
        if i % 2 == 0:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return (10 - total % 10) % 10


def last4(value: str) -> str:
    """The last 4 digits of a card, SSN or account number: the only part ECT keeps."""
    return "".join(c for c in value if c.isdigit())[-4:]


_TOKEN_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"  # letters only: a token can never
                                                                        # look like a card number to a scan


def _token(prefix: str, stream: str, record_id: str, length: int) -> str:
    r = rng(stream, record_id)
    return prefix + "".join(r.choice(_TOKEN_CHARS) for _ in range(length))


def card_token(card_id: str) -> str:
    """The payment processor's token for a card (simulated). Independent of the card number."""
    return _token("tok_", "card-token", card_id, 24)


def payout_token(driver_id: str) -> str:
    """The payout provider's account reference for a driver's bank account (simulated)."""
    return _token("acct_", "payout-token", driver_id, 16)


def card_number(r: random.Random) -> str:
    payload = [4, 0, 0, 0, 0, 0] + [r.randint(0, 9) for _ in range(9)]
    digits = "".join(map(str, payload + [_luhn_check_digit(payload)]))
    return " ".join(digits[i:i + 4] for i in range(0, 16, 4))
