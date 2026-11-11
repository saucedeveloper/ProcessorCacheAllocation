#!/usr/bin/python3

"""Parser for valgrind log files"""

import os
from typing import Iterable, Mapping
from dataclasses import dataclass
from collections import OrderedDict


VALGRIND_RESULT_FOLDERS = tuple(sorted(("pca_results/", "sphinx_results/", "disparity_results/")))
VALGRIND_RESULT_NAMES = tuple(folder.split('_')[0] for folder in VALGRIND_RESULT_FOLDERS)


@dataclass
class CacheGrindResult:
    I_refs: int      # Instruction references
    D_refs: int      # Data references
    I1_misses: int   # Instruction cache level 1 misses
    LLi_misses: int  # Level 1 instruction cache misses
    D1_misses: int   # Data cache level 1 misses
    LLd_misses: int  # Level 1 data cache misses
    LL_refs: int     # Level 2 references
    LL_misses: int   # Level 2 misses


    def get_L1d_hits(self) -> int:
        return self.D_refs

    def get_L1_misses(self) -> int:
        assert(self.I1_misses + self.D1_misses == self.LL_refs)
        l1_i_misses = self.I1_misses - self.LLi_misses
        d1_i_misses = self.D1_misses - self.LLd_misses
        assert(0 <= l1_i_misses)
        assert(0 <= d1_i_misses)
        assert(0 <= self.LL_refs)
        return self.LL_refs# - self.get_L2_misses()

    def get_L2_misses(self) -> int:
        return self.LL_misses


    def __str__(self):
        return (f"CacheGrindResult(\n"
                f"  Instruction References: {self.I_refs},\n"
                f"  Data References: {self.D_refs},\n"
                f"  Level 1 Instruction Misses: {self.I1_misses},\n"
                f"  Level 2 Instruction Cache Misses: {self.LLi_misses},\n"
                f"  Level 1 Data Misses: {self.D1_misses},\n"
                f"  Level 2 Data Cache Misses: {self.LLd_misses},\n"
                f"  Level 2 References: {self.LL_refs},\n"
                f"  Level 2 Misses: {self.LL_misses}\n"
                f")")


"""Get benchmark profiles from log files"""
def get_profiles() -> OrderedDict[str, OrderedDict[int, CacheGrindResult]]:

    def get_statistics(folder: str):
        for file in os.listdir(folder):

            I_refs = None
            I1_misses = None
            LLi_misses = None
            D_refs = None
            D1_misses = None
            LLd_misses = None
            LL_refs = None
            LL_misses = None

            cache_size = int(file.split('_')[-1].split('.')[0])
            with open(folder + file, 'r') as f:
                line = f.readline()
                while line != '':
                    # Check if I refs in line
                    if 'I refs' in line:
                        # Read instruction number
                        I_refs = int(line.split(':')[1].strip().replace(',', ''))

                    if 'I1  misses' in line:
                        I1_misses = int(line.split(':')[1].strip().replace(',', ''))

                    if 'LLi misses' in line:
                        LLi_misses = int(line.split(':')[1].strip().replace(',', ''))

                    if 'D refs' in line:
                        data = line.split(':')[1].strip().replace(',', '').split('(')
                        D_refs = int(data[0].strip())

                    if 'D1  misses' in line:
                        data = line.split(':')[1].strip().replace(',', '').split('(')
                        D1_misses = int(data[0].strip())

                    if 'LLd misses' in line:
                        data = line.split(':')[1].strip().replace(',', '').split('(')
                        LLd_misses = int(data[0].strip())

                    if 'LL refs' in line:
                        data = line.split(':')[1].strip().replace(',', '').split('(')
                        LL_refs = int(data[0].strip())

                    if 'LL misses' in line:
                        data = line.split(':')[1].strip().replace(',', '').split('(')
                        LL_misses = int(data[0].strip())

                    line = f.readline()

            assert(I_refs is not None) # I_refs not found
            assert(D_refs is not None) # D_refs not found
            assert(I1_misses is not None) # I1_misses not found
            assert(LLi_misses is not None) # LLi_misses not found
            assert(D1_misses is not None) # D1_misses not found
            assert(LLd_misses is not None) # LLd_misses not found
            assert(LL_refs is not None) # LL_refs not found
            assert(LL_misses is not None) # LL_misses not found

            cache_grind_result = CacheGrindResult(I_refs, D_refs, I1_misses, LLi_misses, D1_misses, LLd_misses, LL_refs, LL_misses)
            yield (cache_size, cache_grind_result)

    def enumerate_profiles(folders: Iterable[str]):
        for folder in folders:
            benchmark_name = folder.split('_')[0]
            # Read all result files
            statistics_from_folder = get_statistics(folder)
            statistics_set: OrderedDict[int, CacheGrindResult] = OrderedDict()
            for size, result in statistics_from_folder:
                statistics_set[size] = result
            yield (benchmark_name, statistics_set)

    result: OrderedDict[str, OrderedDict[int, CacheGrindResult]] = OrderedDict()
    for name, profile in enumerate_profiles(VALGRIND_RESULT_FOLDERS):
        result[name] = profile
    return result


"""Print `profiles`"""
def print_profiles(profiles: Mapping[str, Mapping[int, CacheGrindResult]]):
    benchmark_names = profiles.keys()
    for benchmark in benchmark_names:
        print(benchmark)
        cache_sizes: Iterable[int] = profiles[benchmark].keys()
        for size in sorted(cache_sizes):
            print(f"cache size: {str(size).ljust(10)}\tLL misses: {str(profiles[benchmark][size].LL_misses).ljust(12)}")
        print()


def main():
    print_profiles(get_profiles())


if __name__ == "__main__":
    main()
