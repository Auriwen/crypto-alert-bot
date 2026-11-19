"""Alert logic: decide whether a price alert should fire."""


def is_triggered(price: float, direction: str, target: float) -> bool:
    """Return True if `price` has reached `target` in the given direction.

    `direction` is "above" or "below".
    """
    if direction == "above":
        return price >= target
    if direction == "below":
        return price <= target
    raise ValueError(f"direction must be 'above' or 'below', got {direction!r}")
