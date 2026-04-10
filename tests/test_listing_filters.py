from utils.listing_filters import normalize_listing_ids


def test_normalize_listing_ids_supports_repeated_and_comma_separated_values():
    values = ["123, 456", "456", "789", ""]

    assert normalize_listing_ids(values) == {"123", "456", "789"}


def test_normalize_listing_ids_handles_missing_values():
    assert normalize_listing_ids(None) == set()
