from __future__ import annotations

# from abc import abstractmethod
from typing import Sequence, Callable, Iterable
from dataclasses import dataclass
import heapq


# class Comparable(Protocol):
#     """Protocol for annotating comparable types."""

#     @abstractmethod
#     def __lt__(self: Comparable, other: Comparable, /) -> bool:
#         ...

#     @abstractmethod
#     def __gt__(self: Comparable, other: Comparable, /) -> bool:
#         ...


# def binary_search(collection: Sequence[int], item: int) -> int:
#     if len(collection) == 0:
#         return 0

#     low_index = 0
#     high_index = len(collection)
#     while low_index < high_index:
#         mid_index = (low_index + high_index) // 2
#         mid_item = collection[mid_index]
#         if item < mid_item:
#             high_index = mid_index
#         elif mid_item < item:
#             low_index = mid_index
#         else:
#             return mid_index

#     assert(low_index == high_index)
#     return low_index


# def insert_sorted(collection: list[int], item: int) -> int:
#     index = binary_search(collection, item)
#     collection.insert(index, item)
#     return index


"""Sufficient schedulability test bound using Rate Monotonic"""
def utilization_bound(n: int):
    assert(0 < n)
    return n * (2 ** (1 / n) - 1)


def extend_iterable[T](iterable: Iterable[T], item: T):
    for x in iterable:
        yield x
    yield item


def sum_counted(iterable: Iterable[int]):
    total_sum = 0
    count = 0
    for item in iterable:
        total_sum += item
        count += 1
    return (total_sum, count)


@dataclass
class CacheAllocation:
    association: tuple[int, ...] #dict[int, int]
    min_allocated_cache: int
    # max_allocated_cache: int

    def exhaustive_association(self, n: int) -> int | None:
        if len(self.association) != n:
            return None
        return self.min_allocated_cache

    def to_str(self, cache_sizes: Sequence[int]):
        cache = ", ".join(f"#{i}={cache_sizes[c]}" for i, c in enumerate(self.association))
        return f"{{{cache}}}, min={self.min_allocated_cache}"

    def __lt__(self, other: CacheAllocation):
        return self.min_allocated_cache.__lt__(other.min_allocated_cache)

    def __gt__(self, other: CacheAllocation):
        return self.min_allocated_cache.__gt__(other.min_allocated_cache)

    def __eq__(self, other: object):
        if isinstance(other, CacheAllocation):
            return self.min_allocated_cache.__eq__(other.min_allocated_cache)
        return False


def is_schedulable(
        allocations: Iterable[int],
        cache_sizes: Sequence[int],
        util_bound: float,
        periods: Sequence[float],
        get_wcet: Callable[[int, int], float]) -> bool:
    return all(512 <= cache_sizes[alloc_i] for alloc_i in allocations)
    utilization_sum = 0
    for i, alloc_i in enumerate(allocations):
        j = alloc_i
        utilization_sum += get_wcet(i, j) / periods[i]
        if util_bound < utilization_sum:
            return False
    return True


"""Evaluate the best case total cache partition
size given some cache size indices (for some tasks)"""
def best_case_allocated_cache(allocations: Iterable[int], cache_sizes: Sequence[int], n: int) -> int:
    size_of_allocated, allocation_count = sum_counted(cache_sizes[j] for j in allocations)
    min_size_of_non_allocated = cache_sizes[0] * (n - allocation_count)
    return size_of_allocated + min_size_of_non_allocated


"""Find the optimal cache partition allocation
that ensures all tasks are schedulable"""
def branch_and_bound(
        cache_sizes: Sequence[int],
        periods: Sequence[float],
        get_wcet: Callable[[int, int], float]):

    def print_ind(message: str, end: str = "\n", p: int = 0):
        print(" " * (p * 4) + message, end=end)

    k = len(cache_sizes)
    n = len(periods)
    assert(0 < k)
    assert(0 < n)

    util_bound = utilization_bound(n)
    # min_cache_size = cache_sizes[0]
    max_cache_size = cache_sizes[-1]

    def better_than_best(best_allocation: CacheAllocation | None, cache_size: int) -> bool:
        if best_allocation is None:
            return True
        return cache_size < best_allocation.min_allocated_cache

    max_allocated_cache = n * max_cache_size
    # min_allocated_cache = n * min_cache_size
    # The default allocation min cache size is the highest because it is partial (cannot be a solution)
    initial_allocation: CacheAllocation = CacheAllocation((), max_allocated_cache)
    exploration_queue: list[CacheAllocation] = []
    heapq.heappush(exploration_queue, initial_allocation)
    print_ind(f"Pushing {initial_allocation.to_str(cache_sizes)}")
    best_allocation: CacheAllocation | None = None
    iter_count = 0

    while 0 < len(exploration_queue):
        if 500 < iter_count:
            raise ValueError(f"Not terminating ({len(exploration_queue)})")
        iter_count += 1
        next_best_node = heapq.heappop(exploration_queue)
        p = len(next_best_node.association)
        print_ind(f"Analysing {next_best_node.to_str(cache_sizes)}", end="", p=p)
        cache_of_exhaustive = next_best_node.exhaustive_association(n)
        if cache_of_exhaustive is not None:
            print_ind(", exhaustive", end="")
            new_best = better_than_best(best_allocation, cache_of_exhaustive)
            schedulable = is_schedulable(next_best_node.association, cache_sizes, util_bound, periods, get_wcet)
            if new_best:
                print_ind(f", new best, {'schedulable' if schedulable else 'not schedulable'}", end="")
            if new_best and schedulable:
                best_allocation = next_best_node
            print_ind("")
        else:
            print_ind(", non-exhaustive")
            next_i = len(next_best_node.association)
            assert(0 <= next_i < n)
            for j in range(k):
                inner_association = extend_iterable(next_best_node.association, j)
                best_case_inner = best_case_allocated_cache(inner_association, cache_sizes, n)
                if better_than_best(best_allocation, best_case_inner):
                    # Reassign iterable as it has been consumed
                    inner_association = extend_iterable(next_best_node.association, j)
                    next_node = CacheAllocation(tuple(inner_association), best_case_inner)
                    heapq.heappush(exploration_queue, next_node)
                    print_ind(f"Pushing[{j=}] {next_node.to_str(cache_sizes)}", p=p + 1)

    print(f"{iter_count=}")
    return best_allocation
