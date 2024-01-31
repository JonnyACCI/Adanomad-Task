def individual_serializer(candidate) -> dict:
    return {
        "id": str(candidate["_id"]),
        "resume": candidate["resume"],
        "name" : candidate["name"],
        "rawText" : candidate["rawText"],
        "data" : candidate["data"],
    }

def list_serializer(candidates) -> list:
    return [individual_serializer(candidate) for candidate in candidates]


