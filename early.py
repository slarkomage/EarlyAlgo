from collections import defaultdict
import queue


class IncorrectRule(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)


class NotCFGGrammar(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)


class Rule:
    def __init__(self, *rule_data):
        if (len(rule_data) == 1):
            rule_statement = rule_data[0]
            if rule_statement.startswith("->") or (not "->" in rule_statement):
                raise IncorrectRule("Wrong rule statement!")
            lhs = rule_statement.split("->")[0]
            rhs = ""
            if (len(lhs) + 2 < len(rule_statement)):
                rhs = rule_statement.split("->")[1]
            self.lhs = lhs
            self.rhs = rhs

        elif len(rule_data) == 2:
            self.lhs = rule_data[0]
            self.rhs = rule_data[1]

    def Compare(self, other) -> bool:
        return (self.lhs == other.lhs) and (self.rhs == other.rhs)

    def __eq__(self, other) -> bool:
        return (self.lhs == other.lhs) and (self.rhs == other.rhs)


class Grammar:
    def __init__(self, term_alphabet, nonterm_alphabet, rules_list, start_symbol):
        self.term_alphabet = term_alphabet
        self.nonterm_alpahbet = nonterm_alphabet
        self.start_symbol = start_symbol
        self.rules = defaultdict(list)
        for single_rule in rules_list:
            self.rules[single_rule.lhs].append(single_rule.rhs)

    def AddRule(self, single_rule):
        self.rules[single_rule.lhs].append(single_rule.rhs)

    def AddStartRule(self, new_start_rule):
        self.AddRule(new_start_rule)
        self.start_symbol = new_start_rule.lhs
        self.nonterm_alpahbet.append(new_start_rule.lhs)

    def CheckCFG(self) -> bool:
        for lhs in self.rules:
            if (len(lhs) != 1) or (lhs not in self.nonterm_alpahbet):
                return False
        for term in self.term_alphabet:
            if term in self.nonterm_alpahbet:
                return False
        return True


class Situation:
    # (A -> a*b, i, j)
    def __init__(self, single_rule, pos, i, j):
        self.rule = single_rule
        self.pos = pos
        self.i = i
        self.j = j

    def ScanSymbol(self):
        return Situation(self.rule, self.pos + 1, self.i, self.j + 1)

    def PredictRule(self, rule):
        return Situation(rule, 0, self.j, self.j)

    def CompleteAndGoUpper(self, upper):
        return Situation(upper.rule, upper.pos + 1, upper.i, self.j)

    def GetSymbolAfterDot(self):
        next_symbol = '$'
        if (self.pos < len(self.rule.rhs)):
            next_symbol = self.rule.rhs[self.pos]
        return next_symbol

    def __hash__(self) -> int:
        return (hash(self.rule.lhs) + hash(self.rule.rhs) + hash(self.i) + hash(self.j) + hash(self.pos))

    def __eq__(self, other) -> bool:
        return (self.rule == other.rule) and (self.i == other.i) and (self.pos == other.pos) and (self.j == other.j)


class Early:
    def __init__(self):
        pass

    def fit(self, grammar):
        # we need to add fictive start rule!
        self.start_rule = Rule('&', grammar.start_symbol)
        self.grammar = grammar
        self.grammar.AddStartRule(self.start_rule)

    def complete(self, j):
        self.Dj_changes = False
        D_j_new = defaultdict(list)

        while not self.delta_Dj.empty():
            situation = self.delta_Dj.get()
            for upper_situation in self.D_j[situation.i][situation.rule.lhs]:
                new_situation = situation.CompleteAndGoUpper(upper_situation)
                if self.add_situation(new_situation):
                    self.Dj_changes = True
                    next_symbol = new_situation.GetSymbolAfterDot()
                    if next_symbol == "$":
                        if new_situation.i == j:
                            self.Dj_j_dollar.append(new_situation)
                        self.delta_Dj.put(new_situation)
                    D_j_new[next_symbol].append(new_situation)

        Dj_j_dollar_new = list()
        for situation in self.Dj_j_dollar:
            for upper_situation in self.D_j[situation.i][situation.rule.lhs]:
                new_situation = situation.CompleteAndGoUpper(upper_situation)
                if self.add_situation(new_situation):
                    self.Dj_changes = True
                    next_symbol = new_situation.GetSymbolAfterDot()
                    if new_situation.i == j and next_symbol == "$":
                        Dj_j_dollar_new.append(new_situation)
                    if next_symbol == "$":
                        self.delta_Dj.put(new_situation)

                    D_j_new[next_symbol].append(new_situation)

        for next_symbol in D_j_new:
            for new_situation in D_j_new[next_symbol]:
                self.D_j[j][next_symbol].append(new_situation)

        for new_dj_j_dollar in Dj_j_dollar_new:
            self.Dj_j_dollar.append(new_dj_j_dollar)

    def predict_rule(self, j):
        D_j_new = defaultdict(list)

        for next_symbol in self.D_j[j]:
            for situation in self.D_j[j][next_symbol]:
                for rule_rhs in self.grammar.rules[next_symbol]:
                    new_situation = situation.PredictRule(
                        Rule(next_symbol, rule_rhs))
                    new_next_symbol = new_situation.GetSymbolAfterDot()
                    if self.add_situation(new_situation):
                        self.Dj_changes = True
                        if new_next_symbol == "$":
                            if new_situation.i == j:
                                self.Dj_j_dollar.append(new_situation)
                            self.delta_Dj.put(new_situation)

                        D_j_new[new_next_symbol].append(new_situation)

        for next_symbol in D_j_new:
            for new_situation in D_j_new[next_symbol]:
                self.D_j[j][next_symbol].append(new_situation)

    def scan(self, j, symbol):
        self.Dj_enterence = defaultdict(bool)
        self.Dj_changes = True
        self.delta_Dj = queue.Queue()
        self.Dj_j_dollar = list()

        for situation in self.D_j[j - 1][symbol]:
            new_situation = situation.ScanSymbol()
            new_next_symbol = new_situation.GetSymbolAfterDot()

            if (self.add_situation(new_situation)):
                if new_next_symbol == "$":
                    self.delta_Dj.put(new_situation)

                self.D_j[j][new_next_symbol].append(new_situation)

    def predict(self, string) -> bool:
        self.string = string
        self.D_j = [defaultdict(list)
                    for i in range(0, len(string) + 1)]
        self.early_algo(string)
        for situation in self.D_j[len(string)]['$']:
            if situation.i == 0 and situation.rule.lhs == '&' and situation.rule.rhs == 'S':
                return True
        return False

    def add_situation(self, situation) -> bool:
        if not self.Dj_enterence[situation]:
            self.Dj_enterence[situation] = True
            return True
        else:
            return False

    def early_algo(self, string):
        self.D_j[0][self.start_rule.rhs].append(
            Situation(self.start_rule, 0, 0, 0))

        # Dj_enetence shows that some situations already saws
        self.Dj_enterence = defaultdict(bool)
        self.Dj_enterence[Situation(self.start_rule, 0, 0, 0)] = True
        self.Dj_changes = True
        self.delta_Dj = queue.Queue()
        self.Dj_j_dollar = list()

        while self.Dj_changes:
            self.complete(0)
            self.predict_rule(0)

        for j in range(1, len(string) + 1):
            self.scan(j, string[j - 1])
            while self.Dj_changes:
                self.complete(j)
                self.predict_rule(j)
