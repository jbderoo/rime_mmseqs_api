#!/bin/bash

# Function to display help message
show_help() {
    echo "Usage: $0 [options] <input_fasta> <output_dir>"
    echo
    echo "Generate MSA's using colabfold_search via MMSEQS with specified input FASTA file and output directory."
    echo
    echo "Options:"
    echo "  -h, --help   Show this help message and exit"
    echo
    echo "Arguments:"
    echo "  input_fasta  Path to the input FASTA file; can have multiple sequences in 1 file"
    echo "  output_dir   Path to the output directory"
    echo
}

# Check for help option
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 input_fasta output_dir"
    exit 1
fi

# Assign arguments to variables
INPUT_FASTA=$1
OUTPUT_DIR=$2

# /data/database/
SECONDS=0
# I know it's annoying but remember; for the api to work, FULL paths
/home/csnow/code/localcolabfold/localcolabfold/colabfold-conda/bin/colabfold_search $INPUT_FASTA /vault/databases/ $OUTPUT_DIR \
        --db1 /data/database/uniref30_2302_db \
	--db3 /data/database/colabfold_envdb_202108_db \
	--db-load-mode 2 \
        --mmseqs /home/csnow/miniforge3/envs/flask/bin/mmseqs

elapsed_time=$SECONDS
echo -e "\n\e[32mFrom Jacob:\nThe operation took $elapsed_time seconds\e[0m"
