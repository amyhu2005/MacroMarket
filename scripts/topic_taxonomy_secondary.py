"""
Supplemental taxonomy entries for topics that only ever appear as a paper's
*secondary or tertiary* topic (never primary), covering everything with
occurrence >= 5 in data/processed/distinct_topics_all_ranks.csv. The long
tail below that threshold (mostly occurrence=1, largely off-topic noise from
OpenAlex's classifier) falls back to a default bucket rather than being
individually classified - see topic_cooccurrence.py.
"""

SECONDARY_TOPIC_TAXONOMY = {
    "Diverse Specialized Academic Research": ("Applied", "Other / Interdisciplinary"),
    "International Arbitration and Investment Law": ("Applied", "Political Economy & Governance"),
    "World Wars: History, Literature, and Impact": ("Applied", "Economic History"),
    "Legal case studies and regulations": ("Applied", "Political Economy & Governance"),
    "Legal Cases and Commentary": ("Applied", "Political Economy & Governance"),
    "Youth Education and Societal Dynamics": ("Applied", "Education Economics"),
    "Capital Investment and Risk Analysis": ("Applied", "Corporate & Household Finance"),
    "Supply Chain and Inventory Management": ("Micro", "Industrial Organization & Competition"),
    "Social and Intergroup Psychology": ("Applied", "Other / Interdisciplinary"),
    "Optimization and Search Problems": ("Econometrics", "Statistical & Bayesian Methods"),
    "Political Conflict and Governance": ("Applied", "Political Economy & Governance"),
    "Psychological Well-being and Life Satisfaction": ("Applied", "Other / Interdisciplinary"),
    "Statistical Methods in Clinical Trials": ("Applied", "Health Economics"),
    "Multi-Criteria Decision Making": ("Micro", "Behavioral & Experimental Economics"),
    "Legal and Constitutional Studies": ("Applied", "Political Economy & Governance"),
}

DEFAULT_BUCKET = ("Applied", "Other / Interdisciplinary")
