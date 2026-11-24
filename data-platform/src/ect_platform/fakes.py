"""Deterministic random streams and fictional identity values.

All values are synthetic. Phone numbers use the 555 exchange, emails use reserved
.example / example.com domains, and card numbers use a test-style 400000 prefix
(Luhn-valid, so PII scanners recognise them as card numbers).
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


def card_number(r: random.Random) -> str:
    payload = [4, 0, 0, 0, 0, 0] + [r.randint(0, 9) for _ in range(9)]
    digits = "".join(map(str, payload + [_luhn_check_digit(payload)]))
    return " ".join(digits[i:i + 4] for i in range(0, 16, 4))
