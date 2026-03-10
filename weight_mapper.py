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
    # Quick test — run this file directly to verify it works
    # Simulates a user who cares mostly about mobility and lifestyle
    test_responses = {
        1: 4,  # "Getting around without a car"
        2: 0,  # "I want to walk or bike to everything"
        3: 0,  # "Dense, walkable, lots of restaurants and bars"
        4: 2,  # "I'll pay more for the right city"
        5: 1,  # "Somewhat important"
        6: 1,  # "I care about it but it's not the deciding factor"
        7: 1,  # "I prefer it but can adapt"
        8: 1,  # "Somewhat important"
        9: 0,  # "Remote worker"
        10: 0, # "Lots of restaurants, bars, and cafes"
        11: 1, # "Somewhat important"
        12: [1, 2, 0]  # Ranked: rent > affordable > own
    }

    weights = map_weights(test_responses)
    percentages = weights_to_percentages(weights)

    print("Weight vector:")
    for subindex, weight in weights.items():
        print(f"  {subindex}: {weight}")

    print("\nAs percentages:")
    for subindex, pct in percentages.items():
        print(f"  {subindex}: {pct}%")