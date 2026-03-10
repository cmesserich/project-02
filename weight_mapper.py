# weight_mapper.py
# Takes a user's survey responses and outputs a normalized weight vector.
# ELI5: Translates "I care about walkability" into numbers the scoring engine understands.

from survey_config import QUESTIONS, SUBINDICES


def map_weights(responses: dict) -> dict:
    """
    Takes a dictionary of responses like:
        {1: 0, 2: 2, 3: 1, ...}
        question_id -> index of selected option (for forced choice)
        question_id -> [0, 2, 1] list of ranked indices (for ranked choice)

    Returns a normalized weight vector like:
        {"econ": 0.25, "lifestyle": 0.30, "community": 0.15, "mobility": 0.20, "health": 0.10}
    """

    # Start all subindex weights at zero
    totals = {subindex: 0.0 for subindex in SUBINDICES}

    for question in QUESTIONS:
        qid = question["id"]

        if qid not in responses:
            continue

        if question["type"] == "forced":
            # User picked one option — grab its weights directly
            selected_index = responses[qid]
            selected_option = question["options"][selected_index]
            for subindex, weight in selected_option["weights"].items():
                totals[subindex] += weight

        elif question["type"] == "ranked":
            # User ranked options — first choice gets full weight,
            # second gets half, third gets quarter
            ranked_indices = responses[qid]
            multipliers = [1.0, 0.5, 0.25]
            for rank, option_index in enumerate(ranked_indices):
                if rank >= len(multipliers):
                    break
                option = question["options"][option_index]
                multiplier = multipliers[rank]
                for subindex, weight in option["weights"].items():
                    totals[subindex] += weight * multiplier

    # Normalize so all weights add up to 1.0
    total_sum = sum(totals.values())
    if total_sum == 0:
        # Fallback to equal weights if something went wrong
        return {subindex: 1.0 / len(SUBINDICES) for subindex in SUBINDICES}

    normalized = {subindex: round(totals[subindex] / total_sum, 4) for subindex in SUBINDICES}
    return normalized


def weights_to_percentages(weight_vector: dict) -> dict:
    """
    Converts weight vector to percentages for display.
    {"econ": 0.25} -> {"econ": 25.0}
    """
    return {k: round(v * 100, 1) for k, v in weight_vector.items()}


if __name__ == "__main__":
    # Test 1 — top answers (outdoor/lifestyle focused)
    top_responses = {
        1: 0,   # Get outside
        2: 1,   # Nothing to do
        3: 0,   # Walk or bike
        4: 1,   # Stretch budget
        5: 0,   # Dense, walkable
        6: 0,   # Clean air non-negotiable
        7: 0,   # Roots, civic life
        8: 0,   # Need good hospitals
        9: 0,   # Fully remote
        10: 0,  # Lots of restaurants
        11: 0,  # Trail recommendation
        12: [2, 0, 1, 3]  # Flexibility first
    }

    # Test 2 — bottom answers (cost/practical focused)
    bottom_responses = {
        1: 3,   # Gym, wellness
        2: 0,   # Too expensive
        3: 2,   # Drive, fine with it
        4: 0,   # Affordability #1
        5: 2,   # Quiet, practical
        6: 2,   # Never factors in
        7: 2,   # Don't optimize for community
        8: 2,   # Not a deciding factor
        9: 1,   # Hybrid/on-site
        10: 2,  # Cook at home
        11: 3,  # Finances dialed in
        12: [1, 0, 2, 3]  # Low cost first
    }

    weights1 = map_weights(top_responses)
    weights2 = map_weights(bottom_responses)

    print("Top answers (outdoor/lifestyle):")
    for k, v in weights1.items():
        print(f"  {k}: {v}")

    print("\nBottom answers (cost/practical):")
    for k, v in weights2.items():
        print(f"  {k}: {v}")

    print("\nDelta (top minus bottom):")
    for k in weights1:
        print(f"  {k}: {round(weights1[k] - weights2[k], 4)}")