import random
from math import comb


class ProbabilityEngine:
    def simple(self, favourable, total):
        if total <= 0:
            raise ValueError("Total outcomes must be positive.")
        return favourable / total

    def combinations(self, n, r):
        return comb(n, r)

    def roll_die(self, sides=6, times=1):
        return [random.randint(1, sides) for _ in range(times)]

    def flip_coin(self, times=1):
        return [random.choice(["Heads", "Tails"]) for _ in range(times)]

    def spin_spinner(self, sectors=8, times=1):
        return [random.randint(1, sectors) for _ in range(times)]

    def draw_card(self, times=1):
        suits = ["♠", "♥", "♦", "♣"]
        ranks = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
        deck = [f"{r}{s}" for s in suits for r in ranks]
        return random.sample(deck, min(times, len(deck)))

    def experimental_vs_theoretical(self, theoretical_p, trials, favourable_check):
        """favourable_check: callable applied to each simulated outcome to test success"""
        successes = sum(1 for _ in range(trials) if favourable_check())
        experimental = successes / trials if trials else 0
        return {"theoretical": theoretical_p, "experimental": experimental,
                "successes": successes, "trials": trials}
