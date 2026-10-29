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
        return 0.0

    periods: Collection[float] = []
    branch_and_bound(CACHE_PARTITION_SIZES, periods, get_wcet)

    print("Still working on it")


if __name__ == "__main__":
    main()
