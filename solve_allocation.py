"""Main file for solving the cache partitioning
problem through branch and bound and brute force"""

from branch_and_bound import pareto_front
from brute_force import best_brute_force
from solving_conditions import is_schedulable, utilization_bound, CACHE_PARTITION_SIZES, periods
import branch_and_bound, solving_conditions, sys, math


def main():

    n = len(periods)
    # k = len(CACHE_PARTITION_SIZES)
    util_bound = utilization_bound(n)

    wcet_count: list[int] = [0]

    def get_wcet(i: int, j: int):
        wcet_count[0] += 1
        return solving_conditions.get_wcet(i, j)

    def get_initial_guess():
        for j in range(len(CACHE_PARTITION_SIZES)):
            associations = tuple(j for _ in range(n))
            if is_schedulable(associations, util_bound, periods, get_wcet):
                return associations
        return None

    if 2 <= len(sys.argv) and sys.argv[1].lower() == "-p":
        wcet_count[0] = 0
        pareto = pareto_front(CACHE_PARTITION_SIZES, periods, get_wcet, max_iter=10000)
        sorted_pareto = sorted(pareto, key=lambda p: p[1])
        cache_max = sorted_pareto[-1][1]

        def prev_pow_10(x: float):
            return 10 ** math.floor(math.log10(x))

        cache_scaling = prev_pow_10(cache_max)

        def pareto_to_str(p: tuple[float, int]):
            return f"({p[1] / cache_scaling:.6f}, {p[0]:.6f})"

        print(f"cache * {cache_scaling}")
        print("[" + ", ".join(pareto_to_str(p) for p in sorted_pareto) + "]")
    else:
        # initial_guess = get_initial_guess()
        # assert(initial_guess is not None)
        branch_and_bound.log_enable = True
        wcet_count[0] = 0
        best_allocation = branch_and_bound.branch_and_bound(CACHE_PARTITION_SIZES, periods, get_wcet, initial_guess=None, max_iter=10000)
        bnb_wcet_count = wcet_count[0]
        assert(best_allocation is not None)
        assert(is_schedulable(best_allocation.association, util_bound, periods, get_wcet))

        print(f"best_allocation=({best_allocation.to_str(CACHE_PARTITION_SIZES)}), called wcet {bnb_wcet_count} times\n\n")
        
        brute_force, brute_force_iter_count, schedulable_count = best_brute_force(CACHE_PARTITION_SIZES, periods, get_wcet)
        assert(brute_force is not None)
        assert(is_schedulable(brute_force.association, util_bound, periods, get_wcet))

        print(f"brute_force=({brute_force.to_str(CACHE_PARTITION_SIZES)}), explored {brute_force_iter_count} combinations ({schedulable_count} schedulable)\n\n")


if __name__ == "__main__":
    main()
