import random, math

# Difficulty: 1=Foundation 2=Standard 3=Advanced 4=Elite

class QuestionEngine:
    TOPICS = [
        "number_sense", "whole_numbers", "integers", "exponents", "patterns",
        "algebraic_expressions", "algebraic_equations", "geometry_lines",
        "pythagoras", "area_perimeter", "financial_maths",
        "transformations", "data_handling", "probability"
    ]

    NAMES = {
        "number_sense": "Number Sense", "whole_numbers": "Whole Numbers", "integers": "Integers",
        "exponents": "Exponents", "patterns": "Numeric Patterns",
        "algebraic_expressions": "Algebraic Expressions",
        "algebraic_equations": "Algebraic Equations",
        "geometry_lines": "Geometry of Straight Lines",
        "pythagoras": "Theorem of Pythagoras",
        "area_perimeter": "Area & Perimeter",
        "financial_maths": "Financial Mathematics",
        "transformations": "Transformation Geometry",
        "data_handling": "Data Handling", "probability": "Probability"
    }

    def generate(self, topic=None, difficulty=1):
        topic = topic if topic in self.TOPICS else random.choice(self.TOPICS)
        difficulty = max(1, min(4, int(difficulty)))
        return getattr(self, "_" + topic)(difficulty)

    def _base(self, topic, q, a, d, hint, exp, diagram=None):
        return {
            "id": f"{topic}_{random.randint(100000,999999)}",
            "topic": topic, "topic_name": self.NAMES[topic],
            "question": q, "answer": str(a), "difficulty": d,
            "hint": hint, "explanation": exp, "marks": d,
            "diagram": diagram
        }

    # ---------------- NUMBER SENSE (new) ----------------
    def _number_sense(self, d):
        mode = random.choice(["add10", "numberline", "compensation", "friendly_mult",
                               "basic_div", "double_half"]) if d > 1 else \
               random.choice(["add10", "numberline", "basic_div"])

        if mode == "add10":
            a = random.randint(1, 9)
            b = random.randint(10 - a, 9)
            return self._base("number_sense", f"Use 'making 10' to add: {a} + {b}", a + b, d,
                f"Take {10-a} from {b} to make {a} up to 10, then add what's left of {b}.",
                f"{a} + {10-a} = 10. {b} − {10-a} = {b-(10-a)}. So 10 + {b-(10-a)} = {a+b}.")

        elif mode == "numberline":
            start = random.randint(-10, 10)
            jump = random.randint(-8, 8) or 3
            return self._base("number_sense", f"On a number line, start at {start} and jump {jump} spaces "
                               f"({'right' if jump>0 else 'left'}). Where do you land?", start + jump, d,
                f"Move {abs(jump)} spaces {'right (add)' if jump>0 else 'left (subtract)'} from {start}.",
                f"{start} {'+' if jump>=0 else '−'} {abs(jump)} = {start+jump}.")

        elif mode == "compensation":
            a = random.randint(20, 90)
            b = random.choice([9, 19, 29, 39, 49, 98, 99])
            ans = a + b
            round_b = b + 1
            return self._base("number_sense", f"Use compensation to calculate: {a} + {b}", ans, d,
                f"Round {b} up to {round_b} (add {round_b-b}), add, then subtract {round_b-b} back.",
                f"{a} + {round_b} = {a+round_b}, then {a+round_b} − {round_b-b} = {ans}.")

        elif mode == "friendly_mult":
            a = random.randint(4, 40)
            choice = random.choice([("x5","x10 ÷ 2",5), ("x25","x100 ÷ 4",25),
                                     ("x50","x100 ÷ 2",50), ("x9","x10 − original",9)])
            label, method, mult = choice
            ans = a * mult
            return self._base("number_sense", f"Use the {label} trick: {a} × {mult}", ans, d,
                f"{label} = {method}.",
                f"{a} × {mult} = {ans} using {method}.")

        elif mode == "basic_div":
            b = random.randint(2, 12)
            q = random.randint(2, 20)
            a = b * q
            return self._base("number_sense", f"Calculate: {a} ÷ {b}", q, d,
                f"Think: {b} × ? = {a}. Use known multiplication facts.",
                f"{b} × {q} = {a}, so {a} ÷ {b} = {q}.")

        else:  # double_half
            a = random.randint(4, 60)
            b = random.choice([4, 8, 16, 6, 12])
            ans = a * b
            return self._base("number_sense", f"Use doubling and halving: {a} × {b}", ans, d,
                "Halve one number and double the other until it's easy to multiply.",
                f"E.g. halve {b} and double {a} repeatedly until simple, then multiply: {a} × {b} = {ans}.")

    # ---------------- WHOLE NUMBERS ----------------
    def _whole_numbers(self, d):
        if d <= 2:
            a, b = random.randint(10, 40), random.randint(2, 12)
            op = random.choice(["+", "-", "*"])
            expr = f"{a} {op} {b}"
            ans = eval(expr)
            return self._base("whole_numbers", f"Calculate: {a} {op} {b}", ans, d,
                f"Work left to right: {a} {op} {b}.", f"{a} {op} {b} = {ans}.")
        else:
            n1, n2 = random.choice([(36,60),(24,84),(18,48),(60,72)])
            def pf(n):
                f, x = {}, 2
                while x*x <= n:
                    while n % x == 0:
                        f[x] = f.get(x,0)+1; n//=x
                    x += 1
                if n > 1: f[n] = f.get(n,0)+1
                return f
            f1, f2 = pf(n1), pf(n2)
            common = set(f1) & set(f2)
            hcf = 1
            for p in common: hcf *= p**min(f1[p], f2[p])
            return self._base("whole_numbers", f"Find the HCF of {n1} and {n2}.", hcf, d,
                f"Break {n1} and {n2} into prime factors, then multiply the lowest common powers.",
                f"{n1} and {n2} share prime factors giving HCF = {hcf}.")

    # ---------------- INTEGERS ----------------
    def _integers(self, d):
        a = random.randint(-15, 15) or 3
        b = random.randint(-15, 15) or 4
        op = random.choice(["+", "-", "*"]) if d < 3 else random.choice(["*", "/"])
        if op == "/":
            b = random.choice([2,3,4,5,6]) * random.choice([-1,1])
            a = b * random.randint(-8, 8)
        expr = f"({a}) {op} ({b})"
        ans = eval(expr) if op != "/" else a // b
        display_op = '×' if op == '*' else ('÷' if op == '/' else op)
        return self._base("integers", f"Calculate: {a} {display_op} {b}", ans, d,
            f"{a} and {b}: same signs give a positive result, different signs give a negative result.",
            f"{a} {op} {b} = {ans}.")

    # ---------------- EXPONENTS ----------------
    def _exponents(self, d):
        a = random.randint(2, 5)
        x, y = random.randint(1, 3+d), random.randint(1, 3+d)
        mode = random.choice(["mul","div","pow"]) if d>1 else "mul"
        if mode == "mul":
            return self._base("exponents", f"Simplify: {a}^{x} × {a}^{y}", a**(x+y), d,
                f"Same base ({a}): add the exponents {x} + {y}.", f"{a}^{x} × {a}^{y} = {a}^{x+y} = {a**(x+y)}.")
        elif mode == "div":
            hi = max(x,y)+2
            return self._base("exponents", f"Simplify: {a}^{hi} ÷ {a}^{x}", a**(hi-x), d,
                f"Same base ({a}): subtract the exponents {hi} − {x}.",
                f"{a}^{hi} ÷ {a}^{x} = {a}^{hi-x} = {a**(hi-x)}.")
        else:
            return self._base("exponents", f"Simplify: ({a}^{x})^{y}", a**(x*y), d,
                f"Power of a power: multiply the exponents {x} × {y}.",
                f"({a}^{x})^{y} = {a}^{x*y} = {a**(x*y)}.")

    # ---------------- PATTERNS ----------------
    def _patterns(self, d):
        diff = random.randint(2, 6)
        start = random.randint(1, 10)
        terms = [start + diff*i for i in range(5)]
        c = start - diff
        if d <= 2:
            seq = ", ".join(map(str, terms[:4])) + ", ..."
            return self._base("patterns", f"Find the next term: {seq}", terms[4], d,
                f"The common difference is {diff}. Add {diff} to the last term ({terms[3]}).",
                f"Common difference = {diff}. Next term = {terms[3]} + {diff} = {terms[4]}.")
        else:
            n = random.randint(8, 20)
            ans = diff*n + c
            seq = ", ".join(map(str, terms[:4])) + ", ..."
            return self._base("patterns", f"Sequence: {seq}\nFind term number {n}.", ans, d,
                f"General term: Tn = {diff}n + ({c}). Substitute n = {n}.",
                f"Tn = {diff}n + ({c}). T{n} = {diff}({n}) + ({c}) = {ans}.")

    # ---------------- ALGEBRAIC EXPRESSIONS ----------------
    def _algebraic_expressions(self, d):
        if d <= 2:
            a1,a2,b1,b2 = [random.randint(1,9) for _ in range(4)]
            expr = f"{a1}x + {b1}y - {a2}x + {b2}y"
            rx, ry = a1-a2, b1+b2
            ans = f"{rx}x + {ry}y"
            return self._base("algebraic_expressions", f"Simplify: {expr}", ans, d,
                f"Collect x-terms: {a1}x − {a2}x. Collect y-terms: {b1}y + {b2}y.",
                f"({a1}x - {a2}x) + ({b1}y + {b2}y) = {ans}.")
        else:
            m, c, x = random.randint(2,6), random.randint(-8,8), random.randint(-5,5)
            ans = m*x*x + c if d==4 else m*x + c
            expr = f"{m}x^2 + ({c})" if d==4 else f"{m}x + ({c})"
            return self._base("algebraic_expressions", f"If x = {x}, evaluate {expr}", ans, d,
                f"Substitute x = {x} using brackets: {expr.replace('x', f'({x})')}.",
                f"Substituting x={x}: {expr.replace('x', f'({x})')} = {ans}.")

    # ---------------- ALGEBRAIC EQUATIONS ----------------
    def _algebraic_equations(self, d):
        x = random.randint(-10, 12) or 3
        a = random.randint(2, 9)
        b = random.randint(1, 20)
        c = a*x + b
        return self._base("algebraic_equations", f"Solve for x: {a}x + {b} = {c}", x, d,
            f"Subtract {b} from both sides to get {a}x = {c-b}, then divide by {a}.",
            f"{a}x = {c} - {b} = {c-b}, so x = {c-b}/{a} = {x}.")

    # ---------------- GEOMETRY OF STRAIGHT LINES ----------------
    def _geometry_lines(self, d):
        mode = random.choice(["line","point","vert"])
        if mode == "line":
            known = random.randint(30, 150)
            ans = 180 - known
            return self._base("geometry_lines", f"Two angles on a straight line are x and {known}°. Find x.", ans, d,
                f"Angles on a straight line add up to 180°. Subtract {known}° from 180°.",
                f"x = 180° - {known}° = {ans}°.",
                diagram={"type":"straight_line_angles","known":known})
        elif mode == "point":
            a1, a2 = random.randint(60,150), random.randint(60,150)
            ans = 360 - a1 - a2
            return self._base("geometry_lines", f"Three angles around a point are {a1}°, {a2}° and y. Find y.", ans, d,
                f"Angles around a point add up to 360°. Subtract {a1}° and {a2}° from 360°.",
                f"y = 360° - {a1}° - {a2}° = {ans}°.",
                diagram={"type":"angles_at_point","a":a1,"b":a2})
        else:
            known = random.randint(20, 160)
            return self._base("geometry_lines", f"Two lines cross. One angle is {known}°. Find its vertically opposite angle.", known, d,
                "Vertically opposite angles are always equal — no calculation needed.",
                f"Vertically opposite angle = {known}°.",
                diagram={"type":"vertical_angles","known":known})

    # ---------------- PYTHAGORAS ----------------
    def _pythagoras(self, d):
        triples = [(3,4,5),(6,8,10),(5,12,13),(9,12,15),(8,15,17),(7,24,25)]
        a,b,c = random.choice(triples)
        if random.random() < 0.5:
            return self._base("pythagoras", f"A right triangle has legs {a} cm and {b} cm. Find the hypotenuse.", c, d,
                f"c² = {a}² + {b}², then take the square root.", f"c² = {a}²+{b}² = {a*a+b*b}, c = √{a*a+b*b} = {c} cm.",
                diagram={"type":"right_triangle","a":a,"b":b,"c":c,"find":"c"})
        else:
            return self._base("pythagoras", f"A right triangle has hypotenuse {c} cm and one leg {a} cm. Find the other leg.", b, d,
                f"b² = {c}² − {a}², then take the square root.",
                f"b² = {c}²-{a}² = {c*c-a*a}, b = √{c*c-a*a} = {b} cm.",
                diagram={"type":"right_triangle","a":a,"c":c,"find":"b"})

    # ---------------- AREA & PERIMETER ----------------
    def _area_perimeter(self, d):
        mode = random.choice(["rect_area","rect_perim","triangle","circle"])
        if mode == "rect_area":
            l, w = random.randint(4,20), random.randint(3,15)
            return self._base("area_perimeter", f"Find the area of a rectangle {l} cm by {w} cm.", l*w, d,
                f"Area = length × width = {l} × {w}.", f"{l} × {w} = {l*w} cm².",
                diagram={"type":"rectangle","l":l,"w":w})
        elif mode == "rect_perim":
            l, w = random.randint(4,20), random.randint(3,15)
            return self._base("area_perimeter", f"Find the perimeter of a rectangle {l} cm by {w} cm.", 2*(l+w), d,
                f"Perimeter = 2 × (length + width) = 2 × ({l} + {w}).", f"2({l}+{w}) = {2*(l+w)} cm.",
                diagram={"type":"rectangle","l":l,"w":w})
        elif mode == "triangle":
            b, h = random.randint(6,20), random.randint(4,14)
            area = b*h/2
            ans = int(area) if area==int(area) else area
            return self._base("area_perimeter", f"Find the area of a triangle with base {b} cm and height {h} cm.", ans, d,
                f"Area = ½ × base × height = ½ × {b} × {h}.", f"½ × {b} × {h} = {ans} cm².",
                diagram={"type":"triangle_bh","b":b,"h":h})
        else:
            r = random.choice([7,14,21,10,20])
            area = round(3.142*r*r, 1) if r not in (7,14,21) else int((22/7)*r*r)
            return self._base("area_perimeter", f"Find the area of a circle with radius {r} cm (use π≈22/7 or 3.142).", area, d,
                f"Area = πr² = π × {r}².", f"π × {r}² ≈ {area} cm².", diagram={"type":"circle","r":r})

    # ---------------- FINANCIAL MATHS ----------------
    def _financial_maths(self, d):
        mode = random.choice(["interest","profit"])
        if mode == "interest":
            p = random.choice([1000,2000,5000,3000,4000])
            r = random.choice([5,6,8,10,12])
            t = random.randint(1,5)
            interest = p*(r/100)*t
            return self._base("financial_maths",
                f"R{p} is invested at {r}% simple interest per year for {t} years. Find the interest earned.",
                int(interest), d, f"I = P × r × t = {p} × {r/100} × {t}.",
                f"I = {p} × {r/100} × {t} = R{int(interest)}.")
        else:
            cost = random.randint(200, 900)
            profit_pct = random.choice([10,15,20,25,30])
            selling = cost + cost*profit_pct//100
            return self._base("financial_maths",
                f"An item costs R{cost} and is sold for R{selling}. Find the profit percentage.",
                profit_pct, d, f"Profit = R{selling}-R{cost}. Profit % = (profit ÷ cost) × 100.",
                f"Profit = R{selling-cost}. % = ({selling-cost}/{cost})×100 = {profit_pct}%.")

    # ---------------- TRANSFORMATIONS ----------------
    def _transformations(self, d):
        x, y = random.randint(-8,8), random.randint(-8,8)
        mode = random.choice(["translate","reflect_x","reflect_y"])
        if mode == "translate":
            a, b = random.randint(-6,6), random.randint(-6,6)
            return self._base("transformations", f"Translate point ({x}, {y}) by vector ({a}, {b}). Give the new point.",
                f"({x+a}, {y+b})", d, f"Add {a} to x and {b} to y.", f"({x}+{a}, {y}+{b}) = ({x+a}, {y+b}).",
                diagram={"type":"translation","x":x,"y":y,"a":a,"b":b})
        elif mode == "reflect_x":
            return self._base("transformations", f"Reflect point ({x}, {y}) over the x-axis.", f"({x}, {-y})", d,
                "Reflecting over the x-axis flips the sign of the y-coordinate only.", f"({x}, {y}) → ({x}, {-y}).",
                diagram={"type":"reflect_x","x":x,"y":y})
        else:
            return self._base("transformations", f"Reflect point ({x}, {y}) over the y-axis.", f"({-x}, {y})", d,
                "Reflecting over the y-axis flips the sign of the x-coordinate only.", f"({x}, {y}) → ({-x}, {y}).",
                diagram={"type":"reflect_y","x":x,"y":y})

    # ---------------- DATA HANDLING ----------------
    def _data_handling(self, d):
        vals = [random.randint(2, 40) for _ in range(6 if d<3 else 8)]
        mode = random.choice(["mean","median","range"])
        if mode == "mean":
            m = sum(vals)/len(vals)
            ans = round(m,2) if m != int(m) else int(m)
            return self._base("data_handling", f"Find the mean of: {', '.join(map(str,vals))}", ans, d,
                f"Add all {len(vals)} values, then divide by {len(vals)}.", f"Sum={sum(vals)}, n={len(vals)}, mean={ans}.")
        elif mode == "median":
            sv = sorted(vals)
            n = len(sv)
            med = sv[n//2] if n%2 else (sv[n//2-1]+sv[n//2])/2
            ans = med if med != int(med) else int(med)
            return self._base("data_handling", f"Find the median of: {', '.join(map(str,vals))}", ans, d,
                "Order the data first, then find the middle value.", f"Ordered: {sv}. Median = {ans}.")
        else:
            ans = max(vals)-min(vals)
            return self._base("data_handling", f"Find the range of: {', '.join(map(str,vals))}", ans, d,
                f"Range = maximum ({max(vals)}) − minimum ({min(vals)}).", f"{max(vals)} − {min(vals)} = {ans}.")

    # ---------------- PROBABILITY ----------------
    def _probability(self, d):
        mode = random.choice(["die","bag"])
        if mode == "die":
            target = random.choice(["even","odd","greater than 4","less than 3","a 6"])
            fav = {"even":3,"odd":3,"greater than 4":2,"less than 3":2,"a 6":1}[target]
            g = math.gcd(fav,6)
            ans = f"{fav//g}/{6//g}"
            return self._base("probability", f"A fair die is rolled. Find P({target}).", ans, d,
                f"{fav} of the 6 faces satisfy this. P = {fav}/6.", f"{fav}/6 simplifies to {ans}.")
        else:
            red, blue = random.randint(2,8), random.randint(2,8)
            total = red+blue
            g = math.gcd(red,total)
            ans = f"{red//g}/{total//g}"
            return self._base("probability", f"A bag has {red} red and {blue} blue balls. Find P(red).", ans, d,
                f"P(red) = {red} red ÷ {total} total balls.", f"{red}/{total} simplifies to {ans}.")
