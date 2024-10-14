import re


def normalize_final_answer(final_answer: str) -> str:
    """Normalize a final answer to a quantitative reasoning question.
    
    Args:
        final_answer (str): The final answer to normalize.
    
    Returns:
        str: The normalized final answer.
    """
    # final_answer = final_answer.split('=')[-1]
    SUBSTITUTIONS = [('an ', ''), ('a ', ''), ('.$', '$'), ('\\$', ''),
                     (r'\ ', ''), (' ', ''), ('mbox', 'text'),
                     (',\\text{and}', ','), ('\\text{and}', ','),
                     ('\\text{m}', '\\text{}'), ('\\le', '<')]
    REMOVED_EXPRESSIONS = [
        'square', 'ways', 'integers', 'dollars', 'mph', 'inches', 'ft', 'hours',
        'km', 'units', '\\ldots', 'sue', 'points', 'feet', 'minutes', 'digits',
        'cents', 'degrees', 'cm', 'gm', 'pounds', 'meters', 'meals', 'edges',
        'students', 'childrentickets', 'multiples', '\\text{s}', '\\text{.}',
        '\\text{\ns}', '\\text{}^2', '\\text{}^3', '\\text{\n}', '\\text{}',
        r'\mathrm{th}', r'^\circ', r'^{\circ}', r'\;', r',\!', '{,}', '"',
        '\\dots', '\n', '\r', '\f'
    ]
    for before, after in SUBSTITUTIONS:
        final_answer = final_answer.replace(before, after)
    for expr in REMOVED_EXPRESSIONS:
        final_answer = final_answer.replace(expr, '')

    # Extract answer that is in LaTeX math, is bold,
    # is surrounded by a box, etc.
    final_answer = re.sub(r'(\\text\{)\((.*?)\)(\})', '\\2', final_answer)
    final_answer = re.sub(r'(\\text\{)(.*?)(\})', '\\2', final_answer)
    final_answer = re.sub(r'(\\textbf\{)(.*?)(\})', '\\2', final_answer)
    final_answer = re.sub(r'(\\overline\{)(.*?)(\})', '\\2', final_answer)
    final_answer = re.sub(r'(\\boxed\{)(.*)(\})', '\\2', final_answer)
    assert '\n' not in final_answer
    assert '\r' not in final_answer
    assert '\f' not in final_answer

    if len(re.findall(r'finalansweris(.*)', final_answer)) > 0:
        final_answer = re.findall(r'finalansweris(.*)', final_answer)[-1]

    if len(re.findall(r'answer?is:?(.*)', final_answer)) > 0:
        final_answer = re.findall(r'answer?is:?(.*)', final_answer)[-1]

    if len(re.findall(r'oxed\{(.*?)\}', final_answer)) > 0:
        final_answer = re.findall(r'oxed\{(.*?)\}', final_answer)[-1]

    if len(re.findall(r'\$(.*?)\$', final_answer)) > 0:
        final_answer = re.findall(r'\$(.*?)\$', final_answer)[-1]
    final_answer = final_answer.strip()
    if 'rac' in final_answer and '\\frac' not in final_answer:
        final_answer = final_answer.replace('rac', '\\frac')

    # Normalize shorthand TeX:
    # \fracab -> \frac{a}{b}
    # \frac{abc}{bef} -> \frac{abc}{bef}
    # \fracabc -> \frac{a}{b}c
    # \sqrta -> \sqrt{a}
    # \sqrtab -> sqrt{a}b
    final_answer = re.sub(r'(frac)([^{])(.)', 'frac{\\2}{\\3}', final_answer)
    final_answer = re.sub(r'(sqrt)([^{])', 'sqrt{\\2}', final_answer)
    final_answer = final_answer.replace('$', '')

    # Normalize 100,000 -> 100000
    if final_answer.replace(',', '').isdigit():
        final_answer = final_answer.replace(',', '')

    return final_answer


class MathEvaluator():

    def __init__(self, version='v2'):
        assert version in ['v1', 'v2']
        self.version = version

    def _fix_fracs(self, string):
        """Fixes fractions in the string.
        
        Args:
            string (str): The string to fix.
            
        Returns:
            str: The fixed string.
        """
        substrs = string.split('\\frac')
        new_str = substrs[0]
        if len(substrs) > 1:
            substrs = substrs[1:]
            for substr in substrs:
                new_str += '\\frac'
                if len(substr) > 0 and substr[0] == '{':
                    new_str += substr
                else:
                    try:
                        assert len(substr) >= 2
                    except AssertionError:
                        return string
                    a = substr[0]
                    b = substr[1]
                    if b != '{':
                        if len(substr) > 2:
                            post_substr = substr[2:]
                            new_str += '{' + a + '}{' + b + '}' + post_substr
                        else:
                            new_str += '{' + a + '}{' + b + '}'
                    else:
                        if len(substr) > 2:
                            post_substr = substr[2:]
                            new_str += '{' + a + '}' + b + post_substr
                        else:
                            new_str += '{' + a + '}' + b
        string = new_str
        return string

    def _fix_a_slash_b(self, string):
        """Fixes a/b to \frac{a}{b}.
        
        Args:
            string (str): The string to fix.
            
        Returns:
            str: The fixed string.
        """
        if len(string.split('/')) != 2:
            return string
        a = string.split('/')[0]
        b = string.split('/')[1]
        try:
            a = int(a)
            b = int(b)
            assert string == '{}/{}'.format(a, b)
            new_string = '\\frac{' + str(a) + '}{' + str(b) + '}'
            return new_string
        except AssertionError:
            return string

    def _remove_right_units(self, string):
        # "\\text{ " only ever occurs (at least in the val set) when describing
        # units
        if '\\text{ ' in string:
            splits = string.split('\\text{ ')
            assert len(splits) == 2
            return splits[0]
        else:
            return string

    def _fix_sqrt(self, string):
        if '\\sqrt' not in string:
            return string
        splits = string.split('\\sqrt')
        new_string = splits[0]
        for split in splits[1:]:
            if split[0] != '{':
                a = split[0]
                new_substr = '\\sqrt{' + a + '}' + split[1:]
            else:
                new_substr = '\\sqrt' + split
            new_string += new_substr
        return new_string

    def _fix_sqrt_v2(self, string):
        _string = re.sub(r'\\sqrt(\w+)', r'\\sqrt{\1}', string)
        return _string

    def _strip_string(self, string):
        """Strip a string of unnecessary characters.
        
        Args:
            string (str): The string to strip.
            
        Returns:
            str: The stripped string.
        """
        # linebreaks
        string = string.replace('\n', '')

        # remove inverse spaces
        string = string.replace('\\!', '')

        # replace \\ with \
        string = string.replace('\\\\', '\\')

        # replace tfrac and dfrac with frac
        string = string.replace('tfrac', 'frac')
        string = string.replace('dfrac', 'frac')

        # remove \left and \right
        string = string.replace('\\left', '')
        string = string.replace('\\right', '')

        # Remove circ (degrees)
        string = string.replace('^{\\circ}', '')
        string = string.replace('^\\circ', '')

        # remove dollar signs
        string = string.replace('\\$', '')

        # remove units (on the right)
        string = self._remove_right_units(string)

        # remove percentage
        string = string.replace('\\%', '')
        string = string.replace('\%', '')  # noqa: W605

        # " 0." equivalent to " ." and "{0." equivalent to "{." Alternatively,
        # add "0" if "." is the start of the string
        string = string.replace(' .', ' 0.')
        string = string.replace('{.', '{0.')
        # if empty, return empty string
        if len(string) == 0:
            return string
        if string[0] == '.':
            string = '0' + string

        # to consider: get rid of e.g. "k = " or "q = " at beginning
        if len(string.split('=')) == 2:
            if len(string.split('=')[0]) <= 2:
                string = string.split('=')[1]

        # fix sqrt3 --> sqrt{3}
        string = self._fix_sqrt(string)

        # remove spaces
        string = string.replace(' ', '')

        # \frac1b or \frac12 --> \frac{1}{b} and \frac{1}{2}, etc. Even works
        # with \frac1{72} (but not \frac{72}1). Also does a/b --> \\frac{a}{b}
        string = self._fix_fracs(string)

        # manually change 0.5 --> \frac{1}{2}
        if string == '0.5':
            string = '\\frac{1}{2}'

        # NOTE: X/Y changed to \frac{X}{Y} in dataset, but in simple cases fix
        # in case the model output is X/Y
        string = self._fix_a_slash_b(string)

        return string

    def _strip_string_v2(self, string):
        string = str(string).strip()
        # linebreaks
        string = string.replace('\n', '')

        # right "."
        string = string.rstrip('.')

        # remove inverse spaces
        string = string.replace('\\!', '')
        string = string.replace('\\ ', '')

        # replace \\ with \
        string = string.replace('\\\\', '\\')
        string = string.replace('\\\\', '\\')

        # replace tfrac and dfrac with frac
        string = string.replace('tfrac', 'frac')
        string = string.replace('dfrac', 'frac')

        # remove \left and \right
        string = string.replace('\\left', '')
        string = string.replace('\\right', '')

        # Remove unit: miles, dollars if after is not none
        _string = re.sub(r'\\text{.*?}$', '', string).strip()
        if _string != '' and _string != string:
            string = _string

        # Remove circ (degrees)
        string = string.replace('^{\\circ}', '')
        string = string.replace('^\\circ', '')

        # remove dollar signs
        string = string.replace('\\$', '')
        string = string.replace('$', '')

        string = string.replace('\\text', '')
        string = string.replace('x\\in', '')

        # remove percentage
        string = string.replace('\\%', '')
        string = string.replace('\%', '')  # noqa: W605
        string = string.replace('%', '')

        # " 0." equivalent to " ." and "{0." equivalent to "{." Alternatively,
        # add "0" if "." is the start of the string
        string = string.replace(' .', ' 0.')
        string = string.replace('{.', '{0.')

        # cdot
        string = string.replace('\\cdot', '')

        # inf
        string = string.replace('infinity', '\\infty')
        if '\\infty' not in string:
            string = string.replace('inf', '\\infty')
        string = string.replace('+\\inity', '\\infty')

        # and
        string = string.replace('and', '')
        string = string.replace('\\mathbf', '')

        # use regex to remove \mbox{...}
        string = re.sub(r'\\mbox{.*?}', '', string)

        # quote
        string.replace("'", '')
        string.replace('"', '')

        # i, j
        if 'j' in string and 'i' not in string:
            string = string.replace('j', 'i')

        # replace a.000b where b is not number or b is end, with ab, use regex
        string = re.sub(r'(\d+)\.0+([^\d])', r'\1\2', string)
        string = re.sub(r'(\d+)\.0+$', r'\1', string)

        # if empty, return empty string
        if len(string) == 0:
            return string
        if string[0] == '.':
            string = '0' + string

        # to consider: get rid of e.g. "k = " or "q = " at beginning
        if len(string.split('=')) == 2:
            if len(string.split('=')[0]) <= 2:
                string = string.split('=')[1]

        string = self._fix_sqrt_v2(string)
        string = string.replace(' ', '')

        # \frac1b or \frac12 --> \frac{1}{b} and \frac{1}{2}, etc.
        # Even works with \frac1{72} (but not \frac{72}1).
        # Also does a/b --> \\frac{a}{b}
        string = self._fix_fracs(string)

        # NOTE: X/Y changed to \frac{X}{Y} in dataset, but in simple
        # cases fix in case the model output is X/Y
        string = self._fix_a_slash_b(string)

        return string

    def is_equiv(self, str1, str2, verbose=False):
        """Check if two strings are equivalent.
        
        Args:
            str1 (str): The first string.
            str2 (str): The second string.
            verbose (bool): If True, print the stripped strings.
        
        Returns:
            bool: True if the strings are equivalent, False otherwise.
        """
        if str1 is None and str2 is None:
            print('WARNING: Both None')
            return True
        if str1 is None or str2 is None:
            return False

        if self.version == 'v1':
            strip_string_func = self._strip_string
        elif self.version == 'v2':
            strip_string_func = self._strip_string_v2
        else:
            raise NotImplementedError

        try:
            ss1 = strip_string_func(str1)
            ss2 = strip_string_func(str2)
            if verbose:
                print(ss1, ss2)
            if ss1 == ss2:
                return True
            ss1 = normalize_final_answer(ss1)
            ss2 = normalize_final_answer(ss2)
            if ss1 == ss2:
                return True
        except Exception:
            pass

        try:
            ss1 = normalize_final_answer(str1)
            ss2 = normalize_final_answer(str2)
            if ss1 == ss2:
                return True
        except Exception:
            pass

        # try:
        #     if is_equiv(str1, str2):
        #         return True
        # except Exception:
        #     pass

        # try:
        #     ss1 = normalize_final_answer(str1)
        #     ss2 = normalize_final_answer(str2)
        #     if is_equiv(ss1, ss2):
        #         return True
        # except Exception:
        #     pass

        return str1 == str2


if __name__ == '__main__':
    math_evaluator = MathEvaluator()
    print(math_evaluator.is_equiv("\\boxed{1005}", "1005"))
