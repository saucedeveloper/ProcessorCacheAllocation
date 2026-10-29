from typing import Collection, Callable


def branch_and_bound(
        cache_sizes: Collection[float],
        periods: Collection[float],
        get_wcet: Callable[[int, int], float]):
    k = len(cache_sizes)
    n = len(periods)


    def recursive(...):
        pass
