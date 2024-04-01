""" defines material semantic frame (MSF)
"""

import math
import random
import numpy as np
from move import MoveType
from utils import wrap_list, list_powerset_, powerset


class MSF:
    """
    A class used to represent a material semantic frame.
    It only records the premises, the conclusions, both as numbers, the valence (reason for or reason against)
    and the label of a move. Labels are of form: a_1, a_2, a_3 entails/excludes a_4.

    Parameters
    ----------
    L : list
        The enumerated language
    imp : frozenset
        a set of implications, each implication is a tuple, whose first element is a frozenset of integers, for indexes
        of premises and second element an integer, for the index of the conclusions.
    inc : frozenset
        a set of incoherent sets. Each member of inc is a frozenset of integers. Each integer is an index for a
        sentence in the enumerated language.

    Attributes
    ----------
    L : list
        The enumerated language
    imp : frozenset
        a set of implications, each implication is a tuple, whose first element is a frozenset of integers, for indexes
        of premises and second element an integer, for the index of the conclusions.
    inc : frozenset
        a set of incoherent sets. Each member of inc is a frozenset of integers. Each integer is an index for a
        sentence in the enumerated language.
    exc : dict
        a dictionary of exclusions. If \Gamma is incoherent, then for any \gamma in \Gamma, \Gamma - \gamma excludes
        \gamma. This dictionary maps the index of each sentence in the language to the set of sets of indexes of sentences
        that exclude this sentence. E.g. exc[2] = {{1},{3,4}}.
    for_move : frozenset
        the set of all possible for moves in this MSF. each member of the set is an object of class MoveType with its
        val == 'reason for'. They correspond one to one with members of imp of this MSF.
    against_move : frozenset
        the set of all possible against moves in this MSF. each member of the set is an object of class MoveType with
        its val == 'reason against'. They correspond one to one with members of exc of this MSF.
    strange_imp:
        the set of all implications that are strange in the sense that although the set of premises is not persistently
        incoherent, the union of premises and its conclusion is persistently incoherently. We prohibit players from
        using such implications to make moves, as asserting such implications will immediately put the player in to a
        persistenlty incoherent set of commitment.
    code : str
        the code of a MSF can be used to regenerate the same MSF using decode_msf function. it's a string of form
        'len' + n + 'imp' + m + 'inc' + s, where n is the length of language, m is the code for imp, s is the code for inc.

        """
    def __init__(self, lang, imp, inc): # documented under the class
        self.lang = lang  # Enumerated Language, as a list of sentences
        self.imp = imp  # Set of Implications
        self.inc = inc  # Set of Incompatibilities
        self.exff = exff_sets(self.lang, self.inc)
        self.exc = exc_generator(self.lang, inc)  # Set of Exclusions
        self.for_move = possible_for_moves(self.lang, imp, inc)
        self.against_move = possible_against_moves(self.lang, inc)
        self.strange_imp = strange_imp(self.lang, self.imp, self.inc)
        self.code = code_msf(self.lang, self.imp, self.inc)
        self.n_reasons = find_n_reasons(language = self.lang, for_moves = self.for_move, against_moves = self.against_move)
        # self.ReasonRatio = reason_ratio_calculator(language = self.lang, for_moves= self.for_move, against_moves = self.against_move)
        self.move_dict = move_dict_generator(self)

    def show(self):
        """
        This method prints out the MSF in a redundant and ugly way but is hopefully minimally usable for those who want
        to see what's in the MSF
        """
        print(
            "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^Beginning of a MSF display^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print('You can retrieve this MSF using the decode_msf function with the following code:')
        print(self.code)

        # First calculate pragmatically significant implications.
        imp = []
        for i in self.for_move:
            imp.append(str(set(i.prem)) + '⊨' + str(i.conc))
        imp.sort()

        # Calculate how many implications are required by exff. The number doesn't include those required by both exff
        # and CO. If an implication is required by both exff and CO, we consider it required by CO.
        exff_co_overlap = 0
        for i in self.exff:
            exff_co_overlap = exff_co_overlap + len(i)
        num_exff_required = len(self.exff)*len(self.lang) - exff_co_overlap

        # Calculate strange implications.
        strange = []
        for i in self.strange_imp:
            strange.append(str(set(i[0])) + '⊨' + str(i[1]))
        strange.sort()

        print('This MSF contains in total', len(self.imp), 'implications, among which', len(imp), 'are pragmatically',
              'significant,', len(co_generator(self.lang)), 'are required by CO,', num_exff_required, 'are required by exff',
              'and', len(strange), 'are strange in the sense that the premises and the conclusion are jointly persistently incoherent.')
        print('(Note that if an implication is required both by CO and exff, it\'s considered to be required by CO but not exff.)')
        print('This MSF contains', len(self.for_move), 'pragmatically significant reasons-for with the following distribution:', self.n_reasons['for'], '.')
        print('This MSF contains', len(self.against_move), 'pragmatically significant reasons-against with the following distribution:', self.n_reasons['against'], '.')
        print('The Reason Ratio, #reasons-for over #reasons-against, for sentences in this msf, is as follows:', self.ReasonRatio)
        print('This MSF contains', len(self.inc), 'incoherent sets, among which', len(self.exff), 'are persistently incoherent.')
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")


        print('This MSF contains the following',len(imp) ,'pragmatically significant implications, i.e. implications that',
              'are not required by CO or exff and are not strange.')
        print(wrap_list(imp, 5))
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

        print('This MSF contains the following', len(strange), 'implications',
              'that are strange in the sense that the premises and the conclusion are jointly persistently incoherent.',
              'We currently do not allow agents to use these implications as reason-fors.')
        print(wrap_list(strange, 5))
        print(
            "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

        # Then print out pragmatic significant reason fors.
        print('Thus, this MSF has the following pragmatically significant reason-fors:')
        print(
            "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        for i in range(len(self.lang)):
            f = []
            for j in self.for_move:
                if j.conc == i:
                    f.append(str(set(j.prem)))
            f.sort()
            print(i, 'has the following', len(f), 'pragmatically significant reasons for it:')
            print(wrap_list(f, 5))
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

        # Print out incoherent sets.
        inc = []
        for i in self.inc:
            inc.append(str(set(i)))
        inc.sort()
        print('This MSF contains the following', len(inc), 'incoherent sets:')
        print(wrap_list(inc, 5))
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

        # Print out persistently incoherent sets.
        pinc = []
        for i in exff_sets(self.lang, self.inc):
            pinc.append(str(set(i)))
        pinc.sort()
        print('Among all incoherent sets, the following', len(pinc),' are persistently incoherent:')
        print(pinc)
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

        # Print out reason againsts.
        print('Thus, this MSF contains the following reasons against:')
        print(
            "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        for i in self.exc:
            c = []
            for j in self.exc[i]:
                c.append(str(set(j)))
            c.sort()
            print(i, 'has the following', len(c) ,'reasons against it:')
            print(wrap_list(c, 5))
            print(
                "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

        print('The universe of reasons generated by this MSF contains the following', len(self.for_move),' (pragmatically significant) reasons-for:')
        reasons_for = []
        for i in self.for_move:
            reasons_for.append(str(set(i.prem)) + '⊨' + str(i.conc))
        reasons_for.sort()
        print(wrap_list(reasons_for, items_per_line=5))

        print('The universe of reasons generated by this MSF contains the following', len(self.against_move),' (pragmatically significant) reasons-against:')
        reasons_against = []
        for i in self.against_move:
            reasons_against.append(str(set(i.prem)) + '#' + str(i.conc))
        reasons_against.sort()
        print(wrap_list(reasons_against, items_per_line=5))


        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^End of a MSF display^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")


def move_dict_generator(msf): # keep a map from text representations of moves to the actual MoveType objects
    move_dict = dict()
    for move in msf.for_move:
        move_dict[move.to_text] = move
    for move in msf.against_move:
        move_dict[move.to_text] = move
    return move_dict


def find_n_reasons(language, for_moves, against_moves):
    num_reason_for = [0]*len(language)
    num_reason_against = [0]*len(language)
    for i in for_moves:
        num_reason_for[i.conc] = num_reason_for[i.conc] + 1
    for i in against_moves:
        num_reason_against[i.conc] = num_reason_against[i.conc] + 1
    dct_num_reason_for = dict()
    dct_num_reason_against = dict()
    for i in range(len(language)):
        dct_num_reason_for[i] = num_reason_for[i]
        dct_num_reason_against[i] = num_reason_against[i]
    result = dict()
    result['for'] = dct_num_reason_for
    result['against'] = dct_num_reason_against
    return result


def safe_divide_for_display(num_reason_for, num_reason_against):
    # NOTE I had to define this function since it was literally not included in the files.
    ## Luckily, this function is also not called at all during the execution of a dialogue, so it works fine.
    ## I think it would have been included in dp_common_funcs, but it wasn't included in the two files that were made available publicly.
    pass


def reason_ratio_calculator(language, for_moves, against_moves):
    num_reason_for = [0]*len(language)
    num_reason_against = [0]*len(language)
    for i in for_moves:
        num_reason_for[i.conc] = num_reason_for[i.conc] + 1
    for i in against_moves:
        num_reason_against[i.conc] = num_reason_against[i.conc] + 1
    result = dict()
    for i in range(len(language)):
        result[i] = safe_divide_for_display(num_reason_for[i], num_reason_against[i])

    return result


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


def possible_non_co_imp_generator(language: list) -> frozenset:
    return possible_imp_generator(language = language) - co_generator(language = language)


def random_imp(language: list, chance = 1/2, size = 'random') -> frozenset:
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


def random_inc(language: list, size = 'random', chance = 1/2) -> frozenset:
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


def exc_generator(lang: list, inc: frozenset) -> dict:
    """
    This generates a dictionary of exclusions for a language with a given inc. The return is completely decided by the
    input. However, this is no long simply a book-keeping. I have removed premises that are persistently incoherent
    from being counted as a reason against. Before, every persistently incoherent set will a reason against any sentence
    not in the set. By definition, adding anything into a persistently incoherent set doesn't make the new set coherent.
    However, if the CL happens to use such a persistently incoherent set as a reason against a sentence outside the set,
    CL will directly put himself into persistently incoherent position and the inquiry will end in two steps.
    After the fix, CL will never do that any more.

    Parameters
    ----------
    lang : list
        A list of strings, each string is a sentence.
        e.g. ['a_0', 'a_1', 'a_2'] or ['red', 'Bob is nice', 'Yao is cool']
    inc : frozenset
        A frozenset of frozensets of intgers
        each frozenset in it is a set of indexes of sentences of the language

    Returns
    -------
    dict
        a dictionary of exclusions. If \Gamma is incoherent, then for any \gamma in \Gamma, \Gamma - \gamma excludes
        \gamma. This dictionary maps the index of each sentence in the language to the set of sets of indexes of sentences
        that exclude this sentence. E.g. exc[2] = {{1},{3,4}}; this means that there are two and only two incoherent
        sets that contain the sentence indexe by 2, namely {1,2} and {2,3,4}
    """
    exff = exff_sets(lang, inc)
    result = dict()
    for i in range(len(lang)):
        against = []
        for n in inc:
            if i in n and n - frozenset([i]) not in exff and n - frozenset([i]) != set():
                against.append(n - frozenset([i]))
        result[i] = frozenset(against)
    return result


def strange_imp(lang, imp, inc):
    # Some implications are weird in the sense that the premises and conclusion are jointly
    # persistently in concsistent. We don't allow agents to use such imp in a for-move.
    strangeimp = []
    for i in imp:
        if i[0] not in exff_sets(lang, inc):
            if frozenset.union(i[0], frozenset([i[1]])) in exff_sets(lang, inc):
                strangeimp.append(i)
    return frozenset(strangeimp)


def possible_for_moves(lang: list, imp: frozenset, inc: frozenset):
    formove = []
    strangeimp = []#Some implications are weird in the sense that the premises and conclusion are jointly
                       #persistently in concsistent. We don't allow agents to use such imp in a for-move.
    for i in imp:
        if frozenset.union(i[0], frozenset([i[1]])) in exff_sets(lang, inc):
            strangeimp.append(i)
    pool = imp - co_generator(lang) - exff_generator(lang, inc) - frozenset(strange_imp(lang, imp, inc))
    for i in pool:
        formove.append(MoveType(prem = i[0], val = 'reason for', conc = i[1], move_label = str(sorted({lang[i] for i in i[0]})) + ' entails ' + lang[i[1]]))
    return frozenset(formove)


def co_closure(language: list, imp: frozenset) -> frozenset:
    return frozenset.union(imp, co_generator(language))


def random_imp_co(language: list, size = 'random', chance = 1/2) -> frozenset:
    return co_closure(language, random_imp(language = language, chance = chance, size = size))


def code_msf(language, imp, inc):
    """
        This function generates a code for an MSF. It's intentionally made to asks for language, imp, inc as inputs,
        instead of asking for an msf, to avoid circularity, as we use it in initializing the .code attribute of MSF.

        Parameters
        ----------
        language : list
            A list of strings, each string is a sentence. Namely, the enumerated language from which the original encoded MSF
            was generated and the new recovered MSF will be generated.
            e.g. ['a_0', 'a_1', 'a_2'] or ['red', 'Bob is nice', 'Yao is cool']
        imp : frozenset
            The frozenset of all implications of the original MSF.
        inc : frozenset
            The frozenset of all incoherent sets of the original MSF.

        Returns
        -------
        str
            The function returns a string of form 'len' + n + 'imp' + m + 'inc' + s, where n is the length of language,
            m is the code for imp, s is the code for inc.
        """

    imp_code = str()
    inc_code = str()
    for i in list(possible_imp_generator(language)):
        if i in imp:
            imp_code = imp_code + '1'
        else:
            imp_code = imp_code + '0'
    for i in list(possible_inc_generator(language)):
        if i in inc:
            inc_code = inc_code + '1'
        else:
            inc_code = inc_code + '0'
    return 'len'+str(len(language))+'imp'+str(int(imp_code, 2))+'inc'+str(int(inc_code, 2))


def decode_msf(language, code):
    """
    This function generates an MSF using a code for MSF.

    Parameters
    ----------
    language : list
        A list of strings, each string is a sentence. Namely, the enumerated language from which the original encoded MSF
        was generated and the new recovered MSF will be generated.
        e.g. ['a_0', 'a_1', 'a_2'] or ['red', 'Bob is nice', 'Yao is cool']
    code : str
        A str for coding an MSF.

    Returns
    -------
    MSF
        An MSF identical to the originally encoded MSF. Note that they are identical in the sense that all artributes of
        them are the same. But they typically do not have the same identity assigned by Python.
    """

    lang_len = int(code[3 : code.find('imp')])
    if lang_len != len(language):
        print('Error: This code only works for language with', lang_len, 'sentences.')
    else:
        inc_code_int = int(code[code.find('inc') + 3:])
        imp_code_int = int(code[code.find('imp') + 3: code.find('inc')])
        possible_imp = list(possible_imp_generator(language))
        possible_inc = list(possible_inc_generator(language))
        imp = []
        inc = []
        imp_code = format(imp_code_int, '0' + str(len(possible_imp)) + 'b')
        inc_code = format(inc_code_int, '0' + str(len(possible_inc)) + 'b')
        for i in range(len(possible_imp)):
            if imp_code[i] == '1':
                imp.append(possible_imp[i])
        for i in range(len(possible_inc)):
            if inc_code[i] == '1':
                inc.append(possible_inc[i])
        return MSF(language, frozenset(imp), frozenset(inc))


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


def exff_closure(language: list, imp: frozenset, inc: frozenset) -> frozenset:
    return frozenset.union(imp, exff_generator(language, inc))


def msf_closure(language: list, imp: frozenset, inc: frozenset):
    return MSF(lang=language, imp=exff_closure(language = language, imp=co_closure(language=language, imp=imp), inc=inc),
               inc=inc)


def random_imp_co_exff(language: list, inc: frozenset, imp_size = 'random', imp_chance = 1/2) -> frozenset:
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


def all_imp_co_exff(language: list, inc: frozenset) -> frozenset:
    # This function general all implications that satisfy CO and exff (given a inc) in a given langauge.
    # Actually running it will almost certainly give us a memory error.
    result = []
    m = powerset(
        possible_imp_generator(language) - frozenset.union(co_generator(language), exff_generator(language, inc)))
    for x in m:
        result.append(frozenset.union(m, frozenset.union(co_generator(language), exff_generator(language, inc))))
    return frozenset(result)


def possible_against_moves(lang, inc):
    againstmove = []
    exc = exc_generator(lang, inc)
    for i in range(len(lang)):
        for s in exc[i]:
            againstmove.append(MoveType(s, 'reason against', i, str(sorted({lang[n] for n in s})) + ' excludes ' + lang[i]))
    return frozenset(againstmove)


def random_msf(language, imp_size = 'random', imp_chance = 1/2, inc_size = 'random', inc_chance = 1/2):
    """
    Generate a random msf according to parameters provided.

    Parameters
    ----------
    language : list
        A list of strings, each string is a sentence.
        e.g. ['a_0', 'a_1', 'a_2'] or ['red', 'Bob is nice', 'Yao is cool']
    imp_size : 'random' or int
        This parameter controls the size of imp directly.
        However, the resulting imp of the MSF may not be of the exact size spcified by this parameter.
        It's kinda tricky. The current way of generating imp is that we first randomly draw from implications that are not
        required by CO. Then add all implications required by CO. Then add all implications required by exff.
        This parameter sets the number of implications to be drawn from all potential implications that are not required
        CO. However, the implications so drawn may overlap with implications required by exff. The size of imp equals
        imp_size + #CO required implications + #exff required implications - size of the overlap between drawn non-CO
        implications and exff required implications.
        Also note that this parameter is always larger than the number of pragmatically significant implications. Pragmatically
        significant implications form a (in most cases, proposal) subset of all non-CO implications. As some non-CO implications
        are also not pragmatically significant, e.g. they can be strange or required by exff (though not CO).
        This complication makes this parameter not as sharp as one may expect, since it doesn't just set the size.
        It nevertheless controls the size of imp roughly.
        One way to use this parameter is to first randomly generate some MSFs and see how many pragmatically significant
        implications those MSFs contain. Then set and tweak this parameter.
    imp_chance : int (0 to 1)
        the chance of any potential imp, i.e. a pair of a subset of the language and a sentence, being an actual
        imp. This parameter will only make a difference if imp_size is not 'random'.
    inc_size : 'random' or int
        This parameter sets the size of inc directly. It doesn't have any complication as imp_size does.
        Note, the entire language is always incoherent. If inc_size = 9, there will be eight proper subsets of the
        language get counted as incoherent, since the entire language is always incoherent.
    inc_chance : int (0 to 1)
        the chance of any non-singleton proper subset of the language being incoherent. This parameter will only make
        a difference if inc_size is 'random'.
    Returns
    -------
    frozenset
        a frozenset set of sets of integers. It contains all subsets of the (indexes of the) enumerated language, except
        all singletons, since we assume singletons are always coherent.
    """
    inc = random_inc(language = language, size = inc_size, chance = inc_chance)
    imp = random_imp_co_exff(language = language, inc = inc, imp_size = imp_size, imp_chance = imp_chance)
    return MSF(language, imp, inc)


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

