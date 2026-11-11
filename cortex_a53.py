from parse_cachegrind import CacheGrindResult


"""The estimate number of cycles for `analysis`"""
def get_total_cycles(analysis: CacheGrindResult) -> float:
    CPI = 0.5
    CYCLES_PER_L1_HIT = 1
    CYCLES_PER_L1_MISS = 13
    CYCLES_PER_L2_MISS = 124
    return (
        analysis.I_refs * CPI
        # + analysis.get_L1d_hits() * CYCLES_PER_L1_HIT
        + analysis.get_L1_misses() * (CYCLES_PER_L1_MISS - CYCLES_PER_L1_HIT)
        + analysis.get_L2_misses() * (CYCLES_PER_L2_MISS - CYCLES_PER_L1_MISS)
    )
