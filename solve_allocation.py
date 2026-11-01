from branch_and_bound import branch_and_bound, is_schedulable, utilization_bound, best_case_allocated_cache, CacheAllocation
from typing import Collection, Sequence, Callable


def main():

    def best_brute_force(
            cache_sizes: Sequence[int],
            periods: Sequence[float],
            get_wcet: Callable[[int, int], float]):

        n = len(periods)
        k = len(cache_sizes)
        util_bound = utilization_bound(n)
        current_solution = [0] * n
        best_solution = None
        for branch_index in range(n):
            for j in range(k):
                current_solution[branch_index] = j
                current_cache_size = best_case_allocated_cache(current_solution, cache_sizes, n)
                schedulable = is_schedulable(current_solution, cache_sizes, util_bound, periods, get_wcet)
                if schedulable and ((best_solution is None) or (current_cache_size < best_solution[1])):
                    best_solution = (current_solution.copy(), current_cache_size)
        return (best_solution, n * k)


    CACHE_PARTITION_SIZES: tuple[int, ...] = (
        0,
        700,
        1024,
        # 2048,
        # 4096,
        # 8192,
        # 16384,
        # 32768,
        # 65536,
        # 131072,
        # 262144,
        # 524288,
        # 1048576,
        # 2097152,
        # 4194304,
    )

    def get_wcet(i: int, j: int) -> float:
        # Computation made up for testing purposes
        CONSTANT_WORK = 1e-3
        CACHE_RELATED_WORK = 10e-3
        NO_CACHE_PENALTY = 100e-3
        cache_size = CACHE_PARTITION_SIZES[j]
        if cache_size == 0:
            return CONSTANT_WORK + NO_CACHE_PENALTY
        return CONSTANT_WORK + CACHE_RELATED_WORK / cache_size

    PERIODS: Collection[float] = (10e-3, 20e-3) # , 40e-3
    best_allocation = branch_and_bound(CACHE_PARTITION_SIZES, PERIODS, get_wcet)
    assert(best_allocation is not None)
    assert(is_schedulable(best_allocation.association, CACHE_PARTITION_SIZES, utilization_bound(len(PERIODS)), PERIODS, get_wcet))

    brute_force, brute_force_iter_count = best_brute_force(CACHE_PARTITION_SIZES, PERIODS, get_wcet)
    assert(brute_force is not None)
    assert(is_schedulable(brute_force[0], CACHE_PARTITION_SIZES, utilization_bound(len(PERIODS)), PERIODS, get_wcet))


    print(f"{brute_force=}, explored {brute_force_iter_count}\n\n")
    print(f"{best_allocation=}")


if __name__ == "__main__":
    main()
