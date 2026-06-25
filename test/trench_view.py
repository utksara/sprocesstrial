import sys
import os

from pysentopo import visualize_trench

def main():
    # Defaults
    csv_file = "task1_results/simulation_results.csv"
    row_id = 1
    
    # Parse CLI arguments if provided
    if len(sys.argv) > 1:
        try:
            row_id = int(sys.argv[1])
        except ValueError:
            print("Error: Row ID must be an integer.")
            print("Usage: poetry run python test/trench_view.py [row_id] [csv_file_path]")
            sys.exit(1)
            
    if len(sys.argv) > 2:
        csv_file = sys.argv[2]
        
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found.")
        sys.exit(1)
        
    print(f"Processing 3D view for Row ID: {row_id} from '{csv_file}'...")
    visualize_trench(csv_file, row_id)

if __name__ == "__main__":
    main()