from statistics import mean, median, multimode, pstdev
import random


class DataEngine:
    def summary(self, values):
        v = sorted(float(x) for x in values)
        n = len(v)
        if not n:
            return {"count": 0}
        q1 = v[n // 4]
        q3 = v[(3 * n) // 4]
        iqr = q3 - q1
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        outliers = [x for x in v if x < lower_fence or x > upper_fence]
        return {
            "count": n, "sum": sum(v), "mean": round(mean(v), 3),
            "median": median(v), "mode": multimode(v),
            "minimum": min(v), "maximum": max(v), "range": max(v) - min(v),
            "q1": q1, "q3": q3, "iqr": iqr,
            "stdev": round(pstdev(v), 3) if n > 1 else 0,
            "sorted": v, "outliers": outliers,
            "five_number_summary": (min(v), q1, median(v), q3, max(v))
        }

    def frequency_table(self, values):
        table = {}
        for val in values:
            table[val] = table.get(val, 0) + 1
        return dict(sorted(table.items()))

    def grouped_frequency(self, values, n_classes=5):
        """Groups raw data into class intervals with frequency + cumulative frequency."""
        if not values:
            return []
        lo, hi = min(values), max(values)
        span = (hi - lo) or 1
        width = max(1, round(span / n_classes))
        classes = []
        start = lo
        while start <= hi:
            end = start + width
            classes.append([start, end, 0])
            start = end

        for v in values:
            for c in classes:
                if c[0] <= v < c[1] or (v == hi and c[1] == classes[-1][1]):
                    c[2] += 1
                    break

        cumulative = 0
        rows = []
        for lo_c, hi_c, freq in classes:
            cumulative += freq
            rows.append({
                "class": f"{lo_c:g}–{hi_c:g}",
                "frequency": freq,
                "cumulative_frequency": cumulative
            })
        return rows

    def random_dataset(self, n=8, low=1, high=50):
        return [random.randint(low, high) for _ in range(n)]
