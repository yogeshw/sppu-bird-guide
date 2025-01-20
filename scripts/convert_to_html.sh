#!/bin/bash

# Convert LaTeX to HTML using pandoc
# Ensure pandoc is installed before running this script

# Define input and output files
INPUT_FILE="../latex/bird_guide.tex"
OUTPUT_FILE="../html/bird_guide.html"

# Run pandoc to convert LaTeX to HTML
pandoc "$INPUT_FILE" -o "$OUTPUT_FILE" --standalone --toc --css=style.css

echo "Conversion complete. HTML file generated at $OUTPUT_FILE"
