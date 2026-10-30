from __future__ import annotations

from abc import abstractmethod
from typing import Protocol, TypeAlias, Mapping, Sequence, Callable, Iterable, Collection, MutableSequence, TypeVar
from dataclasses import dataclass
import heapq


class Comparable(Protocol):
    """Protocol for annotating comparable types."""

    @abstractmethod
    def __lt__(self: Comparable, other: Comparable, /) -> bool:
        ...

    @abstractmethod
    def __gt__(self: Comparable, other: Comparable, /) -> bool:
        ...


def binary_search(collection: Sequence[int], item: int) -> int:
    if len(collection) == 0:
        return 0

    low_index = 0
    high_index = len(collection)
    while low_index < high_index:
        mid_index = (low_index + high_index) // 2
        mid_item = collection[mid_index]
        if item < mid_item:
            high_index = mid_index
        elif mid_item < item:
            low_index = mid_index
        else:
            return mid_index

    assert(low_index == high_index)
    return low_index


def insert_sorted(collection: list[int], item: int) -> int:
    index = binary_search(collection, item)
    collection.insert(index, item)
    return index


"""Sufficient schedulability test bound using Rate Monotonic"""
def utilization_bound(n: int):
    assert(0 < n)
    return n * (2 ** (1 / n) - 1)


@dataclass
class CacheAllocation:
    association: dict[int, int]
    max_allocated_cache: int

    def is_exhaustive_association(self, n: int):
        return len(self.association) == n

    def __lt__(self, other: CacheAllocation):
        return self.max_allocated_cache.__lt__(other.max_allocated_cache)

    def __gt__(self, other: CacheAllocation):
        return self.max_allocated_cache.__gt__(other.max_allocated_cache)

    def __eq__(self, other: object):
        if isinstance(other, CacheAllocation):
            return self.max_allocated_cache.__eq__(other.max_allocated_cache)
        return False


"""Find the optimal cache partition allocation
that ensures all tasks are schedulable"""
def branch_and_bound(
        cache_sizes: Sequence[int],
        periods: Sequence[float],
        get_wcet: Callable[[int, int], float]):

    """Evaluate the total cache partition size
    for given cache size indices (for all tasks)"""
    def evaluate_allocated_cache(allocations: Iterable[int]) -> int:
        return sum(cache_sizes[j] for j in allocations)

    k = len(cache_sizes)
    n = len(periods)
    assert(0 < k)
    assert(0 < n)

    util_bound = utilization_bound(n)
    min_cache_size = cache_sizes[0]
    max_cache_size = cache_sizes[-1]

    """Evaluate the best case total cache partition
    size given some cache size indices (for some tasks)"""
    def best_case_allocated_cache(allocations: Collection[int]) -> int:
        size_of_allocated = sum(cache_sizes[j] for j in allocations)
        min_size_of_non_allocated = min_cache_size * (n - len(allocations))
        return size_of_allocated + min_size_of_non_allocated

    def is_schedulable(allocations: Iterable[int]) -> bool:
        utilization_sum = 0
        for i, alloc_i in enumerate(allocations):
            j = alloc_i
            utilization_sum += get_wcet(i, j) / periods[i]
            if util_bound < utilization_sum:
                return False
        return True

    max_allocated_cache = n * max_cache_size
    min_allocated_cache = n * min_cache_size
    initial_allocation: CacheAllocation = CacheAllocation({}, max_allocated_cache)
    exploration_queue: list[CacheAllocation] = []
    heapq.heappush(exploration_queue, initial_allocation)
    best_allocation = initial_allocation

    while 0 < len(exploration_queue):
        next_best_node = heapq.heappop(exploration_queue)
        if (next_best_node.is_exhaustive_association(n)
            and next_best_node < best_allocation):
            best_allocation = next_best_node
        else:
            # find next i to take decision on
            # branch on the i'th task
            # foreach child:
            #     if child.best_case < best_solution.best_case:
            #         push(child)
            pass


    # def recursive(current_allocation: dict[int, int]) -> dict[int, int]:

    #     exploring_i = len(current_allocation)
    #     assert(exploring_i <= n)
    #     if n <= exploring_i:
    #         return current_allocation

    #     """Ordered by cache size"""
    #     next_allocations: list[dict[int, int]] = []
    #     """Ordered by cache size"""
    #     next_allocations_cache_size: list[int] = []
    #     for j in range(k):
    #         new_alloc = current_allocation.copy()
    #         new_alloc[exploring_i] = j
    #         cache_size = best_case_allocated_cache(new_alloc.values())

    #         insertion_index = binary_search(next_allocations_cache_size, cache_size)
    #         next_allocations_cache_size.insert(insertion_index, cache_size)
    #         next_allocations.insert(insertion_index, new_alloc)

    #     for next_alloc in next_allocations:


    #     return recursive(next_allocations[best_next_allocation[0]])
