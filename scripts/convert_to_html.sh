#!/bin/bash

# Convert both English and Marathi LaTeX to HTML using pandoc
# Ensure pandoc is installed before running this script

# Define input and output files
ENGLISH_INPUT="../latex/bird_guide.tex"
MARATHI_INPUT="../latex/bird_guide_marathi.tex"
ENGLISH_OUTPUT="../html/bird_guide.html"
MARATHI_OUTPUT="../html/bird_guide_marathi.html"

# Create required directories
#mkdir -p ../html
#mkdir -p ../html/images

# Copy all images to HTML directory if they exist
#if compgen -G "../images/*.jpg" > /dev/null; then
#  cp ../images/*.jpg ../html/images/
#else
#  echo "No images to copy."
#fi

# Add additional pandoc options for better image handling
PANDOC_OPTS="--standalone \
  --toc \
  --css=style.css \
  --from=latex+raw_tex \
  --to=html \
  --lua-filter=../scripts/fix_image_paths.lua \
  --extract-media=../html/images \
  --wrap=none \
  --metadata=lang:en"

# Copy script.js to HTML directory
#cp ../html/script.js ../html/

# Convert English version
pandoc $PANDOC_OPTS \
  --metadata title="Birds of SPPU Campus" \
  "$ENGLISH_INPUT" -o "$ENGLISH_OUTPUT"

# Convert Marathi version
pandoc $PANDOC_OPTS \
  --metadata title="एस.पी.पी.यू परिसरातील पक्षी" \
  --variable mainfont="Noto Serif Devanagari" \
  --variable monofont="Noto Sans Devanagari" \
  --html-q-tags \
  "$MARATHI_INPUT" -o "$MARATHI_OUTPUT"

# Add script.js to HTML files
if [ -f "$ENGLISH_OUTPUT" ]; then
  sed -i '/<\/body>/i <script src="script.js"></script>' "$ENGLISH_OUTPUT"
fi
if [ -f "$MARATHI_OUTPUT" ]; then
  sed -i '/<\/body>/i <script src="script.js"></script>' "$MARATHI_OUTPUT"
fi

# Create basic CSS file if it doesn't exist
if [ ! -f "../html/style.css" ]; then
  cat > "../html/style.css" << 'EOF'
body {
  font-family: 'Noto Serif', 'Noto Serif Devanagari', serif;
  line-height: 1.6;
  margin: 0;
  padding: 0;
  background-color: #f4f4f9;
  color: #333;
}

h1, h2, h3, h4, h5, h6 {
  color: #2c3e50;
  margin-top: 1em;
}

h1 {
  font-size: 2.5em;
  text-align: center;
  margin-bottom: 0.5em;
}

h2 {
  font-size: 2em;
  border-bottom: 2px solid #2c3e50;
  padding-bottom: 0.3em;
}

h3 {
  font-size: 1.75em;
}

h4 {
  font-size: 1.5em;
}

h5 {
  font-size: 1.25em;
}

h6 {
  font-size: 1em;
}

p {
  margin: 0.5em 0;
}

ul, ol {
  margin: 1em 0;
  padding-left: 1.5em;
}

li {
  margin-bottom: 0.5em;
}

a {
  color: #3498db;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.container {
  width: 80%;
  margin: 0 auto;
  padding: 2em 0;
}

.header {
  background-color: #2c3e50;
  color: white;
  padding: 1em 0;
  text-align: center;
}

.footer {
  background-color: #2c3e50;
  color: white;
  padding: 1em 0;
  text-align: center;
  position: fixed;
  width: 100%;
  bottom: 0;
}

.card {
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin: 1em 0;
  padding: 1em;
}

.card img {
  max-width: 100%;
  height: auto;
  border-radius: 5px;
}

.card h3 {
  margin-top: 0;
}

.card p {
  margin: 0.5em 0;
}

@media (max-width: 768px) {
  .container {
    width: 95%;
  }
}
EOF
fi

# Print completion message
echo "Conversion complete. HTML files generated at:"
echo "- $ENGLISH_OUTPUT"
echo "- $MARATHI_OUTPUT"
