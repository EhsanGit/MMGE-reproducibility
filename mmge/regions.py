"""WMO/GRDC regions used throughout the manuscript (first digit of the GRDC station number)."""

REGION_MAP = {
    1: 'Africa',
    2: 'Asia',
    3: 'South America',
    4: 'North America, Central America, Caribbean',
    5: 'South-West Pacific',
    6: 'Europe',
}
REGION_ORDER = ['Africa', 'Asia', 'Europe', 'North America, Central America, Caribbean',
                'South America', 'South-West Pacific']


def map_region(grdc_id):
    """Region name of a GRDC station from the first digit of its station number."""
    return REGION_MAP.get(int(str(int(grdc_id))[0]), 'Unknown')
