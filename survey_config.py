# survey_config.py
# All questions, answers, and weight mappings live here.
# To add/change a question, edit this file only. Nothing else needs to change.

SUBINDICES = ["econ", "lifestyle", "community", "mobility", "health"]

QUESTIONS = [
    {
        "id": 1,
        "text": "What matters most to you in your daily life?",
        "type": "forced",
        "options": [
            {
                "text": "Getting outdoors — parks, trails, nature",
                "weights": {"econ": 0, "lifestyle": 0.4, "community": 0, "mobility": 0.1, "health": 0.5}
            },
            {
                "text": "Career growth and earning potential",
                "weights": {"econ": 0.7, "lifestyle": 0.1, "community": 0.1, "mobility": 0.1, "health": 0}
            },
            {
                "text": "Community and civic life",
                "weights": {"econ": 0, "lifestyle": 0.1, "community": 0.7, "mobility": 0.1, "health": 0.1}
            },
            {
                "text": "Health, wellness, and fitness",
                "weights": {"econ": 0, "lifestyle": 0.1, "community": 0.1, "mobility": 0.1, "health": 0.7}
            },
            {
                "text": "Getting around without a car",
                "weights": {"econ": 0, "lifestyle": 0.1, "community": 0.1, "mobility": 0.7, "health": 0.1}
            }
        ]
    },
    {
        "id": 2,
        "text": "How do you feel about your commute?",
        "type": "forced",
        "options": [
            {
                "text": "I want to walk or bike to everything",
                "weights": {"econ": 0, "lifestyle": 0.1, "community": 0, "mobility": 0.8, "health": 0.1}
            },
            {
                "text": "Public transit is fine if it's reliable",
                "weights": {"econ": 0, "lifestyle": 0.1, "community": 0.1, "mobility": 0.7, "health": 0.1}
            },
            {
                "text": "I don't mind driving if the roads aren't bad",
                "weights": {"econ": 0.2, "lifestyle": 0.2, "community": 0.2, "mobility": 0.2, "health": 0.2}
            },
            {
                "text": "Commute doesn't bother me at all",
                "weights": {"econ": 0.3, "lifestyle": 0.3, "community": 0.2, "mobility": 0.1, "health": 0.1}
            }
        ]
    },
    {
        "id": 3,
        "text": "What does your ideal neighborhood look like?",
        "type": "forced",
        "options": [
            {
                "text": "Dense, walkable, lots of restaurants and bars",
                "weights": {"econ": 0, "lifestyle": 0.5, "community": 0.1, "mobility": 0.4, "health": 0}
            },
            {
                "text": "Quiet, suburban, good schools and parks",
                "weights": {"econ": 0.2, "lifestyle": 0.2, "community": 0.4, "mobility": 0, "health": 0.2}
            },
            {
                "text": "Artsy, independent shops, music and culture",
                "weights": {"econ": 0, "lifestyle": 0.7, "community": 0.2, "mobility": 0.1, "health": 0}
            },
            {
                "text": "Affordable, practical, close to work",
                "weights": {"econ": 0.6, "lifestyle": 0.1, "community": 0.1, "mobility": 0.2, "health": 0}
            }
        ]
    },
    {
        "id": 4,
        "text": "How important is cost of living to you?",
        "type": "forced",
        "options": [
            {
                "text": "It's my top priority",
                "weights": {"econ": 0.7, "lifestyle": 0.1, "community": 0.1, "mobility": 0.1, "health": 0}
            },
            {
                "text": "Important but not everything",
                "weights": {"econ": 0.4, "lifestyle": 0.2, "community": 0.1, "mobility": 0.2, "health": 0.1}
            },
            {
                "text": "I'll pay more for the right city",
                "weights": {"econ": 0.1, "lifestyle": 0.4, "community": 0.2, "mobility": 0.2, "health": 0.1}
            },
            {
                "text": "Money isn't a factor",
                "weights": {"econ": 0, "lifestyle": 0.4, "community": 0.2, "mobility": 0.2, "health": 0.2}
            }
        ]
    },
    {
        "id": 5,
        "text": "How do you feel about diversity and community engagement?",
        "type": "forced",
        "options": [
            {
                "text": "Very important, I want somewhere inclusive and engaged",
                "weights": {"econ": 0, "lifestyle": 0.1, "community": 0.8, "mobility": 0, "health": 0.1}
            },
            {
                "text": "Somewhat important",
                "weights": {"econ": 0.1, "lifestyle": 0.2, "community": 0.5, "mobility": 0.1, "health": 0.1}
            },
            {
                "text": "Not a major factor for me",
                "weights": {"econ": 0.3, "lifestyle": 0.3, "community": 0.1, "mobility": 0.2, "health": 0.1}
            }
        ]
    },
    {
        "id": 6,
        "text": "How much do you prioritize your physical and mental health?",
        "type": "forced",
        "options": [
            {
                "text": "It's central to how I choose where to live",
                "weights": {"econ": 0, "lifestyle": 0.1, "community": 0.1, "mobility": 0.1, "health": 0.7}
            },
            {
                "text": "I care about it but it's not the deciding factor",
                "weights": {"econ": 0.1, "lifestyle": 0.2, "community": 0.2, "mobility": 0.2, "health": 0.3}
            },
            {
                "text": "I'll figure it out wherever I land",
                "weights": {"econ": 0.3, "lifestyle": 0.3, "community": 0.2, "mobility": 0.1, "health": 0.1}
            }
        ]
    },
    {
        "id": 7,
        "text": "What kind of environment matters to you?",
        "type": "forced",
        "options": [
            {
                "text": "Clean air and green space are non-negotiable",
                "weights": {"econ": 0, "lifestyle": 0.2, "community": 0, "mobility": 0.1, "health": 0.7}
            },
            {
                "text": "I prefer it but can adapt",
                "weights": {"econ": 0.1, "lifestyle": 0.2, "community": 0.2, "mobility": 0.2, "health": 0.3}
            },
            {
                "text": "Doesn't factor into my decision",
                "weights": {"econ": 0.3, "lifestyle": 0.2, "community": 0.2, "mobility": 0.2, "health": 0.1}
            }
        ]
    },
    {
        "id": 8,
        "text": "How important is access to healthcare?",
        "type": "forced",
        "options": [
            {
                "text": "Critical, I need good hospitals and coverage nearby",
                "weights": {"econ": 0.1, "lifestyle": 0, "community": 0.1, "mobility": 0.1, "health": 0.7}
            },
            {
                "text": "Somewhat important",
                "weights": {"econ": 0.1, "lifestyle": 0.2, "community": 0.2, "mobility": 0.2, "health": 0.3}
            },
            {
                "text": "Not a deciding factor",
                "weights": {"econ": 0.3, "lifestyle": 0.3, "community": 0.2, "mobility": 0.1, "health": 0.1}
            }
        ]
    },
    {
        "id": 9,
        "text": "What's your relationship with work?",
        "type": "forced",
        "options": [
            {
                "text": "Remote — I want coworking options and good coffee shops",
                "weights": {"econ": 0.1, "lifestyle": 0.5, "community": 0.1, "mobility": 0.2, "health": 0.1}
            },
            {
                "text": "Office commuter — I want it to be easy",
                "weights": {"econ": 0.2, "lifestyle": 0.1, "community": 0.1, "mobility": 0.5, "health": 0.1}
            },
            {
                "text": "Work-life balance — parks and recreation matter most",
                "weights": {"econ": 0.1, "lifestyle": 0.3, "community": 0.1, "mobility": 0.1, "health": 0.4}
            }
        ]
    },
    {
        "id": 10,
        "text": "What kind of food and nightlife scene do you want?",
        "type": "forced",
        "options": [
            {
                "text": "Lots of restaurants, bars, and cafes",
                "weights": {"econ": 0, "lifestyle": 0.8, "community": 0.1, "mobility": 0.1, "health": 0}
            },
            {
                "text": "Some good options but not critical",
                "weights": {"econ": 0.2, "lifestyle": 0.4, "community": 0.2, "mobility": 0.1, "health": 0.1}
            },
            {
                "text": "Doesn't matter much to me",
                "weights": {"econ": 0.3, "lifestyle": 0.2, "community": 0.2, "mobility": 0.2, "health": 0.1}
            }
        ]
    },
    {
        "id": 11,
        "text": "How important is education and civic engagement?",
        "type": "forced",
        "options": [
            {
                "text": "I want to live somewhere educated and politically active",
                "weights": {"econ": 0.1, "lifestyle": 0.1, "community": 0.7, "mobility": 0, "health": 0.1}
            },
            {
                "text": "Somewhat important",
                "weights": {"econ": 0.1, "lifestyle": 0.2, "community": 0.5, "mobility": 0.1, "health": 0.1}
            },
            {
                "text": "Not a factor",
                "weights": {"econ": 0.3, "lifestyle": 0.3, "community": 0.1, "mobility": 0.2, "health": 0.1}
            }
        ]
    },
    {
        "id": 12,
        "text": "What's your housing priority?",
        "type": "ranked",
        "options": [
            {
                "text": "Own a home and build equity",
                "weights": {"econ": 0.5, "lifestyle": 0.1, "community": 0.2, "mobility": 0, "health": 0.2}
            },
            {
                "text": "Rent and stay flexible",
                "weights": {"econ": 0.2, "lifestyle": 0.2, "community": 0.1, "mobility": 0.4, "health": 0.1}
            },
            {
                "text": "Just want affordable housing, own or rent",
                "weights": {"econ": 0.6, "lifestyle": 0.1, "community": 0.1, "mobility": 0.1, "health": 0.1}
            }
        ]
    }
]