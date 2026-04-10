from collections.abc import Iterable


def normalize_listing_ids(values: Iterable[str] | None) -> set[str]:
    if not values:
        return set()

    normalized_values: set[str] = set()
    for value in values:
        if not value:
            continue

        for item in value.split(","):
            normalized_item = item.strip()
            if normalized_item:
                normalized_values.add(normalized_item)

    return normalized_values
