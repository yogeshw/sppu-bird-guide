#!/bin/bash

# Convert both English and Marathi LaTeX to HTML using make4ht
# Ensure make4ht is installed before running this script

# Define base directory and other paths
BASE_DIR="/home/yogesh/sppu-bird-guide"
LATEX_DIR="$BASE_DIR/latex"
HTML_DIR="$BASE_DIR/html"
IMG_DIR="$BASE_DIR/images"

# Create required directories if they don't exist
mkdir -p "$HTML_DIR"
mkdir -p "$HTML_DIR/images"

# Copy all images to HTML directory if they exist
if compgen -G "$IMG_DIR/*.jpg" > /dev/null; then
  cp "$IMG_DIR"/*.jpg "$HTML_DIR/images/"
else
  echo "No images to copy."
fi

# Create a custom make4ht config file for Latin script
cat > "$LATEX_DIR/config.cfg" << 'EOF'
\Preamble{xhtml}
\Configure{graphics*}{jpg}{\Picture[pict]{\csname Gin@base\endcsname.jpg}}
\Configure{@HEAD}{\HCode{<link rel="stylesheet" type="text/css" href="style.css" />\Hnewline}}
\begin{document}
\EndPreamble
EOF

# Create a custom make4ht config file for Devanagari script
cat > "$LATEX_DIR/config_marathi.cfg" << 'EOF'
\Preamble{xhtml}
\Configure{graphics*}{jpg}{\Picture[pict]{\csname Gin@base\endcsname.jpg}}
\Configure{@HEAD}{\HCode{<link rel="stylesheet" type="text/css" href="style.css" />\Hnewline}}
\special{t4ht>head.cfg}
\begin{document}
\EndPreamble
EOF

# Create special head config for Devanagari
cat > "$LATEX_DIR/head.cfg" << 'EOF'
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /> 
<meta name="viewport" content="width=device-width, initial-scale=1"/>
EOF

# Create tex4ht configuration file for XeTeX
cat > "$LATEX_DIR/tex4ht.env" << 'EOF'
\def\Apply{\HCode{<link rel="stylesheet" type="text/css" href="style.css" />\Hnewline}}
\Configure{VERSION}{}
\Configure{DOCTYPE}{\HCode{<!DOCTYPE html>\Hnewline}}
\Configure{HTML}{\HCode{<html>\Hnewline}}{\HCode{\Hnewline</html>}}
\Configure{@HEAD}{}
\Configure{@HEAD}{\HCode{<meta charset="UTF-8" />\Hnewline}}
\Configure{@HEAD}{\HCode{<meta name="viewport" content="width=device-width, initial-scale=1"/>\Hnewline}}
\Configure{@HEAD}{\Apply}
EOF

# Convert English version
cd "$LATEX_DIR"
htlatex bird_guide.tex "config.cfg,xhtml,charset=utf-8" " -cunihtf -utf8"
if [ -f "bird_guide.html" ]; then
    mv bird_guide.html "$HTML_DIR/"
fi

# Convert Marathi version using XeTeX explicitly
cd "$LATEX_DIR"
export TEXMFHOME="$LATEX_DIR"
xelatex -no-pdf bird_guide_marathi.tex
tex4ht -f bird_guide_marathi.tex
t4ht -f bird_guide_marathi.tex
if [ -f "bird_guide_marathi.html" ]; then
    mv bird_guide_marathi.html "$HTML_DIR/"
fi

# Move CSS files if they exist
for f in *.css; do
    [ -f "$f" ] && mv "$f" "$HTML_DIR/"
done

# Add script.js to HTML files
if [ -f "$HTML_DIR/bird_guide.html" ]; then
  sed -i '/<\/body>/i <script src="script.js"></script>' "$HTML_DIR/bird_guide.html"
fi
if [ -f "$HTML_DIR/bird_guide_marathi.html" ]; then
  sed -i '/<\/body>/i <script src="script.js"></script>' "$HTML_DIR/bird_guide_marathi.html"
fi

# Update CSS for better styling
cat > "$HTML_DIR/style.css" << 'EOF'
body {
  font-family: 'Noto Serif', 'Noto Serif Devanagari', serif;
  line-height: 1.6;
  margin: 0 auto;
  max-width: 1200px;
  padding: 2em;
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

.minipage {
  display: inline-block;
  vertical-align: top;
  width: 48%;
  margin: 1%;
}

.mdframed {
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin: 1em 0;
  padding: 1em;
}

img {
  max-width: 100%;
  height: auto;
  border-radius: 5px;
  display: block;
  margin: 1em auto;
}

a {
  color: #3498db;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.index {
  column-count: 2;
  column-gap: 2em;
}

@media (max-width: 768px) {
  .minipage {
    width: 100%;
    margin: 1em 0;
  }
  
  .index {
    column-count: 1;
  }
}
EOF

# Clean up intermediate files
cd "$LATEX_DIR"
rm -f *.4ct *.4tc *.aux *.dvi *.idv *.lg *.log *.out *.tmp *.xref *.fls *.fdb_latexmk
rm -f *.css *.idv *.html *.4dx *.4ix *.4nt *.eps *.png *.ps *.svg
rm -f *.tid *.toc *.tms *.dvi *.ref *.thm
rm -f *.blg *.bbl *.ilg *.ind *.lof *.lot *.nav *.snm *.vrb
rm -f tex4ht.* texput.* *.idx *.xdv *.html.* *.odt

# Print completion message
echo "Conversion complete. HTML files generated in $HTML_DIR"
