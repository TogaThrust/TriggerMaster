# TriggerMaster
CSV data manipulator. 

Takes a CSV file with multiple columns, and generate all possible combinations of each non NAN row under those column.

For example:

// Input //

Columns A B C
Row 1   1 2 3
Row 2   4   6

// Outputs //

Columns A B C
Row 1   1 2 3
Row 2   1 2 6
Row 3   4 2 3
Row 3   4 2 6