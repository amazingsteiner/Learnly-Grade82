from math import comb
class ProbabilityEngine:
    def simple(self,favourable,total):
        if total<=0: raise ValueError("Total outcomes must be positive.")
        return favourable/total
    def combinations(self,n,r): return comb(n,r)
