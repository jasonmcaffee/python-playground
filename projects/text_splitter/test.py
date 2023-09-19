import math
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

# broken into groups of 20 with overlap amount of 10
# I am the walrus that
#  lives in the
# basement and drives
# a blue car that
# everyone loves.
#
# I am the walrus that
# walrus that lives in
# lives
#
def break_into_groups_of_N_with_overlaps_of_Y(text, group_length, overlap_length):
    groups = []
    current_start_index = 0
    next_end_index_to_split_so_word_isnt_cut = find_index_word_split_before_max_length(text, end_index=group_length)
    # prevent unlikely scenario where word length is greater than group_length
    previous_next_end_index_to_split_so_word_isnt_cut = -1
    print(f"text length: {len(text)}")
    count = 0
    while(count < 10):
        print("=================================")
        count = count + 1

        group = text[current_start_index: next_end_index_to_split_so_word_isnt_cut]
        groups.append(group)
        print(f"current_start_index: {current_start_index} next_end_index_to_split_so_word_isnt_cut: {next_end_index_to_split_so_word_isnt_cut}")
        print(f"group:-{group}- length: {len(group)}")

        # if(next_end_index_to_split_so_word_isnt_cut + group_length < len(text)):
        #     next_end_index_to_split_so_word_isnt_cut = len(text)

        current_start_index = next_end_index_to_split_so_word_isnt_cut
        #current_start_index should now have half group_length added
        # current_start_index = math.floor(current_start_index + (group_length - overlap_length))
        # current_start_index = text.find(" ", current_start_index)
        # current_start_index = next_end_index_to_split_so_word_isnt_cut
        next_end_index_to_split_so_word_isnt_cut = find_index_word_split_before_max_length(text, start_index=current_start_index, end_index=current_start_index + group_length)

        #ensure last word is captured
        if(current_start_index == next_end_index_to_split_so_word_isnt_cut):
            next_end_index_to_split_so_word_isnt_cut = len(text)

        # overlap_end_index = find_index_word_split_before_max_length(text, next_end_index_to_split_so_word_isnt_cut, group_length + next_end_index_to_split_so_word_isnt_cut,)
        # print(f"overlap_end_index: {overlap_end_index}")
        # print(f"next_end_index_to_split_so_word_isnt_cut: {next_end_index_to_split_so_word_isnt_cut}")
        # overlap_group = text[next_end_index_to_split_so_word_isnt_cut: overlap_end_index ]
        # print(f"overlap group:-{overlap_group}-")

        # return
    return groups


def find_index_word_split_before_max_length(text, start_index = 0, end_index=0):
    """
    text: I am the walrus that lives in the basement and drives a blue car that everyone loves.
    max_length: 7
    results in: 4
    """
    index = text.rfind(" ", start_index, end_index + 1) # +1
    #include the " "
    # if index < end_index:
    #     index += 1
    # print(f"index is {index}")
    # print(f"word after index:-{text[index: len(text)]}-")
    # print(f"word before index:-{text[0: index]}-")
    return index

# 1 token == 4 characters
def easy_grouping(text, group_token_length):
    """Note: These must be joined back together with ' '.join(groups) """
    groups = []
    current_group = []
    current_group_token_count = 0
    words = text.split(" ")
    while len(words) > 0:
        word = words[0]
        current_word_token_count = calculate_tokens_for_word(word + " ")
        if(current_group_token_count + current_word_token_count <= group_token_length):
            words.pop(0)
            current_group.append(word)
            current_group_token_count += current_word_token_count
            #if the we are out of words and less than the group_token_length, we need to get out.
            if(len(words)) == 0:
                current_group_text = " ".join(current_group)
                groups.append(current_group_text)
        else:
            current_group_text = " ".join(current_group)
            groups.append(current_group_text)
            current_group = []
            current_group_token_count = 0
    return groups

def calculate_tokens_for_word(word):
    return math.ceil(len(word) / 4)

if __name__ == "__main__":
    text = " I am the walrus that lives in the basement and drives a blue car that everyone loves. "
    groups = easy_grouping(text, 10)
    print(groups)
    final = " ".join(groups)
    print(final == text)
    # groups = text.split(" ")
    # print(groups)
    # result = " ".join(groups)
    # print(result)
    # print(result == text)
    # find_index_word_split_before_max_length(text, end_index=2)
    # start_text, end_text = split_string_at_nearest_space("I am the walrus that lives in the basement", 2)
    # print(f"result: {start_text},{end_text}")
    #main()
    # groups = break_into_groups_of_N_with_overlaps_of_Y(text, 40, 0)
    # print(f"groups are {groups}")
    # sub = text[0:5]
    # sub = sub[2:3]
    # print(sub)
    # print("I"[1])
