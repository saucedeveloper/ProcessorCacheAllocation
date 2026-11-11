"""Implementation of the branch and bound algorithm
applied to the cache partitioning problem"""

from __future__ import annotations

# from abc import abstractmethod
from typing import Sequence, Callable, Iterable
from dataclasses import dataclass
from solving_conditions import utilization_bound, get_utilization_ratio
import heapq


"""Extend `iterable` by `item`"""
def extend_iterable[T](iterable: Iterable[T], item: T):
    for x in iterable:
        yield x
    yield item


"""Sum elements of `iterable` while counting them"""
def sum_counted(iterable: Iterable[int]):
    total_sum = 0
    count = 0
    for item in iterable:
        total_sum += item
        count += 1
    return (total_sum, count)


"""Partial or exhaustive allocation of cache
partition sizes, with best case allocated
cache size (`min_allocated_cache`) and processor
utilization (`utilization_sum`)"""
@dataclass
class CacheAllocation:
    association: tuple[int, ...]
    min_allocated_cache: int
    utilization_sum: float

    def exhaustive_association(self, n: int) -> int | None:
        if len(self.association) != n:
            return None
        return self.min_allocated_cache

    def to_str(self, cache_sizes: Sequence[int]):
        cache = ", ".join(f"#{i}={cache_sizes[c]}" for i, c in enumerate(self.association))
        return f"{{{cache}}}, min_cache={self.min_allocated_cache}, util={self.utilization_sum:.4f}"

    def __lt__(self, other: CacheAllocation):
        return self.min_allocated_cache.__lt__(other.min_allocated_cache)

    def __gt__(self, other: CacheAllocation):
        return self.min_allocated_cache.__gt__(other.min_allocated_cache)

    def __eq__(self, other: object):
        if isinstance(other, CacheAllocation):
            return self.min_allocated_cache.__eq__(other.min_allocated_cache)
        return False


"""Evaluate the best case total cache partition
size given some cache size indices (for some tasks)"""
def best_case_allocated_cache(allocations: Iterable[int], cache_sizes: Sequence[int], n: int) -> int:
    size_of_allocated, allocation_count = sum_counted(cache_sizes[j] for j in allocations)
    min_size_of_non_allocated = cache_sizes[0] * (n - allocation_count)
    return size_of_allocated + min_size_of_non_allocated


"""Get the minimum index between `j_min` and
`j_max` such that `predicate` is true"""
def get_min_index_where(j_min: int, j_max: int, predicate: Callable[[int], tuple[bool, float]], non_matching: set[int]):
    best_result = None
    while j_min < j_max:
        j_mid = (j_min + j_max) // 2
        predicate_result = predicate(j_mid)
        if predicate_result[0]:
            best_result = (j_mid, predicate_result[1])
            j_max = j_mid
        else:
            non_matching.add(j_mid)
            j_min = j_mid + 1
    return best_result


log_enable = False


def print_ind(message: str, end: str = "\n", p: int = 0):
    if log_enable:
        print(" " * (p * 4) + message, end=end)


def branch_and_bound_generic(
        cache_sizes: Sequence[int],
        periods: Sequence[float],
        get_wcet: Callable[[int, int], float],
        report_exhaustive: Callable[[CacheAllocation], None],
        should_explore: Callable[[int, float], bool],
        initial_guess: tuple[int, ...] | None = None,
        max_iter: int = 1000):

    wcet_cache: dict[tuple[int, int], float] = {}
    def get_cached_wcet(i: int, j: int):
        existing = wcet_cache.get((i, j))
        if existing is not None:
            return existing
        new = get_wcet(i, j)
        wcet_cache[(i, j)] = new
        return new

    k = len(cache_sizes)
    n = len(periods)
    assert(0 < k)
    assert(0 < n)

    util_bound = utilization_bound(n)

    def is_partially_schedulable(utilization_sum: float, last_i: int, last_j: int) -> tuple[bool, float]:
        additional_ratio = get_utilization_ratio(periods, get_cached_wcet, last_i, last_j)
        new_sum = utilization_sum + additional_ratio
        return (new_sum <= util_bound, new_sum)

    assert(initial_guess is None or (len(initial_guess) == n))
    # assert(initial_guess is None or is_schedulable(initial_guess, cache_sizes, util_bound, periods, get_cached_wcet)[0])

    # min_cache_size = cache_sizes[0]
    max_cache_size = cache_sizes[-1]

    max_allocated_cache = n * max_cache_size
    # The default allocation min cache size is the highest because it is partial (cannot be a solution)
    initial_allocation: CacheAllocation = CacheAllocation((), max_allocated_cache, 0)
    exploration_queue: list[CacheAllocation] = []
    heapq.heappush(exploration_queue, initial_allocation)
    print_ind(f"Pushing {initial_allocation.to_str(cache_sizes)}")

    iter_count = 0
    analysed_exhaustive_count = 0

    while 0 < len(exploration_queue):
        if max_iter <= iter_count:
            raise ValueError(f"Not terminating ({len(exploration_queue)})")
        iter_count += 1
        next_best_node = heapq.heappop(exploration_queue)
        p = len(next_best_node.association)
        print_ind(f"Analysing {next_best_node.to_str(cache_sizes)}", end="", p=p)
        cache_of_exhaustive = next_best_node.exhaustive_association(n)
        if cache_of_exhaustive is not None:
            print_ind(", exhaustive", end="")
            report_exhaustive(next_best_node)
            analysed_exhaustive_count += 1
        else:
            print_ind(", non-exhaustive")
            next_i = len(next_best_node.association)
            assert(0 <= next_i < n)

            def is_schedulable_for_j(j: int):
                result = is_partially_schedulable(next_best_node.utilization_sum, next_i, j)
                return result

            j_min = 0
            j_max = k
            non_schedulable_js: set[int] = set()
            min_schedulable_j = get_min_index_where(j_min, j_max, is_schedulable_for_j, non_schedulable_js)#(j_min, is_partially_schedulable(next_best_node.utilization_sum, next_i, j_min)[1])

            if min_schedulable_j is None:
                min_schedulable_j = (j_min, next_best_node.utilization_sum + get_utilization_ratio(periods, get_cached_wcet, next_i, j_min))
                print_ind(f"No schedulable j found", p=p + 1)

            min_sched_j, _new_utilization_sum = min_schedulable_j

            for j in range(min_sched_j, j_max):
                if j in non_schedulable_js:
                    continue
                # Generates iterable only consumable once
                inner_association = lambda: extend_iterable(next_best_node.association, j)
                best_case_inner = best_case_allocated_cache(inner_association(), cache_sizes, n)
                partially_schedulable, new_utilization_sum = is_partially_schedulable(next_best_node.utilization_sum, next_i, j)
                if partially_schedulable and should_explore(best_case_inner, new_utilization_sum):
                    next_node = CacheAllocation(tuple(inner_association()), best_case_inner, new_utilization_sum)
                    heapq.heappush(exploration_queue, next_node)
                    print_ind(f"Pushing[{j=}] {next_node.to_str(cache_sizes)}", p=p + 1)

    print_ind(f"\nAnalysed {iter_count} nodes ({analysed_exhaustive_count} complete solutions)")


"""Find the optimal cache partition allocation
that ensures all tasks are schedulable"""
def branch_and_bound(
        cache_sizes: Sequence[int],
        periods: Sequence[float],
        get_wcet: Callable[[int, int], float],
        initial_guess: tuple[int, ...] | None = None,
        max_iter: int = 1000):

    k = len(cache_sizes)
    n = len(periods)
    assert(0 < k)
    assert(0 < n)

    util_bound = utilization_bound(n)

    max_cache_size = cache_sizes[-1]
    max_allocated_cache = n * max_cache_size
    # The default allocation min cache size is the highest because it is partial (cannot be a solution)
    initial_allocation: CacheAllocation = CacheAllocation((), max_allocated_cache, 0)
    exploration_queue: list[CacheAllocation] = []
    heapq.heappush(exploration_queue, initial_allocation)

    best_allocation: list[CacheAllocation | None]
    if initial_guess is None:
        best_allocation = [None]
    else:
        best_case_cache_size = best_case_allocated_cache(initial_guess, cache_sizes, n)
        best_alloc = CacheAllocation(initial_guess, best_case_cache_size, util_bound)
        best_allocation = [best_alloc]
        print(f"initial_guess: {best_alloc.to_str(cache_sizes)}")

    def better_than_best(best_allocation: CacheAllocation | None, cache_size: int) -> bool:
        if best_allocation is None:
            return True
        return cache_size < best_allocation.min_allocated_cache

    def is_schedulable_allocation(allocation: CacheAllocation):
        return allocation.utilization_sum <= util_bound

    def report_exhaustive(next_best_node: CacheAllocation):
        cache_of_exhaustive = next_best_node.min_allocated_cache
        is_new_best = better_than_best(best_allocation[0], cache_of_exhaustive)
        schedulable = is_schedulable_allocation(next_best_node)
        if is_new_best:
            print_ind(f", new best, {'schedulable' if schedulable else f'not_schedulable ({next_best_node.utilization_sum / util_bound:.2f})'}", end="")
        if is_new_best and schedulable:
            best_allocation[0] = next_best_node
        print_ind("")

    def should_explore(best_case_cache_size: int, _utilization_sum: float) -> bool:
        return better_than_best(best_allocation[0], best_case_cache_size)

    branch_and_bound_generic(cache_sizes, periods, get_wcet, report_exhaustive,
                             should_explore, initial_guess, max_iter)

    return best_allocation[0]


def pareto_front(
        cache_sizes: Sequence[int],
        periods: Sequence[float],
        get_wcet: Callable[[int, int], float],
        max_iter: int = 1000,
        tolerance: float = 1e-7):

    dominant_solutions: set[tuple[float, int]] = set()

    def add_dominant(new_dominant: tuple[float, int]):
        dominated_solutions: set[tuple[float, int]] = set()
        for existing in dominant_solutions:
            if dominates(new_dominant, existing):
                dominated_solutions.add(existing)
        for dominated in dominated_solutions:
            dominant_solutions.remove(dominated)
        dominant_solutions.add(new_dominant)

    def dominates(solution_a: tuple[float, int], solution_b: tuple[float, int]):
        return solution_a[0] < solution_b[0] + tolerance and solution_a[1] < solution_b[1] + tolerance

    def should_consider_min_bound(utilization: float, cache_size: int):
        return not any(
            dominates(existing, (utilization, cache_size))
            for existing in dominant_solutions
        )

    def report_exhaustive(next_best_node: CacheAllocation):
        print_ind("")
        utilization = next_best_node.utilization_sum
        cache_size = next_best_node.min_allocated_cache
        should_add = should_consider_min_bound(utilization, cache_size)
        if should_add:
            add_dominant((utilization, cache_size))

    def should_explore(best_case_cache_size: int, new_utilization_sum: float) -> bool:
        return should_consider_min_bound(new_utilization_sum, best_case_cache_size)

    branch_and_bound_generic(cache_sizes, periods, get_wcet, report_exhaustive,
                             should_explore, initial_guess=None, max_iter=max_iter)

    return dominant_solutions
