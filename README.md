# Bloomon code challenge

## Approach

The challenge can be approached in several ways. One could generate all valid bouquets codes, without maximizing the number of bouquets.
Another approach is maximizing the number of bouquets given the available designs and flowers. 
I followed the latter approach, following these steps:

+ Parse the file sample.txt, separating large and small designs and flowers.

+ For each group (large/small), generate the bouquets as follow:

    + Loop over the designs, for each design compute the minimum total cost of forming a valid bouquet. 
    The cost is calculated by summing the marginal cost of adding every single flower to the bouquet. 
    The marginal cost is proportional to the scarcity of a given flower specie (1.0 - num_flowers_specie_in_group/total_num_flowers_in_group). 
    For the designs with extra space available, the most common flower specie is added (i.e. the one that adds the lower cost).

    + Among the available designs, choose the design having the lower cost. 
    
    + Update the number of available flowers for each specie.

    + Repeat until no bouquet can be generated.
    
  This approach uses a greedy algorithm to maximize the number of bouquets for each group (large/small). 
  For the flowers available in the sample.txt input file, 15 large and 15 small bouquets were generated.
  
+ From the generated bouquets encode the bouquet code and print the results to standard output.

## Build docker

    docker build -t bloomon_solution .

## Run docker

Input designs and species are read from standard input (after two empty lines the application is executed). 
Output is streamed to the standard the output and stored in output.txt.

    docker run -ti bloomon_solution
    
Input designs and species are read from sample.txt. Output is streamed to the standard the output and stored in output.txt.

    docker run -it bloomon_solution sample.txt 
    
