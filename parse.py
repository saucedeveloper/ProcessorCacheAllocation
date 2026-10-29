#!/usr/bin/python3
import os
from math import ceil
from collections import defaultdict
from typing import Any, Iterable
from functools import singledispatch


valgrind_result_folders=["pca_results/", "sphinx_results/", "disparity_results/"]


class CacheGrindResult:
    @singledispatch
    def __init__(self, I_refs: int, D_refs: str, I1_misses: int, LLi_misses: int, D1_misses: str, LLd_misses: str, LL_refs: str, LL_misses: str):
        self.I_refs = I_refs              # Instruction references
        self.D_refs = D_refs              # Data references
        self.I1_misses = I1_misses        # Instruction cache level 1 misses
        self.LLi_misses = LLi_misses      # Level 1 instruction cache misses
        self.D1_misses = D1_misses        # Data cache level 1 misses
        self.LLd_misses = LLd_misses      # Level 1 data cache misses
        self.LL_refs = LL_refs            # Level 2 references
        self.LL_misses = LL_misses        # Level 2 misses


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


profiles: defaultdict[str, defaultdict[str, CacheGrindResult]] = defaultdict(lambda: defaultdict(CacheGrindResult))


for valgrind_result_folder in valgrind_result_folders:
    benchmark_name = valgrind_result_folder.split('_')[0]
    # Read all result files
    for file in os.listdir(valgrind_result_folder):

        I_refs = None
        I1_misses = None
        LLi_misses = None
        D_refs = None
        D1_misses = None
        LLd_misses = None
        LL_refs = None
        LL_misses = None

        cache_size = int(file.split('_')[-1].split('.')[0])
        with open(valgrind_result_folder + file, 'r') as f:
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
                    D_refs = data[0].strip()

                if 'D1  misses' in line:
                    data = line.split(':')[1].strip().replace(',', '').split('(')
                    D1_misses = data[0].strip()

                if 'LLd misses' in line:
                    data = line.split(':')[1].strip().replace(',', '').split('(')
                    LLd_misses = data[0].strip()

                if 'LL refs' in line:
                    data = line.split(':')[1].strip().replace(',', '').split('(')
                    LL_refs = data[0].strip()

                if 'LL misses' in line:
                    data = line.split(':')[1].strip().replace(',', '').split('(')
                    LL_misses = data[0].strip()

                line = f.readline()

        if I_refs is None: raise ValueError("I_refs not found")
        if D_refs is None: raise ValueError("D_refs not found")
        if I1_misses is None: raise ValueError("I1_misses not found")
        if LLi_misses is None: raise ValueError("LLi_misses not found")
        if D1_misses is None: raise ValueError("D1_misses not found")
        if LLd_misses is None: raise ValueError("LLd_misses not found")
        if LL_refs is None: raise ValueError("LL_refs not found")
        if LL_misses is None: raise ValueError("LL_misses not found")

        profiles[benchmark_name][cache_size]=CacheGrindResult(I_refs, D_refs, I1_misses, LLi_misses, D1_misses, LLd_misses, LL_refs, LL_misses)


for benchmark in ['pca', 'sphinx', 'disparity']:
    print(benchmark)
    cache_sizes: Iterable[int] = profiles[benchmark].keys()
    for size in sorted(cache_sizes):
        print(f"cache size: {size}\tLL misses: {profiles[benchmark][size].LL_misses}")
    print()



