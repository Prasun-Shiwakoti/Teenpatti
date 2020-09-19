
def declare_winer(card_owner):

    def con_int(n):
        lett = {"A": 1, "J": 11, "Q": 12, "K": 13}
        return int(n) if n not in lett else lett[n]

    def get_spec(classes, values):
        specs = []
        values = list(map(con_int, values))
        s_values = sorted(values)
        if len(set(classes)) == 1:
            specs.append("color")
        if len(set(values)) == 1:
            specs.append(trial)
        elif len(set(values)) == 2:
            specs.append(jut)
        elif (s_values[0] + s_values[2]) / 2 == s_values[1]:
            specs.append(run)
        elif set(s_values) == {1, 12, 13}:
            specs.append(run)
        else:
            specs.append(top)

        return specs

    def top(card_owner):
        val1, val2 = card_owner.keys()
        temp_val1 = val1.split(" ")
        temp_val2 = val2.split(" ")

        replaces = {"A": 14, "J": 11, "Q": 12, "K": 13}
        for vals in [temp_val1, temp_val2]:
            for index, val in enumerate(vals):
                if val in replaces:
                    vals[index] = replaces[val]

        s_val1 = list(map(int, temp_val1))
        s_val2 = list(map(int, temp_val2))

        s_val1 = sorted(s_val1)
        s_val2 = sorted(s_val2)

        pos = -1
        while True:
            if s_val1[pos] > s_val2[pos]:
                print(card_owner)
                return card_owner[val1]
            elif s_val1[pos] < s_val2[pos]:
                return card_owner[val2]
            else:
                if pos == -3:
                    return "DRAW"
                pos -= 1

    def jut(card_owner):
        val1_str, val2_str = card_owner.keys()
        val1 = val1_str.split(" ")
        val2 = val2_str.split(" ")

        replaces = {"A": 14, "J": 11, "Q": 12, "K": 13}
        for vals in [val1, val2]:
            for index, val in enumerate(vals):
                if val in replaces:
                    vals[index] = replaces[val]

        val1 = list(map(int, val1))
        val2 = list(map(int, val2))

        for i in val1:
            if val1.count(i) > 1:
                val1_jut = i

        for i in val2:
            if val2.count(i) > 1:
                val2_jut = i

        if val1_jut > val2_jut:
            return card_owner[val1_str]
        elif val1_jut < val2_jut:
            return card_owner[val2_str]
        else:
            (val1_none_rep,) = set(val1) - {val1_jut}
            (val2_none_rep,) = set(val2) - {val2_jut}
            print(val1_none_rep, val2_none_rep)

            if val1_none_rep > val2_none_rep:
                return card_owner[val1_str]
            elif val1_none_rep < val2_none_rep:
                return card_owner[val2_str]
            else:
                return "DRAW"

    def run(card_owner):
        val1_str, val2_str = card_owner.keys()
        val1 = val1_str.split(" ")
        val2 = val2_str.split(" ")

        replaces = {"A": 14, "J": 11, "Q": 12, "K": 13}
        for vals in [val1, val2]:
            for index, val in enumerate(vals):
                if val in replaces:
                    vals[index] = replaces[val]

        val1 = list(map(int, val1))
        val2 = list(map(int, val2))

        if max(val1) > max(val2):
            return card_owner[val1_str]
        elif max(val1) < max(val2):
            return card_owner[val2_str]
        else:
            if sum(val1) > sum(val2):
                return card_owner[val1_str]
            elif sum(val1) < sum(val2):
                return card_owner[val2_str]
            else:
                return "DRAW"

    def trial(card_owner):
        val1_str, val2_str = card_owner.keys()
        val1 = val1_str.split(" ")
        val2 = val2_str.split(" ")

        replaces = {"A": 14, "J": 11, "Q": 12, "K": 13}
        for vals in [val1, val2]:
            for index, val in enumerate(vals):
                if val in replaces:
                    vals[index] = replaces[val]

        val1 = list(map(int, val1))
        val2 = list(map(int, val2))

        if val1[0] > val2[0]:
            return card_owner[val1_str]
        elif val1[0] < val2[0]:
            return card_owner[val2_str]
        else:
            return "DRAW"

    def get_points(specs):
        points = 0
        for spec in specs:
            points += spec_points[spec]
        return points

    card1_str, card2_str = card_owner.keys()

    card1 = card1_str.split(" ")
    card2 = card2_str.split(" ")

    card_points = {
        card1_str: int,
        card2_str: int
    }

    values1 = []
    class1 = []

    values2 = []
    class2 = []

    spec_points = {top: 1, jut: 2, "color": 3, run: 6, trial: 10}

    for card in card1:
        class_, value = list(card)
        values1.append(value)
        class1.append(class_)

    for card in card2:
        class_, value = list(card)
        values2.append(value)
        class2.append(class_)

    specs1 = get_spec(class1, values1)
    specs2 = get_spec(class2, values2)

    card_points[card1_str] = get_points(specs1)
    card_points[card2_str] = get_points(specs2)

    if card_points[card1_str] > card_points[card2_str]:
        winner = card_owner[card1_str]
    elif card_points[card1_str] < card_points[card2_str]:
        winner = card_owner[card2_str]
    else:
        winner = specs1[-1]({
            " ".join(values1): card_owner[card1_str],
            " ".join(values2): card_owner[card2_str]
        })

    return winner
