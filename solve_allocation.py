from branch_and_bound import branch_and_bound
from typing import Collection


def main():
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

    def get_wcet(i: int, j: int) -> float:
        # Computation made up for testing purposes
        CONSTANT_WORK = 1e-3
        CACHE_RELATED_WORK = 20e-3
        NO_CACHE_PENALTY = 100e-3
        cache_size = CACHE_PARTITION_SIZES[j]
        if cache_size == 0:
            return CONSTANT_WORK + NO_CACHE_PENALTY
        return CONSTANT_WORK + CACHE_RELATED_WORK / cache_size

    periods: Collection[float] = (2e-3, 1e-3, 4e-5)
    branch_and_bound(CACHE_PARTITION_SIZES, periods, get_wcet)

    print("Still working on it")


if __name__ == "__main__":
    main()
