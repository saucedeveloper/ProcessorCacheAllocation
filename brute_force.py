"""Implementation of an exhaustive brute force
algorithm applied to the cache partitioning problem"""

from branch_and_bound import best_case_allocated_cache, CacheAllocation
from typing import Sequence, Callable
from solving_conditions import is_schedulable, utilization_bound, CACHE_PARTITION_SIZES, periods, get_wcet
import sys


"""Iterates over every integer combination
of n values with maximum index"""
class CombinationIterator:
    def __init__(self, value_count: int, value_max: int) -> None:
        self.value_count = value_count
        self.value_max = value_max
        self.current = [0] * value_count

    def next(self) -> bool:
        # print(f"{self.current=}")
        for i in range(self.value_count):
            if self.current[i] + 1 < self.value_max:
                self.current[i] += 1
                return True
            if self.current[i] + 1 == self.value_max:
                self.current[i] = 0
                if i + 1 < self.value_count:
                    continue
                elif i + 1 == self.value_count:
                    break
                else:
                    assert(False)
            else:
                assert(False)
        return False

    def get_next(self) -> Sequence[int] | None:
        if self.next():
            return self.current
        return None


"""Gets the best schedulable cache allocation using brute force"""
def best_brute_force(
        cache_sizes: Sequence[int],
        periods: Sequence[float],
        get_wcet: Callable[[int, int], float]):

    n = len(periods)
    k = len(cache_sizes)
    util_bound = utilization_bound(n)
    solution_iterator = CombinationIterator(value_count=n, value_max=k)
    best_solution = None
    schedulable_count = 0
    empirical_iter_count = 0
    while True:
        empirical_iter_count += 1
        current_cache_size = best_case_allocated_cache(solution_iterator.current, cache_sizes, n)
        utilization_sum = [-1.0]
        schedulable = is_schedulable(solution_iterator.current, util_bound, periods, get_wcet, utilization_sum)
        if schedulable:
            schedulable_count += 1
        if schedulable and ((best_solution is None) or (current_cache_size < best_solution.min_allocated_cache)):
            best_solution = CacheAllocation(tuple(solution_iterator.current), current_cache_size, utilization_sum[0])
        if not solution_iterator.next():
            break

    return (best_solution, empirical_iter_count, schedulable_count)


"""Generates all cache allocations possible"""
def all_brute_force(
        cache_sizes: Sequence[int],
        periods: Sequence[float],
        get_wcet: Callable[[int, int], float]):

    n = len(periods)
    k = len(cache_sizes)
    util_bound = utilization_bound(n)
    solution_iterator = CombinationIterator(value_count=n, value_max=k)
    while True:
        current_cache_size = best_case_allocated_cache(solution_iterator.current, cache_sizes, n)
        utilization_sum = [-1.0]
        schedulable = is_schedulable(solution_iterator.current, util_bound, periods, get_wcet, utilization_sum)
        yield (CacheAllocation(tuple(solution_iterator.current), current_cache_size, utilization_sum[0]), schedulable)
        if not solution_iterator.next():
            break


"""Writes all cache allocations possible to `destination`"""
def log_brute_force(
        cache_sizes: Sequence[int],
        periods: Sequence[float],
        get_wcet: Callable[[int, int], float],
        destination: str):

    with open(destination, "w") as file:
        for solution, schedulable in all_brute_force(cache_sizes, periods, get_wcet):
            file.write(f"{str(solution.association).replace(' ', '')}>{solution.min_allocated_cache}!{int(schedulable)}\n")


"""Writes all cache allocations possible to `sys.argv[1]`"""
def main():
    if 2 <= len(sys.argv):
        destination = sys.argv[1]
    else:
        destination = "brute_force.log"
    log_brute_force(CACHE_PARTITION_SIZES, periods, get_wcet, destination)


if __name__ == "__main__":
    main()
