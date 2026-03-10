# survey_config.py
# All questions, answers, and weight mappings live here.
# To add/change a question, edit this file only. Nothing else needs to change.
#
# Weight remapping notes (v2):
# - Affordability answers now hit econ hard (0.7+) so econ_affordability/econ_housing
#   actually penalize expensive cities like Seattle
# - Outdoor answers isolate lifestyle without bleeding into community
# - Health answers split cleanly: environment = health_air, medical = health_access
# - Community answers target civic/capital specifically, not generic community bucket
# - Mobility answers distinguish transit vs. car — hits mobility_transit vs mobility_commute

SUBINDICES = ["econ", "lifestyle", "community", "mobility", "health"]

QUESTIONS = [
    {
        "id": 1,
        "text": "What do you actually do on weekends?",
        "type": "forced",
        "options": [
            {
                "text": "Get outside — hikes, trails, parks, water",
                "weights": {"econ": 0, "lifestyle": 0.3, "community": 0, "mobility": 0.1, "health": 0.6}
            },
            {
                "text": "Eat, drink, explore the city",
                "weights": {"econ": 0, "lifestyle": 0.8, "community": 0.1, "mobility": 0.1, "health": 0}
            },
            {
                "text": "Volunteer, local events, farmers markets, community stuff",
                "weights": {"econ": 0, "lifestyle": 0.1, "community": 0.8, "mobility": 0.1, "health": 0}
            },
            {
                "text": "Gym, yoga, wellness, health-focused activities",
                "weights": {"econ": 0, "lifestyle": 0.2, "community": 0, "mobility": 0.1, "health": 0.7}
            }
        ]
    },
    {
        "id": 2,
        "text": "What's your biggest frustration with where you live now?",
        "type": "forced",
        "options": [
            {
                "text": "It's too expensive — rent, groceries, everything",
                "weights": {"econ": 0.8, "lifestyle": 0, "community": 0, "mobility": 0.1, "health": 0.1}
            },
            {
                "text": "There's nothing to do that actually interests me",
                "weights": {"econ": 0, "lifestyle": 0.7, "community": 0.2, "mobility": 0.1, "health": 0}
            },
            {
                "text": "Getting around without a car is impossible",
                "weights": {"econ": 0, "lifestyle": 0.1, "community": 0, "mobility": 0.8, "health": 0.1}
            },
            {
                "text": "I don't feel connected to the people or place",
                "weights": {"econ": 0, "lifestyle": 0.1, "community": 0.8, "mobility": 0, "health": 0.1}
            }
        ]
    },
    {
        "id": 3,
        "text": "How do you get around day to day?",
        "type": "forced",
        "options": [
            {
                "text": "I want to walk or bike to everything",
                "weights": {"econ": 0, "lifestyle": 0.1, "community": 0.1, "mobility": 0.8, "health": 0}
            },
            {
                "text": "Good public transit is enough for me",
                "weights": {"econ": 0, "lifestyle": 0.1, "community": 0, "mobility": 0.8, "health": 0.1}
            },
            {
                "text": "I drive and I'm totally fine with that",
                "weights": {"econ": 0.3, "lifestyle": 0.2, "community": 0.2, "mobility": 0.2, "health": 0.1}
            },
            {
                "text": "I'd like to drive less but I'm not picky",
                "weights": {"econ": 0.1, "lifestyle": 0.2, "community": 0.1, "mobility": 0.5, "health": 0.1}
            }
        ]
    },
    {
        "id": 4,
        "text": "Be honest about money:",
        "type": "forced",
        "options": [
            {
                "text": "Affordability is my #1 filter — I won't live somewhere I can't save",
                "weights": {"econ": 0.8, "lifestyle": 0, "community": 0.1, "mobility": 0.1, "health": 0}
            },
            {
                "text": "I'll stretch my budget for the right city",
                "weights": {"econ": 0.1, "lifestyle": 0.5, "community": 0.2, "mobility": 0.1, "health": 0.1}
            },
            {
                "text": "Cost isn't really a factor for me",
                "weights": {"econ": 0, "lifestyle": 0.4, "community": 0.2, "mobility": 0.2, "health": 0.2}
            }
        ]
    },
    {
        "id": 5,
        "text": "What kind of neighborhood do you want?",
        "type": "forced",
        "options": [
            {
                "text": "Dense, walkable, restaurants and bars on every corner",
                "weights": {"econ": 0, "lifestyle": 0.5, "community": 0.1, "mobility": 0.4, "health": 0}
            },
            {
                "text": "Artsy, independent, local music and culture scene",
                "weights": {"econ": 0, "lifestyle": 0.8, "community": 0.1, "mobility": 0.1, "health": 0}
            },
            {
                "text": "Quiet, practical, close to work or family",
                "weights": {"econ": 0.4, "lifestyle": 0.1, "community": 0.2, "mobility": 0.2, "health": 0.1}
            },
            {
                "text": "Green, spacious, parks and trails nearby",
                "weights": {"econ": 0, "lifestyle": 0.3, "community": 0, "mobility": 0.1, "health": 0.6}
            }
        ]
    },
    {
        "id": 6,
        "text": "How much does the environment around you actually matter?",
        "type": "forced",
        "options": [
            {
                "text": "Clean air and green space are non-negotiable for me",
                "weights": {"econ": 0, "lifestyle": 0.2, "community": 0, "mobility": 0, "health": 0.8}
            },
            {
                "text": "I'd like it but I can adapt to most places",
                "weights": {"econ": 0.1, "lifestyle": 0.2, "community": 0.2, "mobility": 0.2, "health": 0.3}
            },
            {
                "text": "Honestly never factors into my thinking",
                "weights": {"econ": 0.3, "lifestyle": 0.3, "community": 0.2, "mobility": 0.1, "health": 0.1}
            }
        ]
    },
    {
        "id": 7,
        "text": "What does community mean to you?",
        "type": "forced",
        "options": [
            {
                "text": "I want roots — neighbors I know, local politics, civic life",
                "weights": {"econ": 0, "lifestyle": 0, "community": 0.9, "mobility": 0.1, "health": 0}
            },
            {
                "text": "I want options — good people around but I make my own connections",
                "weights": {"econ": 0, "lifestyle": 0.4, "community": 0.3, "mobility": 0.2, "health": 0.1}
            },
            {
                "text": "Community isn't really something I optimize for",
                "weights": {"econ": 0.3, "lifestyle": 0.3, "community": 0, "mobility": 0.2, "health": 0.2}
            }
        ]
    },
    {
        "id": 8,
        "text": "Healthcare access — how do you think about it?",
        "type": "forced",
        "options": [
            {
                "text": "I need good hospitals and specialists nearby, it's critical",
                "weights": {"econ": 0, "lifestyle": 0, "community": 0.1, "mobility": 0.1, "health": 0.8}
            },
            {
                "text": "Nice to have but not a dealbreaker",
                "weights": {"econ": 0.1, "lifestyle": 0.2, "community": 0.2, "mobility": 0.2, "health": 0.3}
            },
            {
                "text": "Not something I think about when choosing where to live",
                "weights": {"econ": 0.3, "lifestyle": 0.3, "community": 0.1, "mobility": 0.2, "health": 0.1}
            }
        ]
    },
    {
        "id": 9,
        "text": "What's your work situation?",
        "type": "forced",
        "options": [
            {
                "text": "Fully remote — I can live anywhere, job market doesn't matter",
                "weights": {"econ": 0, "lifestyle": 0.5, "community": 0.1, "mobility": 0.1, "health": 0.3}
            },
            {
                "text": "Hybrid or on-site — commute and job market both matter",
                "weights": {"econ": 0.3, "lifestyle": 0.1, "community": 0.1, "mobility": 0.5, "health": 0}
            },
            {
                "text": "Self-employed or freelance — I care about coworking culture and coffee shops",
                "weights": {"econ": 0.1, "lifestyle": 0.5, "community": 0.3, "mobility": 0.1, "health": 0}
            }
        ]
    },
    {
        "id": 10,
        "text": "What kind of food and social scene do you want?",
        "type": "forced",
        "options": [
            {
                "text": "Lots of restaurants, bars, and cafes — the more options the better",
                "weights": {"econ": 0, "lifestyle": 0.8, "community": 0.1, "mobility": 0.1, "health": 0}
            },
            {
                "text": "Some good spots but I'm not living for the nightlife",
                "weights": {"econ": 0.2, "lifestyle": 0.4, "community": 0.2, "mobility": 0.1, "health": 0.1}
            },
            {
                "text": "Doesn't matter much — I cook at home and keep to myself",
                "weights": {"econ": 0.3, "lifestyle": 0.1, "community": 0.1, "mobility": 0.1, "health": 0.4}
            }
        ]
    },
    {
        "id": 11,
        "text": "What would your friends say you care most about?",
        "type": "forced",
        "options": [
            {
                "text": "Always has a trail or park recommendation",
                "weights": {"econ": 0, "lifestyle": 0.2, "community": 0, "mobility": 0.1, "health": 0.7}
            },
            {
                "text": "Knows every good restaurant and bar in town",
                "weights": {"econ": 0, "lifestyle": 0.8, "community": 0.1, "mobility": 0.1, "health": 0}
            },
            {
                "text": "Always shows up for the community",
                "weights": {"econ": 0, "lifestyle": 0.1, "community": 0.8, "mobility": 0.1, "health": 0}
            },
            {
                "text": "Has their finances completely dialed in",
                "weights": {"econ": 0.8, "lifestyle": 0.1, "community": 0, "mobility": 0.1, "health": 0}
            }
        ]
    },
    {
        "id": 12,
        "text": "When it comes to housing, rank these in order of priority:",
        "type": "ranked",
        "options": [
            {
                "text": "Owning a home and building equity",
                "weights": {"econ": 0.5, "lifestyle": 0.1, "community": 0.2, "mobility": 0, "health": 0.2}
            },
            {
                "text": "Low monthly cost — rent or own, just keep it affordable",
                "weights": {"econ": 0.7, "lifestyle": 0.1, "community": 0.1, "mobility": 0.1, "health": 0}
            },
            {
                "text": "Flexibility — renting in a walkable, lively neighborhood",
                "weights": {"econ": 0.1, "lifestyle": 0.4, "community": 0.1, "mobility": 0.4, "health": 0}
            },
            {
                "text": "Space and access to nature, even if it means more driving",
                "weights": {"econ": 0.1, "lifestyle": 0.2, "community": 0.1, "mobility": 0, "health": 0.6}
            }
        ]
    }
]