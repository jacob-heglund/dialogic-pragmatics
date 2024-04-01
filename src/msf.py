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
    IMP : frozenset
        a set of implications, each implication is a tuple, whose first element is a frozenset of integers, for indexes
        of premises and second element an integer, for the index of the conclusions.
    INC : frozenset
        a set of incoherent sets. Each member of INC is a frozenset of integers. Each integer is an index for a
        sentence in the enumerated language.

    Attributes
    ----------
    L : list
        The enumerated language
    IMP : frozenset
        a set of implications, each implication is a tuple, whose first element is a frozenset of integers, for indexes
        of premises and second element an integer, for the index of the conclusions.
    INC : frozenset
        a set of incoherent sets. Each member of INC is a frozenset of integers. Each integer is an index for a
        sentence in the enumerated language.
    EXC : dict
        a dictionary of exclusions. If \Gamma is incoherent, then for any \gamma in \Gamma, \Gamma - \gamma excludes
        \gamma. This dictionary maps the index of each sentence in the language to the set of sets of indexes of sentences
        that exclude this sentence. E.g. EXC[2] = {{1},{3,4}}.
    ForMove : frozenset
        the set of all possible for moves in this MSF. each member of the set is an object of class MoveType with its
        Val == 'reason for'. They correspond one to one with members of IMP of this MSF.
    AgainstMove : frozenset
        the set of all possible against moves in this MSF. each member of the set is an object of class MoveType with
        its Val == 'reason against'. They correspond one to one with members of EXC of this MSF.
    StrangeImp:
        the set of all implications that are strange in the sense that although the set of premises is not persistently
        incoherent, the union of premises and its conclusion is persistently incoherently. We prohibit players from
        using such implications to make moves, as asserting such implications will immediately put the player in to a
        persistenlty incoherent set of commitment.
    Code : str
        the code of a MSF can be used to regenerate the same MSF using Decode_MSF function. it's a string of form
        'len' + n + 'imp' + m + 'inc' + s, where n is the length of language, m is the code for imp, s is the code for inc.

        """
    def __init__(self, L, IMP, INC): # documented under the class
        self.L = L  # Enumerated Language, as a list of sentences
        self.IMP = IMP  # Set of Implications
        self.INC = INC  # Set of Incompatibilities
        self.ExFF = ExFF_sets(self.L, self.INC)
        self.EXC = EXC_generator(L, INC)  # Set of Exclusions
        self.ForMove = PossibleForMoves(L, IMP, INC)
        self.AgainstMove = PossibleAgainstMoves(L, INC)
        self.StrangeImp = StrangeImp(self.L, self.IMP, self.INC)
        self.Code = Code_MSF(self.L, self.IMP, self.INC)
        self.NumberOfReasons = num_reason_calculator(language = self.L, for_moves = self.ForMove, against_moves = self.AgainstMove)
        # self.ReasonRatio = reason_ratio_calculator(language = self.L, for_moves= self.ForMove, against_moves = self.AgainstMove)
        self.MoveDict = move_dict_generator(self)

    def show(self):
        """
        This method prints out the MSF in a redundant and ugly way but is hopefully minimally usable for those who want
        to see what's in the MSF
        """
        print(
            "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^Beginning of a MSF display^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print('You can retrieve this MSF using the Decode_MSF function with the following code:')
        print(self.Code)

        # First calculate pragmatically significant implications.
        imp = list()
        for i in self.ForMove:
            imp.append(str(set(i.Prem)) + '⊨' + str(i.Conc))
        imp.sort()

        # Calculate how many implications are required by ExFF. The number doesn't include those required by both ExFF
        # and CO. If an implication is required by both ExFF and CO, we consider it required by CO.
        exff_co_overlap = 0
        for i in self.ExFF:
            exff_co_overlap = exff_co_overlap + len(i)
        num_exff_required = len(self.ExFF)*len(self.L) - exff_co_overlap

        # Calculate strange implications.
        strange = list()
        for i in self.StrangeImp:
            strange.append(str(set(i[0])) + '⊨' + str(i[1]))
        strange.sort()

        print('This MSF contains in total', len(self.IMP), 'implications, among which', len(imp), 'are pragmatically',
              'significant,', len(CO_generator(self.L)), 'are required by CO,', num_exff_required, 'are required by ExFF',
              'and', len(strange), 'are strange in the sense that the premises and the conclusion are jointly persistently incoherent.')
        print('(Note that if an implication is required both by CO and ExFF, it\'s considered to be required by CO but not ExFF.)')
        print('This MSF contains', len(self.ForMove), 'pragmatically significant reasons-for with the following distribution:', self.NumberOfReasons['for'], '.')
        print('This MSF contains', len(self.AgainstMove), 'pragmatically significant reasons-against with the following distribution:', self.NumberOfReasons['against'], '.')
        print('The Reason Ratio, #reasons-for over #reasons-against, for sentences in this MSF, is as follows:', self.ReasonRatio)
        print('This MSF contains', len(self.INC), 'incoherent sets, among which', len(self.ExFF), 'are persistently incoherent.')
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")


        print('This MSF contains the following',len(imp) ,'pragmatically significant implications, i.e. implications that',
              'are not required by CO or ExFF and are not strange.')
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
        for i in range(len(self.L)):
            f = list()
            for j in self.ForMove:
                if j.Conc == i:
                    f.append(str(set(j.Prem)))
            f.sort()
            print(i, 'has the following', len(f), 'pragmatically significant reasons for it:')
            print(wrap_list(f, 5))
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

        # Print out incoherent sets.
        inc = list()
        for i in self.INC:
            inc.append(str(set(i)))
        inc.sort()
        print('This MSF contains the following', len(inc), 'incoherent sets:')
        print(wrap_list(inc, 5))
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

        # Print out persistently incoherent sets.
        pinc = list()
        for i in ExFF_sets(self.L, self.INC):
            pinc.append(str(set(i)))
        pinc.sort()
        print('Among all incoherent sets, the following', len(pinc),' are persistently incoherent:')
        print(pinc)
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

        # Print out reason againsts.
        print('Thus, this MSF contains the following reasons against:')
        print(
            "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        for i in self.EXC:
            c = list()
            for j in self.EXC[i]:
                c.append(str(set(j)))
            c.sort()
            print(i, 'has the following', len(c) ,'reasons against it:')
            print(wrap_list(c, 5))
            print(
                "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

        print('The universe of reasons generated by this MSF contains the following', len(self.ForMove),' (pragmatically significant) reasons-for:')
        reasons_for = list()
        for i in self.ForMove:
            reasons_for.append(str(set(i.Prem)) + '⊨' + str(i.Conc))
        reasons_for.sort()
        print(wrap_list(reasons_for, items_per_line=5))

        print('The universe of reasons generated by this MSF contains the following', len(self.AgainstMove),' (pragmatically significant) reasons-against:')
        reasons_against = list()
        for i in self.AgainstMove:
            reasons_against.append(str(set(i.Prem)) + '#' + str(i.Conc))
        reasons_against.sort()
        print(wrap_list(reasons_against, items_per_line=5))


        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^End of a MSF display^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")


def move_dict_generator(msf): # keep a map from text representations of moves to the actual MoveType objects
    move_dict = dict()
    for move in msf.ForMove:
        move_dict[move.to_text] = move
    for move in msf.AgainstMove:
        move_dict[move.to_text] = move
    return move_dict


def num_reason_calculator(language, for_moves, against_moves):
    num_reason_for = [0]*len(language)
    num_reason_against = [0]*len(language)
    for i in for_moves:
        num_reason_for[i.Conc] = num_reason_for[i.Conc] + 1
    for i in against_moves:
        num_reason_against[i.Conc] = num_reason_against[i.Conc] + 1
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
    ## I think it would have been included in dp_common_funcs, but Bob and his students apparently literally have no idea about any proper programming practices, so don't use git, and therefore that file is not included. Fuck, I hate this.

    pass


def reason_ratio_calculator(language, for_moves, against_moves):
    num_reason_for = [0]*len(language)
    num_reason_against = [0]*len(language)
    for i in for_moves:
        num_reason_for[i.Conc] = num_reason_for[i.Conc] + 1
    for i in against_moves:
        num_reason_against[i.Conc] = num_reason_against[i.Conc] + 1
    result = dict()
    for i in range(len(language)):
        result[i] = safe_divide_for_display(num_reason_for[i], num_reason_against[i])

    return result


def Possible_IMP_Generator(language: list) -> frozenset:
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
    result = list()
    lst = [i for i in range(len(language))]
    for i in list_powerset_(lst):
        for j in range(len(language)):
            result.append((frozenset(i), j))
    return frozenset(result)


def CO_generator(language: list) -> frozenset:
    # This function generates the list of implications required by CO for any atomic language
    result = list()
    lst = [i for i in range(len(language))]
    for i in list_powerset_(lst):
        for j in i:
            result.append((frozenset(i), j))
    return frozenset(result)


def CO_checker(language: list, imp: frozenset):
    # This takes a set of implications and checks if that set satisfies CO in a given language
    return CO_generator(language).issubset(imp)


def Possible_non_CO_IMP_Generator(language: list) -> frozenset:
    return Possible_IMP_Generator(language = language) - CO_generator(language = language)


def RandomIMP(language: list, chance = 1/2, size = 'random') -> frozenset:
    """
    Generate a random set of implications of a given enumberated langauge by sampling from the set of all possible
    implications for a given enumerated language.
    It first generates the size of the resulting IMP, k, by generating a integer in [0, #all possible IMP] following binomial
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
        return frozenset.union(frozenset(random.sample(Possible_non_CO_IMP_Generator(language), size)), CO_generator(language))
    else:
        k = np.random.binomial(len(Possible_non_CO_IMP_Generator(language)), chance)
        return frozenset.union(frozenset(random.sample(Possible_non_CO_IMP_Generator(language), k)), CO_generator(language))


def Possible_INC_Generator(language: list) -> frozenset:
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


def RandomINC(language: list, size = 'random', chance = 1/2) -> frozenset:
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
        result = frozenset(random.sample(Possible_INC_Generator(language) - frozenset([frozenset(lst)]), size - 1))
        return frozenset.union(result, frozenset([frozenset(lst)]))
    else:
        k = np.random.binomial(len(Possible_INC_Generator(language)), chance)
        result = frozenset(random.sample(Possible_INC_Generator(language), k))
        return frozenset.union(result, frozenset([frozenset(lst)]))


def ExFF_sets(language: list, inc: frozenset) -> frozenset:
    exff_sets = list()
    for gamma in inc:
        if math.pow(2, (len(language) - len(gamma))) <= len(inc):
            n = 0
            for delta in inc:
                if gamma.issubset(delta):
                    n = n + 1
            if n >= math.pow(2, (len(language) - len(gamma))):
                exff_sets.append(gamma)
    return frozenset(exff_sets)


def EXC_generator(lang: list, inc: frozenset) -> dict:
    """
    This generates a dictionary of exclusions for a language with a given INC. The return is completely decided by the
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
        that exclude this sentence. E.g. EXC[2] = {{1},{3,4}}; this means that there are two and only two incoherent
        sets that contain the sentence indexe by 2, namely {1,2} and {2,3,4}
    """
    exff = ExFF_sets(lang, inc)
    result = dict()
    for i in range(len(lang)):
        against = list()
        for n in inc:
            if i in n and n - frozenset([i]) not in exff and n - frozenset([i]) != set():
                against.append(n - frozenset([i]))
        result[i] = frozenset(against)
    return result


def StrangeImp(lang, imp, inc):
    # Some implications are weird in the sense that the premises and conclusion are jointly
    # persistently in concsistent. We don't allow agents to use such IMP in a for-move.
    strangeimp = list()
    for i in imp:
        if i[0] not in ExFF_sets(lang, inc):
            if frozenset.union(i[0], frozenset([i[1]])) in ExFF_sets(lang, inc):
                strangeimp.append(i)
    return frozenset(strangeimp)


def PossibleForMoves(lang: list, imp: frozenset, inc: frozenset):
    formove = list()
    strangeimp = list()#Some implications are weird in the sense that the premises and conclusion are jointly
                       #persistently in concsistent. We don't allow agents to use such IMP in a for-move.
    for i in imp:
        if frozenset.union(i[0], frozenset([i[1]])) in ExFF_sets(lang, inc):
            strangeimp.append(i)
    pool = imp - CO_generator(lang) - ExFF_generator(lang, inc) - frozenset(StrangeImp(lang, imp, inc))
    for i in pool:
        formove.append(MoveType(Prem = i[0], Val = 'reason for', Conc = i[1], MoveLabel = str(sorted({lang[i] for i in i[0]})) + ' entails ' + lang[i[1]]))
    return frozenset(formove)


def CO_closure(language: list, imp: frozenset) -> frozenset:
    return frozenset.union(imp, CO_generator(language))


def RandomIMP_CO(language: list, size = 'random', chance = 1/2) -> frozenset:
    return CO_closure(language, RandomIMP(language = language, chance = chance, size = size))


def Code_MSF(language, imp, inc):
    """
        This function generates a code for an MSF. It's intentionally made to asks for language, imp, inc as inputs,
        instead of asking for an MSF, to avoid circularity, as we use it in initializing the .Code attribute of MSF.

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
    for i in list(Possible_IMP_Generator(language)):
        if i in imp:
            imp_code = imp_code + '1'
        else:
            imp_code = imp_code + '0'
    for i in list(Possible_INC_Generator(language)):
        if i in inc:
            inc_code = inc_code + '1'
        else:
            inc_code = inc_code + '0'
    return 'len'+str(len(language))+'imp'+str(int(imp_code, 2))+'inc'+str(int(inc_code, 2))


def Decode_MSF(language, code):
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
        possible_imp = list(Possible_IMP_Generator(language))
        possible_inc = list(Possible_INC_Generator(language))
        imp = list()
        inc = list()
        imp_code = format(imp_code_int, '0' + str(len(possible_imp)) + 'b')
        inc_code = format(inc_code_int, '0' + str(len(possible_inc)) + 'b')
        for i in range(len(possible_imp)):
            if imp_code[i] == '1':
                imp.append(possible_imp[i])
        for i in range(len(possible_inc)):
            if inc_code[i] == '1':
                inc.append(possible_inc[i])
        return MSF(language, frozenset(imp), frozenset(inc))


def ExFF_generator(language: list, inc: frozenset) -> frozenset:
    # This generates the list of implications required by ExFF given a list of implications (IMP) and a list of
    # incoherences (INC).
    # One may have the concern that adding this generated set to an IMP doesn't always make that set closed
    # under ExFF. Perhaps, more requirements can be generated in the process of adding. That is not the case.
    # The process of adding doesn't change INC. It only changes IMP. So adding this generated set to a given IMP,
    # does make that IMP closed under ExFF relative to a INC.
    exff_sets = list()
    result = list()
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


def ExFF_checker(language: list, imp: frozenset, inc: frozenset):
    # This function checks if a given a set of implications satisfy ExFF for a given set of incoherence in a given
    # language.
    return ExFF_generator(language, inc).issubset(imp)


def ExFF_closure(language: list, imp: frozenset, inc: frozenset) -> frozenset:
    return frozenset.union(imp, ExFF_generator(language, inc))

def MSF_closure(language: list, imp: frozenset, inc: frozenset):
    return MSF(L=language, IMP=ExFF_closure(language = language, imp=CO_closure(language=language, imp=imp), inc=inc),
               INC=inc)


def RandomIMP_CO_ExFF(language: list, inc: frozenset, imp_size = 'random', imp_chance = 1/2) -> frozenset:
    return ExFF_closure(language, RandomIMP_CO(language = language, size = imp_size, chance = imp_chance), inc)


def RandomIMP_CO_ExFF_with_random_INC(language: list) -> frozenset:
    # The current method used to generate a random IMP is by first randomly sampling from all possible IMPs
    # and then add all ones required by CO and ExFF (and potentially other further requirements) to the sample.
    # An alternative way to do so is to first put in all required ones and then sample from the non-required ones.
    # I now think these two ways are equivalent. It's as if you are generating a binary number of the length of all
    # possible implications relations. Suppose that there are 60 possible ones in total and 36 of them are required.
    # It's as if you are generating a binary number of 60 digits and (say) the first 36 of them (on the left) are set
    # to be 1 by fiat. It doesn't matter for the later 24 digits whether you are only generating the later 24 digits
    # and then add 36 1's in front of them or you generate 60 digits and make the first 36 of them 1.
    # Another question is whether the current procedure I use to generate these digits are faithful. What I do now is
    # first generate how many ones are there and then pick where the ones are at. I think it works well.
    return ExFF_closure(language, RandomIMP_CO(language), RandomINC(language))


def all_IMP_CO_ExFF(language: list, inc: frozenset) -> frozenset:
    # This function general all implications that satisfy CO and ExFF (given a INC) in a given langauge.
    # Actually running it will almost certainly give us a memory error.
    result = list()
    m = powerset(
        Possible_IMP_Generator(language) - frozenset.union(CO_generator(language), ExFF_generator(language, inc)))
    for x in m:
        result.append(frozenset.union(m, frozenset.union(CO_generator(language), ExFF_generator(language, inc))))
    return frozenset(result)


def PossibleAgainstMoves(lang, inc):
    againstmove = list()
    exc = EXC_generator(lang, inc)
    for i in range(len(lang)):
        for s in exc[i]:
            againstmove.append(MoveType(s, 'reason against', i, str(sorted({lang[n] for n in s})) + ' excludes ' + lang[i]))
    return frozenset(againstmove)


def RandomMSF(language, imp_size = 'random', imp_chance = 1/2, inc_size = 'random', inc_chance = 1/2):
    """
    Generate a random msf according to parameters provided.

    Parameters
    ----------
    language : list
        A list of strings, each string is a sentence.
        e.g. ['a_0', 'a_1', 'a_2'] or ['red', 'Bob is nice', 'Yao is cool']
    imp_size : 'random' or int
        This parameter controls the size of IMP directly.
        However, the resulting IMP of the MSF may not be of the exact size spcified by this parameter.
        It's kinda tricky. The current way of generating IMP is that we first randomly draw from implications that are not
        required by CO. Then add all implications required by CO. Then add all implications required by ExFF.
        This parameter sets the number of implications to be drawn from all potential implications that are not required
        CO. However, the implications so drawn may overlap with implications required by ExFF. The size of IMP equals
        imp_size + #CO required implications + #ExFF required implications - size of the overlap between drawn non-CO
        implications and ExFF required implications.
        Also note that this parameter is always larger than the number of pragmatically significant implications. Pragmatically
        significant implications form a (in most cases, proposal) subset of all non-CO implications. As some non-CO implications
        are also not pragmatically significant, e.g. they can be strange or required by ExFF (though not CO).
        This complication makes this parameter not as sharp as one may expect, since it doesn't just set the size.
        It nevertheless controls the size of IMP roughly.
        One way to use this parameter is to first randomly generate some MSFs and see how many pragmatically significant
        implications those MSFs contain. Then set and tweak this parameter.
    imp_chance : int (0 to 1)
        the chance of any potential imp, i.e. a pair of a subset of the language and a sentence, being an actual
        imp. This parameter will only make a difference if imp_size is not 'random'.
    inc_size : 'random' or int
        This parameter sets the size of INC directly. It doesn't have any complication as imp_size does.
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
    inc = RandomINC(language = language, size = inc_size, chance = inc_chance)
    imp = RandomIMP_CO_ExFF(language = language, inc = inc, imp_size = imp_size, imp_chance = imp_chance)
    return MSF(language, imp, inc)


def SSMeaning(msf, object, valence = 'for'):
    # This is an implementation of Dan Kaplan's vee-function in his semantics for single succedent.
    # Note: when we calculate the vee-function, we consider all reasons, including the ones that are not pragmatically significant.
    # input msf is the msf we are operating in.
    # input 'object' should be a list of implications. For example, it can be [([2,3,4],1), ([1,3,4],5)]
    # or [([1,3,5], None), ([1,3,5], None)]. Formally, input 'object' should be a list of tuples.
    # The first element of the tuple is a list of indexes for sentences, the second element is either a number (index)
    # or None. By making the consequent None, you effectively leave it empty.
    # valence specifies whether we are trying to apply vee-function to reason-for or reason-against. It must either be 'for'
    # or 'against'.
    c = object[0][1]    # We first find out what the consequent of the implications are.
                        # For the single-succedent system, all implications of the input set must have the same consequent.
    result = list()
    finalresult = frozenset()
    display = ''
    if valence == 'for':
        if all([p[1] == c for p in object]):    # Here we check if the succedent of all reasons in the input set are the same.
            if c == None:
                for p in object:
                    count = list()
                    for i in msf.IMP:
                        if frozenset(p[0]).issubset(i[0]):
                            count.append((i[0] - frozenset(p[0]), i[1]))
                    result.append(frozenset(count))
                finalresult = frozenset.intersection(*result)
                for i in finalresult:
                    display = display + str(list(i[0])) + '⊨' + str(i[1]) + ', '
                print('Applying the vee-function to', object, 'as reasons-for gives the following set of (prima-facie) implications:')
                print('{' + display[:-2] + '}')
                return finalresult
            else:
                for p in object:
                    count = list()
                    for i in msf.IMP:
                        if i[1] == c:
                            if frozenset(p[0]).issubset(i[0]):
                                count.append((i[0] - frozenset(p[0]), None))
                    result.append(frozenset(count))
                finalresult = frozenset.intersection(*result)
                for i in finalresult:
                    display = display + str(list(i[0])) + '⊨' + str(i[1]) + ', '
                print('Applying the vee-function to', object, 'as reasons-for gives the following set of (prima-facie) implications:')
                print('{' + display[:-2] + '}')
                return finalresult

        else:
            print('For single succedent sysmtems, the second elements of ordered pairs in the input list must all be uniform'
                    'for the return to be none-empty.They can either all be None, or a particular sentence.')
    elif valence == 'against':
        if all([p[1] == c for p in object]):    # Here we check if the succedent of all reasons in the input set are the same.
            if c == None:
                rawresult = list()
                for p in object:
                    count = list()
                    for i in msf.INC:
                        if frozenset(p[0]).issubset(i):
                            count.append(i - frozenset(p[0]))
                    rawresult.append(frozenset(count))
                rawresult = frozenset.intersection(*rawresult)
                for i in rawresult:
                    for j in i:
                        result.append((i-frozenset([j]), j))
                for i in result:
                    display = display + str(list(i[0])) + '#' + str(i[1]) + ', '
                print('Applying the vee-function to', object, 'as reasons-against gives the following set of (prima-facie) implications:')
                print('{' + display[:-2] + '}')
                return result
            else:
                for p in object:
                    count = list()
                    for i in msf.INC:
                        if frozenset.union(frozenset(p[0]), frozenset([p[1]])).issubset(i):
                            count.append((i - frozenset.union(frozenset(p[0]), frozenset([p[1]])), None))
                    result.append(frozenset(count))
                finalresult = frozenset.intersection(*result)
                for i in finalresult:
                    display = display + str(list(i[0])) + '#' + str(i[1]) + ', '
                print('Applying the vee-function to', object, ' as reasons-against gives the following set of (prima-facie) implications:')
                print('{' + display[:-2] + '}')
                return finalresult
        else:
            print('For single succedent sysmtems, the second elements of ordered pairs in the input list must all be uniform'
                    'for the return to be none-empty.They can either all be None, or a particular sentence.')
    else:
        print('valence must be either \'for\' or \'against\'. If you do not specify, it is \'for\' by default. ')
        return frozenset()

