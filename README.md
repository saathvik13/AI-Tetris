# Fomulation

The problem is formulated as a search problem with MAX node and RAND node. We want to choose the command that maximize the expected heuristic.

# Heuristic

Given a board, we calculate its heuristic as follows:

1. Count number of rows that are already full and multiply them by `ComputerPlayer.LINE_SCORE`, as variable `score`.
2. Obtain the index of first row that is not empty, and record as `non_empty_idx`.
3. Starting from `non_empty_idx`, we count number of spaces. For spaces that do not have `x` on them, the costs are `ComputerPlayer.OPEN_COSTS`; for spaces that have `x` on them, the costs are `ComputerPlayer.ENCLOSE_COSTS`. These costs are multiplied by `(y / height)`, which is used to encourage to not remain empty spaces at bottom of the board, and sumed into `costs` variable.
4. Final heuristic is `score - costs`.
5. `LINE_SCORE` is set to be very big to encourage elimination of lines to get score, and `ENCLOSE_COSTS` is also much larger than `OPEN_COSTS` intuitively.

# Search

For a `max_node`, we consider all possible rotations of current piece (repeat ones are removed) and all possible locations they can fall to obtain many new boards. For each of these boards, we calculate its expected reward using `rand_node`, so to get the maximum one as the result for this `max_node`.

For a `rand_node`, we firstly check if `depth`, which is a variable that is used to restrict depth of tree and that is decremented for each `max_node`, already reaches `0`. If so, we just calculate the heuritic without going further. Otherwise, we get its expected score. One thing to note is that when `next_piece` is given, we can directly calculate its `max_node` without calculating any random expectation.

The statistics of distrubition is updated becore each move. We have tackled the rotation: even if the given piece is rotated, we can still identify which original piece it belongs to.

# Problems

The program quickly becomes slow as depth is slightly higher. As long as `depth == 2`, which starts to consider random node, the program becomes quite slow: it takes about 10 seconds to figure out the command.

# Assumptions

We did not consider any complicated move in animated version that is mentioned in specification.