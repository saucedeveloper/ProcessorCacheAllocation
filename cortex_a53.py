from parse_cachegrind import CacheGrindResult
import math


def get_total_cycles(analysis: CacheGrindResult) -> int:
    CPI = 0.5
    CYCLES_PER_L1_HIT = 1
    CYCLES_PER_L1_MISS = 13
    CYCLES_PER_L2_MISS = 124
    return (
        math.ceil(analysis.I_refs * CPI)
        + analysis.get_L1_hits() * CYCLES_PER_L1_HIT
        + analysis.get_L1_misses() * CYCLES_PER_L1_MISS
        + analysis.get_L2_misses() * CYCLES_PER_L2_MISS
    )
