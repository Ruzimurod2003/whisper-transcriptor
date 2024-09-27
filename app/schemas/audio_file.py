def serialize_dict(a) -> dict:
    return {
        **{i: str(a[i]) for i in a if i == "_id"},
        **{i: a[i] for i in a if i != "_id"},
    }


def serialize_list(entity) -> list:
    return [serialize_dict(a) for a in entity]
