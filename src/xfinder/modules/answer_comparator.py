import ast
from typing import List, Tuple, Union

from ..helpers import MathEvaluator


class Comparator:
    """
    Comparator class for comparing extracted answers with correct answers.

    Attributes:
        math_evaluator (MathEvaluator): An instance of MathEvaluator class.
    """

    def __init__(self):
        self.math_evaluator = MathEvaluator()

    def compare(
        self, ext_cor_pair: Tuple[str, Union[str, list], str, str]
    ) -> List[Union[str, int]]:
        """Compare the extracted answer with the correct answer. Return a list of the comparison result.

        Args:
            ext_cor_pair (Tuple[str, Union[str, list], str, str]): A tuple of the extracted answer, correct answer, and the key answer type.

        Returns:
            List[Union[str, int]]: A list of the comparison result.
        """
        right_flag = 0
        key_answer_type, standard_answer_range, extracted, correct = ext_cor_pair
        if key_answer_type == "math":
            if self.math_evaluator.is_equiv(extracted, correct) == True:
                right_flag = 1
        else:
            if extracted.strip().rstrip(".").lower() == correct.strip().rstrip(
                    ".").lower():
                right_flag = 1

            elif key_answer_type == "alphabet_option":
                if type(standard_answer_range) == str:
                    standard_answer_range_list = ast.literal_eval(
                        standard_answer_range)
                else:  
                    standard_answer_range_list = standard_answer_range
                for option in standard_answer_range_list:
                    if option[0] == correct and \
                            extracted.strip().rstrip(".").lower() == option[1].strip().rstrip(".").lower():
                        right_flag = 1
                        break

        return [*ext_cor_pair, right_flag]
