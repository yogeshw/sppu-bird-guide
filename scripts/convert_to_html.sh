#!/bin/bash

# Convert both English and Marathi LaTeX to HTML using pandoc
# Ensure pandoc is installed before running this script

# Define input and output files
ENGLISH_INPUT="../latex/bird_guide.tex"
MARATHI_INPUT="../latex/bird_guide_marathi.tex"
ENGLISH_OUTPUT="../html/bird_guide.html"
MARATHI_OUTPUT="../html/bird_guide_marathi.html"

# Create required directories
mkdir -p ../html
mkdir -p ../html/images

# Copy all images to HTML directory
echo "Copying images..."
cp ../images/*.jpg ../html/images/

# Add additional pandoc options for better image handling
PANDOC_OPTS="--standalone \
  --toc \
  --css=style.css \
  --from=latex+raw_tex \
  --to=html \
  --lua-filter=../scripts/fix_image_paths.lua \
  --extract-media=../html \
  --wrap=none \
  --metadata=lang:en \
  --parse-raw"

# Create images directory and copy images
mkdir -p ../html/images
cp -r ../images/*.jpg ../html/images/

echo "Converting English version..."
pandoc $PANDOC_OPTS \
  --metadata title="Birds of SPPU Campus" \
  "$ENGLISH_INPUT" -o "$ENGLISH_OUTPUT"

echo "Converting Marathi version..."
pandoc $PANDOC_OPTS \
  --metadata title="एस.पी.पी.यू परिसरातील पक्षी" \
  --variable mainfont="Noto Serif Devanagari" \
  --variable monofont="Noto Sans Devanagari" \
  --html-q-tags \
  "$MARATHI_INPUT" -o "$MARATHI_OUTPUT"

echo "Conversion complete. HTML files generated at:"
echo "- $ENGLISH_OUTPUT"
echo "- $MARATHI_OUTPUT"

# Create basic CSS file if it doesn't exist
if [ ! -f "../html/style.css" ]; then
  cat > "../html/style.css" << 'EOF'
body {
  font-family: 'Noto Serif', 'Noto Serif Devanagari', serif;
  max-width: 1200px;
  margin: auto;
  padding: 1em;
  line-height: 1.5;
}

:lang(mr) { 
  font-family: 'Noto Serif Devanagari', serif;
}

h1, h2, h3 {
  color: #228B22;  /* Forest Green */
}

img {
  max-width: 100%;
  height: auto;
}
EOF
fi
