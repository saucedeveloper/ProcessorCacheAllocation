import parse_cachegrind
from typing import Callable, Iterable, Sequence
from cortex_a53 import get_total_cycles


"""Sufficient schedulability test bound using Rate Monotonic"""
def utilization_bound(n: int):
    assert(0 < n)
    return n * (2 ** (1 / n) - 1)


CACHE_PARTITION_SIZES = (
    0,
    1024,
    2048,
    4096,
    8192,
    16384,
    32768,
    65536,
    131072,
    262144,
    524288,
    1048576,
    2097152,
    4194304,
)

cachegrind_profiles = parse_cachegrind.get_profiles()

periods = tuple(get_total_cycles(profile[0]) * 1.75 for _, profile in cachegrind_profiles.items())

util_bound = utilization_bound(len(periods))

def get_wcet(i: int, j: int) -> float:
    task_name = parse_cachegrind.VALGRIND_RESULT_NAMES[i]
    profile = cachegrind_profiles[task_name]
    cache_size = CACHE_PARTITION_SIZES[j]
    return get_total_cycles(profile[cache_size])


def is_schedulable(
        allocations: Iterable[int],
        cache_sizes: Sequence[int],
        util_bound: float,
        periods: Sequence[float],
        get_wcet: Callable[[int, int], float]) -> tuple[bool, float]:
    # return all(512 <= cache_sizes[alloc_i] for alloc_i in allocations)
    utilization_sum = sum(get_wcet(i, j) / periods[i] for i, j in enumerate(allocations))
    return (utilization_sum <= util_bound, utilization_sum)
    # utilization_sum = 0
    # for i, alloc_i in enumerate(allocations):
    #     j = alloc_i
    #     processor_utilization = get_wcet(i, j) / periods[i]
    #     utilization_sum += processor_utilization
    #     if util_bound < utilization_sum:
    #         return False
    # return True
