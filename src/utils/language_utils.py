import math
import random
import numpy as np
from utils.utils import list_powerset_, powerset


def possible_imp_generator(language: list) -> frozenset:
    """
    Generate the set of all possible implications for a given enumerated language.
    Any set of premises with any conclusion is a potential implication.

    Parameters
    ----------
    language : list
        A list of strings, each string is a sentence.
        e.g. ['a_0', 'a_1', 'a_2'] or ['red', 'Bob is nice', 'Yao is cool']

    Returns
    -------
    frozenset
        frozenset set of implications, each implication is a tuple, whose first element is a frozenset of integers and
        second element an integer
    """
    result = []
    lst = [i for i in range(len(language))]
    for i in list_powerset_(lst):
        for j in range(len(language)):
            result.append((frozenset(i), j))
    return frozenset(result)


def possible_non_co_imp_generator(language: list) -> frozenset:
    return possible_imp_generator(language = language) - co_generator(language = language)


def possible_inc_generator(language: list) -> frozenset:
    """
    Generates all possible incoherence for a given language, namely all subsets of the language of size 2 or higher

    Parameters
    ----------
    language : list
        A list of strings, each string is a sentence.
        e.g. ['a_0', 'a_1', 'a_2'] or ['red', 'Bob is nice', 'Yao is cool']

    Returns
    -------
    frozenset
        a frozenset set of sets of integers. It contains all subsets of the (indexes of the) enumerated language, except
        all singletons, since we assume singletons are always coherent.
    """
    lst = [i for i in range(len(language))]
    result = list_powerset_(lst) - frozenset([frozenset([i]) for i in lst])
    return result


def co_generator(language: list) -> frozenset:
    # This function generates the list of implications required by CO for any atomic language
    result = []
    lst = [i for i in range(len(language))]
    for i in list_powerset_(lst):
        for j in i:
            result.append((frozenset(i), j))
    return frozenset(result)


def co_checker(language: list, imp: frozenset):
    # This takes a set of implications and checks if that set satisfies CO in a given language
    return co_generator(language).issubset(imp)


def co_closure(language: list, imp: frozenset) -> frozenset:
    return frozenset.union(imp, co_generator(language))


def random_imp(language: list, chance = 0.5, size = 'random') -> frozenset:
    """
    Generate a random set of implications of a given enumberated langauge by sampling from the set of all possible
    implications for a given enumerated language.
    It first generates the size of the resulting imp, k, by generating a integer in [0, #all possible imp] following binomial
    distribution, then sampling k elements in all possible implications without replacement.

    Parameters
    ----------
    language : list
        A list of strings, each string is a sentence.
        e.g. ['a_0', 'a_1', 'a_2'] or ['red', 'Bob is nice', 'Yao is cool']

    Returns
    -------
    frozenset
        frozenset set of some implications, each implication is a tuple, whose first element is a frozenset of integers and
        second element an integer
    """
    if size != 'random':
        return frozenset.union(frozenset(random.sample(possible_non_co_imp_generator(language), size)), co_generator(language))
    else:
        k = np.random.binomial(len(possible_non_co_imp_generator(language)), chance)
        return frozenset.union(frozenset(random.sample(possible_non_co_imp_generator(language), k)), co_generator(language))


def random_imp_co(language: list, size = 'random', chance = 0.5) -> frozenset:
    return co_closure(language, random_imp(language = language, chance = chance, size = size))


def random_inc(language: list, size = 'random', chance = 0.5) -> frozenset:
    """
    This generates a random set of sets of integers, to be interpreted as the set of all incoherent sets of sentences
    in some MSF.
    Note every single sentence is always coherent and the entire language is always incoherent.
    Like generating random implications, we first generate the size of the return set following a binomial distribution
    and then generate the return by sampling from all possible incoherent sets.

    Parameters
    ----------
    language : list
        A list of strings, each string is a sentence.
        e.g. ['a_0', 'a_1', 'a_2'] or ['red', 'Bob is nice', 'Yao is cool']

    Returns
    -------
    frozenset
        A set of sets. Each set in it is a set of indexes of sentences that are jointly incoherent.
        Every single sentence is always coherent and hence is never in the output set.
        The entire language is always incoherent and hence is always in the output set.
    """
    lst = [i for i in range(len(language))]

    if size != 'random':
        result = frozenset(random.sample(possible_inc_generator(language) - frozenset([frozenset(lst)]), size - 1))
        return frozenset.union(result, frozenset([frozenset(lst)]))
    else:
        k = np.random.binomial(len(possible_inc_generator(language)), chance)
        result = frozenset(random.sample(possible_inc_generator(language), k))
        return frozenset.union(result, frozenset([frozenset(lst)]))


def exff_sets(language: list, inc: frozenset) -> frozenset:
    exff_sets = []
    for gamma in inc:
        if math.pow(2, (len(language) - len(gamma))) <= len(inc):
            n = 0
            for delta in inc:
                if gamma.issubset(delta):
                    n = n + 1
            if n >= math.pow(2, (len(language) - len(gamma))):
                exff_sets.append(gamma)
    return frozenset(exff_sets)


def exff_closure(language: list, imp: frozenset, inc: frozenset) -> frozenset:
    return frozenset.union(imp, exff_generator(language, inc))


def exff_generator(language: list, inc: frozenset) -> frozenset:
    # This generates the list of implications required by exff given a list of implications (imp) and a list of
    # incoherences (inc).
    # One may have the concern that adding this generated set to an imp doesn't always make that set closed
    # under exff. Perhaps, more requirements can be generated in the process of adding. That is not the case.
    # The process of adding doesn't change inc. It only changes imp. So adding this generated set to a given imp,
    # does make that imp closed under exff relative to a inc.
    exff_sets = []
    result = []
    for gamma in inc:
        if math.pow(2, (len(language) - len(gamma))) <= len(inc):
            n = 0
            for delta in inc:
                if gamma.issubset(delta):
                    n = n + 1
            if n >= math.pow(2, (len(language) - len(gamma))):
                exff_sets.append(gamma)

    for gamma in exff_sets:
        for i in range(len(language)):
            result.append((gamma, i))
    return frozenset(result)


def exff_checker(language: list, imp: frozenset, inc: frozenset):
    # This function checks if a given a set of implications satisfy exff for a given set of incoherence in a given
    # language.
    return exff_generator(language, inc).issubset(imp)


def all_imp_co_exff(language: list, inc: frozenset) -> frozenset:
    # This function general all implications that satisfy CO and exff (given a inc) in a given langauge.
    # Actually running it will almost certainly give us a memory error.
    result = []
    m = powerset(
        possible_imp_generator(language) - frozenset.union(co_generator(language), exff_generator(language, inc)))
    for x in m:
        result.append(frozenset.union(m, frozenset.union(co_generator(language), exff_generator(language, inc))))
    return frozenset(result)


def random_imp_co_exff(language: list, inc: frozenset, imp_size = 'random', imp_chance = 0.5) -> frozenset:
    return exff_closure(language, random_imp_co(language = language, size = imp_size, chance = imp_chance), inc)


def random_imp_co_exff_with_random_inc(language: list) -> frozenset:
    # The current method used to generate a random imp is by first randomly sampling from all possible imps
    # and then add all ones required by CO and exff (and potentially other further requirements) to the sample.
    # An alternative way to do so is to first put in all required ones and then sample from the non-required ones.
    # I now think these two ways are equivalent. It's as if you are generating a binary number of the length of all
    # possible implications relations. Suppose that there are 60 possible ones in total and 36 of them are required.
    # It's as if you are generating a binary number of 60 digits and (say) the first 36 of them (on the left) are set
    # to be 1 by fiat. It doesn't matter for the later 24 digits whether you are only generating the later 24 digits
    # and then add 36 1's in front of them or you generate 60 digits and make the first 36 of them 1.
    # Another question is whether the current procedure I use to generate these digits are faithful. What I do now is
    # first generate how many ones are there and then pick where the ones are at. I think it works well.
    return exff_closure(language, random_imp_co(language), random_inc(language))


def ss_meaning(msf, imp, valence = 'for'):
    # This is an implementation of Dan Kaplan's vee-function in his semantics for single succedent.
    # Note: when we calculate the vee-function, we consider all reasons, including the ones that are not pragmatically significant.
    # input msf is the msf we are operating in.
    # input 'imp' should be a list of implications. For example, it can be [([2,3,4],1), ([1,3,4],5)]
    # or [([1,3,5], None), ([1,3,5], None)]. Formally, input 'imp' should be a list of tuples.
    # The first element of the tuple is a list of indexes for sentences, the second element is either a number (index)
    # or None. By making the consequent None, you effectively leave it empty.
    # valence specifies whether we are trying to apply vee-function to reason-for or reason-against. It must either be 'for'
    # or 'against'.
    c = imp[0][1]    # We first find out what the consequent of the implications are.
                        # For the single-succedent system, all implications of the input set must have the same consequent.
    result = []
    finalresult = frozenset()
    display = ''
    if valence == 'for':
        if all([p[1] == c for p in imp]):    # Here we check if the succedent of all reasons in the input set are the same.
            if c is None:
                for p in imp:
                    count = []
                    for i in msf.imp:
                        if frozenset(p[0]).issubset(i[0]):
                            count.append((i[0] - frozenset(p[0]), i[1]))
                    result.append(frozenset(count))
                finalresult = frozenset.intersection(*result)
                for i in finalresult:
                    display = display + str(list(i[0])) + '⊨' + str(i[1]) + ', '
                print('Applying the vee-function to', imp, 'as reasons-for gives the following set of (prima-facie) implications:')
                print('{' + display[:-2] + '}')
                return finalresult
            else:
                for p in imp:
                    count = []
                    for i in msf.imp:
                        if i[1] == c:
                            if frozenset(p[0]).issubset(i[0]):
                                count.append((i[0] - frozenset(p[0]), None))
                    result.append(frozenset(count))
                finalresult = frozenset.intersection(*result)
                for i in finalresult:
                    display = display + str(list(i[0])) + '⊨' + str(i[1]) + ', '
                print('Applying the vee-function to', imp, 'as reasons-for gives the following set of (prima-facie) implications:')
                print('{' + display[:-2] + '}')
                return finalresult

        else:
            print('For single succedent sysmtems, the second elements of ordered pairs in the input list must all be uniform'
                    'for the return to be none-empty.They can either all be None, or a particular sentence.')
    elif valence == 'against':
        if all([p[1] == c for p in imp]):    # Here we check if the succedent of all reasons in the input set are the same.
            if c is None:
                rawresult = []
                for p in imp:
                    count = []
                    for i in msf.inc:
                        if frozenset(p[0]).issubset(i):
                            count.append(i - frozenset(p[0]))
                    rawresult.append(frozenset(count))
                rawresult = frozenset.intersection(*rawresult)
                for i in rawresult:
                    for j in i:
                        result.append((i-frozenset([j]), j))
                for i in result:
                    display = display + str(list(i[0])) + '#' + str(i[1]) + ', '
                print('Applying the vee-function to', imp, 'as reasons-against gives the following set of (prima-facie) implications:')
                print('{' + display[:-2] + '}')
                return result
            else:
                for p in imp:
                    count = []
                    for i in msf.inc:
                        if frozenset.union(frozenset(p[0]), frozenset([p[1]])).issubset(i):
                            count.append((i - frozenset.union(frozenset(p[0]), frozenset([p[1]])), None))
                    result.append(frozenset(count))
                finalresult = frozenset.intersection(*result)
                for i in finalresult:
                    display = display + str(list(i[0])) + '#' + str(i[1]) + ', '
                print('Applying the vee-function to', imp, ' as reasons-against gives the following set of (prima-facie) implications:')
                print('{' + display[:-2] + '}')
                return finalresult
        else:
            print('For single succedent sysmtems, the second elements of ordered pairs in the input list must all be uniform'
                    'for the return to be none-empty.They can either all be None, or a particular sentence.')
    else:
        print('valence must be either \'for\' or \'against\'. If you do not specify, it is \'for\' by default. ')
        return frozenset()

