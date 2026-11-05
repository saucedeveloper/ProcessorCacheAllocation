from branch_and_bound import branch_and_bound
from brute_force import best_brute_force

from solving_conditions import is_schedulable, utilization_bound, CACHE_PARTITION_SIZES, periods
import solving_conditions

# pareto front with x = cache_size, y = processor utilization


def main():

    n = len(periods)
    # k = len(CACHE_PARTITION_SIZES)
    util_bound = utilization_bound(n)
    print(f"{util_bound=}, {periods=}")

    wcet_count: list[int] = [0]

    def get_wcet(i: int, j: int):
        wcet_count[0] += 1
        return solving_conditions.get_wcet(i, j)

    def get_initial_guess():
        for j in range(len(CACHE_PARTITION_SIZES)):
            associations = tuple(j for _ in range(n))
            if is_schedulable(associations, CACHE_PARTITION_SIZES, util_bound, periods, get_wcet)[0]:
                return associations
        return None

    initial_guess = None #get_initial_guess()
    # assert(initial_guess is not None)
    best_allocation = branch_and_bound(CACHE_PARTITION_SIZES, periods, get_wcet, initial_guess, max_iter=10000)
    assert(best_allocation is not None)
    assert(is_schedulable(best_allocation.association, CACHE_PARTITION_SIZES, util_bound, periods, get_wcet)[0])

    brute_force, brute_force_iter_count, schedulable_count = best_brute_force(CACHE_PARTITION_SIZES, periods, get_wcet)
    assert(brute_force is not None)
    assert(is_schedulable(brute_force.association, CACHE_PARTITION_SIZES, util_bound, periods, get_wcet)[0])


    print(f"wcet_count={wcet_count[0]}, best_allocation=({best_allocation.to_str(CACHE_PARTITION_SIZES)})\n\n")
    print(f"brute_force=({brute_force.to_str(CACHE_PARTITION_SIZES)}), explored {brute_force_iter_count} ({schedulable_count=})\n\n")


if __name__ == "__main__":
    main()
