#!/usr/bin/env python
from itertools import combinations
import unittest
from audioop import avg


class KnapSackItem(object):
    def __init__(self, name, value, weight):
        self.name = str(name)
        self.value = float(value)
        self.weight = float(weight)

    def __str__(self):
        return "({}, {}, {})".format(self.name, round(self.value,3), round(self.weight,3))

    def __repr__(self):
        return self.__str__()

class KnapSack(object):

    def __init__(self, num_of_items, max_weight):
        self.num_of_items = num_of_items
        self.max_weight = max_weight
        self.items = []

    def total_weight_available(self):
        w = 0.0
        for i in self.items:
            w += i.weight
        return w

    def combo_value_weight(self, combo):
        value = 0.0
        weight = 0.0
        for item in combo:
            value += item.value
            weight += item.weight
        return (value,weight)

    def solve(self):
        '''
        maximize value with these restrictions
        1) knapsack must have exactly num_of_items items
        2) knapsack must not exceed max_weight
        '''
        assert(self.num_of_items > 1)
        assert(len(self.items) > self.num_of_items)

        #print(self.items)
        combos = list(combinations(self.items, int(self.num_of_items)))

        combo_value = [0.0] * len(combos)
        combo_weight = [0.0] * len(combos)

        highest_value = None
        best_combo = None

        for i in range(len(combos)):
            combo_value[i], combo_weight[i] = self.combo_value_weight(combos[i])

            if combo_weight[i] > self.max_weight: continue

            if highest_value is None or combo_value[i] > highest_value:
                highest_value = combo_value[i]
                best_combo = combos[i]

        return best_combo

    def normalizeWeights(self, goal_total_weight):

        current_total_weight = self.total_weight_available()

        mult = float(goal_total_weight) / current_total_weight

        for item in self.items:
                item.weight *= mult


    def weightOptimize(self, n, bump=0):
        '''
        adjust weights to be optimal
        '''

        total_weight = self.total_weight_available()

        for _i in range(n):
            best_combo = self.solve()
            if best_combo is None: return
            combo_value, combo_weight = self.combo_value_weight(best_combo)

            avg_combo_value = combo_value / len(best_combo)
            #scrub_threshold = avg_combo_value / len(best_combo)
            scrub_threshold = avg_combo_value / 2

            combo_weight_increase = (self.max_weight - combo_weight) + bump
            #print(combo_weight_increase)
            weith_incr_mult = (combo_weight + combo_weight_increase) / combo_weight
            #weith_decr_mult = (total_weight - combo_weight - combo_weight_increase) / (total_weight - combo_weight)

            #print(best_combo)
            #print(self.items)
            #print(str((weith_incr_mult,weith_decr_mult)))

            for item in best_combo:
                if item.value > scrub_threshold:
                    item.weight *= weith_incr_mult

            self.normalizeWeights(goal_total_weight=total_weight)

            '''
            for item in set(self.items) - set(best_combo):
                item.weight *= weith_decr_mult
            '''


class TestKnapSack01(unittest.TestCase):

    def test_simple_case(self):
        ks = KnapSack(2, 10)
        ks.items.append(KnapSackItem('lunch', 1.3, 5))
        ks.items.append(KnapSackItem('book', 0.4, 4))
        ks.items.append(KnapSackItem('pencil', 0.91, 6))
        best_combo = ks.solve()
        print(best_combo)
        value, weight = ks.combo_value_weight(best_combo)
        self.assertAlmostEqual(value, 1.7)
        self.assertAlmostEqual(weight, 9)


    def testOptimizer(self):
        ks = KnapSack(num_of_items=4, max_weight=500)
        ks.items.append(KnapSackItem('a', 10, 10))
        ks.items.append(KnapSackItem('b', 20, 20))
        ks.items.append(KnapSackItem('c', 30, 30))
        ks.items.append(KnapSackItem('d', 40, 40))
        ks.items.append(KnapSackItem('e', 50, 50))
        ks.items.append(KnapSackItem('f', 60, 60))
        ks.items.append(KnapSackItem('g', 70, 80))
        ks.items.append(KnapSackItem('h', 80, 80))
        ks.items.append(KnapSackItem('i', 90, 90))

        #print(ks.items)
        ks.weightOptimize(n=10, bump=0.1)
        print(ks.items)
        best_combo = ks.solve()
        print(best_combo)
