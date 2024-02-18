from itertools import zip_longest


class TextSplitter:
    @staticmethod
    def split_text_into_lines_of_length_and_create_overlapping_lines_of_text(text_to_split, max_line_length,
                                                                             line_overlap_length):
        """
        Main function to split the text into lines that don't exceed the max_line_length.
        Then overlapping lines are created so that part of the previous line is included
        e.g.
        The brown fox jumped over the
        jumped over the blue moon on
        blue moon on its way to the
        its way to the fairy store.
        fairy store. The blue cow ran
        The blue cow ran into a car
        """
        lines = TextSplitter.split_text_into_lines_of_length(text_to_split, max_line_length)
        overlapping_lines = TextSplitter.create_overlapping_lines(text_to_split, line_overlap_length, max_line_length)
        print(f"lines: {len(lines)} overlapping: {len(overlapping_lines)}")
        merged_lines = [item for pair in zip_longest(lines, overlapping_lines, fillvalue=None) for item in pair if
                        item is not None]
        # zipped = zip_longest(lines, overlapping_lines, fillvalue=None)
        # merged_lines = []
        # for pair in zipped:
        #     for item in pair:
        #         if item is not None:
        #             merged_lines.append(item)
        return merged_lines

    @staticmethod
    def split_text_into_lines_of_length(text_to_split: str, max_line_length=15):
        """
        Split the text into lines that do not exceed max_line_length.
        Only split on " ", in order to not split words in half.
        """
        remaining_text = text_to_split
        lines = []
        while len(remaining_text) > 0:
            end_index = TextSplitter.get_nearest_index_that_doesnt_break_a_word(remaining_text, max_line_length)
            line = remaining_text[0: end_index]
            lines.append(line)
            remaining_text = remaining_text[end_index:]
        return lines

    @staticmethod
    def get_nearest_index_that_doesnt_break_a_word(text: str, index: int):
        """
        Attempts to work backwards from the index and finds the earliest index possible to start on that doesn't break a word.
        If there are no suitable earlier indexes, will return the end of the current text.
        """
        # don't bother trying if the index is greater than the string length.
        if index > len(text):
            return len(text)

        # Ensure start_index is within the bounds of the text
        start_index = min(index, len(text) - 1)

        # walk backwards through the text until the nearest space is found.
        while start_index > 0 and text[start_index - 1] != " ":
            start_index -= 1

        # if no space was found when walking backwards, walk forwards until a space is found.
        if start_index == 0:
            start_index = min(index, len(text) - 1)
            while start_index < len(text) and text[start_index - 1] != " ":
                start_index += 1

        # start_index = start_index if start_index > 0 else len(text)
        return start_index

    @staticmethod
    def create_overlapping_lines(text_to_split, line_overlap_length=7, max_line_length=15):
        """
        It is useful in RAG to break the text up into chunks that overlap.  That way we are more likely to get a hit for the surrounding text
        e.g.
        The brown fox jumped over
        jumped over the blue moon
        blue moon on its way to
        """
        # to create overlapping text we can create a new substring that starts N chars into the original, and use our original splitting function
        # e.g. For "The brown fox jumped over the blue moon", we can start at "jumped over the blue moon on its way to"
        start_index = TextSplitter.get_nearest_index_that_doesnt_break_a_word(text_to_split, line_overlap_length)
        overlap_text_to_split = text_to_split[start_index:]
        overlapping_lines = TextSplitter.split_text_into_lines_of_length(overlap_text_to_split, max_line_length)
        return overlapping_lines

    @staticmethod
    def recombine_text(lines_and_overlapping_lines):
        """
        After we find multiple results in the db, we will want to recombine them together into a single piece of text that does not contain overlap.
        """

        def find_overlap(s1, s2):
            """Find the length of the longest suffix of s1 that is a prefix of s2."""
            for i in range(min(len(s1), len(s2)), 0, -1):
                if s1.endswith(s2[:i]):
                    return i
            return 0

        result = ""
        for s in lines_and_overlapping_lines:
            overlap_len = find_overlap(result, s)
            result += s[overlap_len:]

        return result
