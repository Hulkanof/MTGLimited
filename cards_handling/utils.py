def build_card_dict(cards: list) -> dict:
    """
    Build a usable dictionary ordered by card uuids.
    """
    card_dict = dict()
    for card in cards:
        card_dict[card['uuid']] = dict(name=card['name'], colors=card['colors'])
    return card_dict