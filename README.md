# TriggerMaster
CSV data manipulator. 

Takes a CSV file with multiple columns, and generate all possible combinations of each non NAN row under those column.

For example:

// Input //

A  |  B  |  C
-------------
1  |  2  |  3
-------------
4  | NAN |  6
-------------
// Outputs //

A  |  B  |  C
-------------
1  |  2  |  3
-------------
1  |  2  |  6
-------------
4  |  2  |  3
-------------
4  |  2  |  6
-------------