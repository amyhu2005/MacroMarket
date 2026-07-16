"""
Manual corrections for OpenAlex institution mis-links found by spot-checking
the top-100 institutions by paper count (author names cross-checked against
known affiliations). These are acronym/name collisions in OpenAlex's automated
affiliation-string matching, e.g. "MIT" matched to Moscow Institute of Thermal
Technology instead of Massachusetts Institute of Technology.

Only corrects the highest-impact (high-paper-count) errors found in the top
100; lower down the ranking (< ~12 papers), similar noise likely exists but
doesn't move the rankings enough to be worth manually auditing hundreds of
low-count institutions.

Keyed by the (wrong) OpenAlex institution_id -> corrected display name.
"""

INSTITUTION_CORRECTIONS = {
    "https://openalex.org/I175594653": "Brown University",           # was "John Brown University"
    "https://openalex.org/I2801851002": "Harvard University",         # was "Harvard University Press"
    "https://openalex.org/I2801857525": "Northwestern University",    # was "Kellogg's (Canada)" -> Kellogg School of Mgmt
    "https://openalex.org/I134446601": "University of California, Berkeley",  # was "Berkeley College"
    "https://openalex.org/I4210109586": "Massachusetts Institute of Technology",  # was "Moscow Institute of Thermal Technology"
    "https://openalex.org/I36788626": "University of Pennsylvania",   # was "California University of Pennsylvania"
    "https://openalex.org/I4210140029": "IZA - Institute of Labor Economics",  # was "International Zinc Association"
    "https://openalex.org/I2800552397": "BREAD (Bureau for Research and Economic Analysis of Development)",  # was "Bread for the World Institute"
}

# Same 8 mis-links, but for anything keyed by *institution_id* rather than
# display name (the geo map: institutions are plotted by ID, and each of
# these wrong IDs belongs to a real, differently-located place - e.g.
# "Moscow Institute of Thermal Technology" is genuinely in Moscow, so its
# coordinates are wrong for MIT, not just its label). Where a correctly-linked
# counterpart ID already exists in this dataset (confirmed via
# institution_geo_cache.json), authorships on the wrong ID should be merged
# onto it so the map shows one accurately-placed node, not a mislabeled one.
INSTITUTION_ID_MERGES = {
    "https://openalex.org/I175594653": "https://openalex.org/I27804330",    # John Brown University -> Brown University
    "https://openalex.org/I2801851002": "https://openalex.org/I136199984",  # Harvard University Press -> Harvard University
    "https://openalex.org/I2801857525": "https://openalex.org/I111979921",  # Kellogg's (Canada) -> Northwestern University
    "https://openalex.org/I134446601": "https://openalex.org/I95457486",    # Berkeley College -> UC Berkeley
    "https://openalex.org/I4210109586": "https://openalex.org/I63966007",   # Moscow Institute of Thermal Technology -> MIT
    "https://openalex.org/I36788626": "https://openalex.org/I79576946",     # California University of Pennsylvania -> UPenn
    "https://openalex.org/I4210140029": "https://openalex.org/I197518295",  # International Zinc Association -> IZA
}

# "Bread for the World Institute" (I2800552397, a real DC advocacy nonprofit)
# has no correctly-linked BREAD counterpart ID in this dataset to merge onto,
# and BREAD itself is a multi-institution research network with no single
# true location - so it's dropped from the geo map entirely rather than
# plotted at a real-but-wrong DC address.
INSTITUTIONS_EXCLUDED_FROM_GEO = {"https://openalex.org/I2800552397"}
