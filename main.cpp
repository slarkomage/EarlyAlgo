from early import Rule
from early import Grammar
from early import Early
from early import NotCFGGrammar

if __name__ == "__main__":
    sizes = input()
    nonterm_sz = int(sizes.split()[0])
    term_sz = int(sizes.split()[1])
    rules_sz = int(sizes.split()[2])

    nonterm_alphabet = input()
    nonterm_alphabet = list(nonterm_alphabet)
    term_alphabet = input()
    term_alphabet = list(term_alphabet)

    rules_list = []
    for i in range(0, rules_sz):
        rule_statement = input()
        rules_list.append(Rule(rule_statement))

    start_symbol = input()

    cfg = Grammar(term_alphabet, nonterm_alphabet, rules_list, start_symbol)
    if not cfg.CheckCFG():
        raise NotCFGGrammar("Grammar is not contex-free!")

    early_algo = Early()
    early_algo.fit(cfg)

    amount_strings = int(input())
    for i in range(0, amount_strings):
        string = input()
        if (early_algo.predict(string)):
            print("Yes")
        else:
            print("No")
