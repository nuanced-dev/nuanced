def deserialize(data):
    if not data:
        return None
    return {k: v for k, v in data.items() if v is not None}
