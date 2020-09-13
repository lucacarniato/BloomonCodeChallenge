from collections import Counter, OrderedDict
import argparse
import copy
import re
import sys


def get_content(input_file):
    """Parses the input_file

    Parameters:
    input_file (str): the input file. If empty ("") the standard input is used

    Returns:
    content (list): a list with all lines of the input file or standard input

   """

    content = []
    num_empty_lines = 0
    if input_file == "":
        # read from standard input
        for line in sys.stdin:
            line = line.strip()
            content.append(line)
            if not line:
                num_empty_lines += 1
            # break when two empty lines are found
            if num_empty_lines == 2:
                break
    else:
        # read from file
        with open(input_file) as f:
            for line in f:
                line = line.strip()
                content.append(line)
                if not line:
                    num_empty_lines += 1

    if len(content) <= num_empty_lines:
        return []
    else:
        return content

    return content


def parse_content(content):
    """Parses the content

    Parameters:
    content (list): a list with all lines of the input file or standard input

    Returns:
    large_bouquets_designs_str (str): the designs of the large bouquets
    small_bouquets_designs_str (str): the designs of the small bouquets
    large_flowers (Counter): a counter object for small flowers
    small_flowers (Counter): a counter object for large flowers

   """

    # Get the bouquet design and flowers
    large_bouquets_designs_str = []
    small_bouquets_designs_str = []
    large_flowers = []
    small_flowers = []

    reading_bouquet_design = True

    for c in content:

        if not c:
            reading_bouquet_design = False
            continue

        if reading_bouquet_design:

            if c[1] == 'L':
                large_bouquets_designs_str.append(c)
            elif c[1] == 'S':
                small_bouquets_designs_str.append(c)
        else:
            if c[1] == 'L':
                large_flowers.append(c[0])
            elif c[1] == 'S':
                small_flowers.append(c[0])

    large_flowers = Counter(large_flowers)
    small_flowers = Counter(small_flowers)

    return large_bouquets_designs_str, small_bouquets_designs_str, large_flowers, small_flowers


def parse_bouquet_design(bouquet_design):
    """Parses a bouquet design string

    Parameters:
    bouquet_design (str): the bouquet design string

    Returns:
    design (dict): the bouquet design stored as a dict (e.g. {'a':10, 'b': 15})
    num_flowers_bouquet (int): the total number of flowers in the bouquet design
    design_name (str): the name of the design (e.g. 'AL')

   """

    design_counters = re.findall(r'[0-9]+', bouquet_design)
    for i in range(len(design_counters)):
        design_counters[i] = int(design_counters[i])
    design_species = re.findall(r'[a-z]+', bouquet_design)

    design = {}
    for i, s in enumerate(design_species):
        design[s] = design_counters[i]

    num_flowers_bouquet = design_counters[-1]
    design_name = bouquet_design[:2]

    return design, num_flowers_bouquet, design_name


def bouquet_from_design_with_most_common_flowers(design, flowers):
    """Computes the bouquet from design using the most common flowers for the extra space
       Adds the flowers one by one and add the marginal cost computed as flower scarcity

    Parameters:
    design (tuple): the bouquet design and additional information, such as the total number of flowers
                    and the bouquet design name (e.g. ({'a':10, 'b': 15}, 25, 'AL'))

    Returns:
    bouquet (dict): the bouquet stored as a dict (e.g. {'a':10, 'b': 15}). Empty if bouquet cannot be formed
    cost_value (float): the value of the cost function (bouquets with common flowers have a lower cost). 1e99 if bouquet cannot be formed

   """

    remaining_flowers_to_add = design[1]
    total_number_of_flowers = sum(flowers.values())
    bouquet = {}
    large_cost = 1e99
    cost_value = 0.0

    # add flowers one by one and add the marginal cost of addition
    # cost
    for s in design[0].keys():

        # enough flowers to complete the required design and total_number_of_flowers must be larger than 0
        if flowers[s] < design[0][s] or total_number_of_flowers <= 0:
            # design not possible
            return {}, large_cost

        bouquet[s] = 0
        for j in range(design[0][s]):
            # calculate cost
            cost_value += 1.0 - flowers[s] / total_number_of_flowers
            flowers[s] -= 1
            total_number_of_flowers -= 1
            remaining_flowers_to_add -= 1
            bouquet[s] += 1

    # bouquet completed, return
    if remaining_flowers_to_add == 0:
        return bouquet, cost_value

    # add extra space
    for i in range(remaining_flowers_to_add):

        # get the most common flower
        most_common = flowers.most_common(1)
        s = most_common[0][0]

        # specie mist mot be empty and total_number_of_flowers must be larger than 0
        if flowers[s] < 0 or total_number_of_flowers <= 0:
            return {}, large_cost

        # id specie is new in the bouquet, add it
        if s not in bouquet.keys():
            bouquet[s] = 0

        # calculate cost
        cost_value += 1.0 - flowers[s] / total_number_of_flowers
        flowers[s] -= 1
        total_number_of_flowers -= 1
        remaining_flowers_to_add -= 1
        bouquet[s] += 1

        if flowers[s] == 0:
            del flowers[s]

    return bouquet, cost_value


def compute_bouquets(designs, flowers):
    """Uses a greedy approach to maximize the number of bouquets given the available flowers and designs

    Parameters:
    designs (list): All bouquet designs. Each entry stores a tuple with the bouquet design and additional information,
                    such as the total number of flowers and the bouquet design name (e.g. ({'a':10, 'b': 15}, 25, 'AL'))

    Returns:
    bouquets (list): all computed bouquets as a list of dictionaries
    num_flowers (int): the total number of flowers left

   """

    # compute all flowers
    num_flowers = sum(flowers.values())

    bouquets = []
    while num_flowers > 0:
        bouquet_to_generate = {}
        cost = 1e99
        # first find which bouquet should be generated first, based on the minim cost
        for d in designs:
            # We need to use a deep copy because we do not want to operate with a modified variables
            # (we have not decided which design to pick)
            design = copy.deepcopy(d)
            flowers_copy = copy.deepcopy(flowers)
            bouquet, minimum_cost = bouquet_from_design_with_most_common_flowers(design, flowers_copy)
            if minimum_cost < cost:
                cost = minimum_cost
                bouquet_to_generate = (bouquet, design[2])

        if not bouquet_to_generate:
            break

        # generate the bouquet with the minimum cost
        bouquets.append(bouquet_to_generate)
        for s in bouquet_to_generate[0].keys():
            num_flowers -= bouquet_to_generate[0][s]
            flowers[s] -= bouquet_to_generate[0][s]

    return bouquets, num_flowers


def encode_bouquets(bouquets):
    """Given a list of bouquets dictionaries, produces a list of strings, where each entry is an encoded bouquet.
       Species  must be ordered alphabetically in the encoding

    Parameters:
    designs (list): bouquets as a list of dictionaries

    Returns:
    encoded_bouquet (list): a listed of encoded bouquets

   """

    encoded_bouquet = []
    for b in bouquets:
        enc = b[1]
        od = OrderedDict(sorted(b[0].items()))
        for s, v in od.items():
            enc += str(v) + s
        encoded_bouquet.append(enc)

    return encoded_bouquet


def compute(input_file):
    """Given the input file, computes the list of large and small flowers bouquets. the aim is to produce as many bouquets as possible

    Parameters:
    input_file (str): the input file name

    Returns:
    encoded_large_bouquets (list): a listed of encoded bouquets
    encoded_small_bouquet (list): a listed of encoded bouquets

   """

    content = get_content(input_file)
    if not content:
        print('empty content, nothing to do ')
        return

    large_bouquet_designs_str, small_bouquet_designs_str, large_flowers, small_flowers = parse_content(content)


    large_bouquet_designs = []
    for d in large_bouquet_designs_str:
        design, num_flowers_bouquet, design_name = parse_bouquet_design(d)
        large_bouquet_designs.append((design, num_flowers_bouquet, design_name))

    small_bouquet_designs = []
    for d in small_bouquet_designs_str:
        design, num_flowers_bouquet, design_name = parse_bouquet_design(d)
        small_bouquet_designs.append((design, num_flowers_bouquet, design_name))

    # compute all large bouquets
    print('large flowers before before forming large bouquets ', large_flowers)
    print('small flowers before before forming small bouquets ', small_flowers)

    large_bouquets, num_large_flowers_left = compute_bouquets(large_bouquet_designs, large_flowers)
    small_bouquets, num_small_flowers_left = compute_bouquets(small_bouquet_designs, small_flowers)

    print('large flowers before after forming large bouquets ', large_flowers)
    print('small flowers before after forming small bouquets ', small_flowers)

    print('number large bouquets formed ', len(large_bouquets))
    print('number small bouquets formed ', len(small_bouquets))

    # encode bouquets
    encoded_large_bouquets = encode_bouquets(large_bouquets)
    encoded_small_bouquet = encode_bouquets(small_bouquets)

    # save results to file and stream it to standard output
    with open("output.txt", 'w') as f:
        print('large bouquets formed ')
        for v in encoded_large_bouquets:
            f.write("%s\n" % v)
            print(v)
        print('small bouquets formed ')
        for v in encoded_small_bouquet:
            f.write("%s\n" % v)
            print(v)


if __name__ == "__main__":

    #name of input and output files
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file",
                        help="The input file containing bouquet designs and flowers",
                        nargs='?',
                        default="")
    args = parser.parse_args()
    input_file = args.input_file

    #compute bouquets
    compute(input_file)

