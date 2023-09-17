# get an overlap of text, but split only at spaces inbetween words.
# "hello I am jason and I am on an airplane"
# should become
# hello I am jason and
# and I am on an airplane
# where "and" is overlapped, and the amount of words should be configurable.
def main():
    text = "hello I am jason and I am on an airplane"
    print(f"text length: {len(text)}")
    max_length = 12
    index_to_split_so_word_isnt_cut = text.find(" ", max_length)
    print(f"index_to_split: {index_to_split_so_word_isnt_cut}")
    part_one = text[0:index_to_split_so_word_isnt_cut]
    part_two = text[index_to_split_so_word_isnt_cut:len(text)]
    print(f"1:-{part_one}-2:-{part_two}")
    print(f"part_one len: {len(part_one)}")
    print(f"part_two len: {len(part_two)}")

    # get the last N
    last_n = 8
    highest_index_to_split_so_word_isnt_cut = text.rfind(" ", 0, last_n)
    print(f"highest_index: {highest_index_to_split_so_word_isnt_cut}")
    print(text[highest_index_to_split_so_word_isnt_cut: len(text)])


# params:
# "I am the walrus that lives in the basement"
# 2
# should yield
# "I am the waltrus that lives in the ", "basement"
def split_string_at_nearest_space(string_to_split, end_position):
    end = len(string_to_split) - end_position
    highest_index_to_split_so_word_isnt_cut = string_to_split.rfind(" ", 0, end)
    print(f"highest_index: {highest_index_to_split_so_word_isnt_cut}")
    end_text = string_to_split[highest_index_to_split_so_word_isnt_cut: len(string_to_split)]
    print(f"end_text: {end_text}")
    start_text = string_to_split[0: highest_index_to_split_so_word_isnt_cut]
    return start_text, end_text


# I am the walrus that lives in the basement
# broken into groups of 3
# 1. I am the
# 2. walrus that lives
# 3. in the basement.


if __name__ == "__main__":
    start_text, end_text = split_string_at_nearest_space("I am the walrus that lives in the basement", 2)
    print(f"result: {start_text},{end_text}")
    # main()
