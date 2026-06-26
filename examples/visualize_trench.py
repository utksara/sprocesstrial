import sys
from pysentopo import visualize_from_csv

if __name__ == "__main__":
    # csv_file = "task2_results/simulation_results.csv"
    csv_file = "etchingWithPlasma/results.csv"
    row_id = 8
    if len(sys.argv) > 1:
        row_id = int(sys.argv[1])
    if len(sys.argv) > 2:
        csv_file = sys.argv[2]
        
    visualize_from_csv(csv_file, row_id)
