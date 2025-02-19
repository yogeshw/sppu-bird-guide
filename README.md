# Birds of SPPU Campus

This project aims to create a comprehensive bird guide for the birds of the Savitribai Phule Pune University (SPPU) campus, available in both LaTeX and HTML formats.

## Project Overview

The guide includes:

* **High-Quality Images:** Professional photographs of each bird species found on campus
* **Detailed Descriptions:** Comprehensive text descriptions similar to those found in classic Indian bird guides
* **Bilingual Support:** Available in both English and Marathi
* **Multiple Formats:** 
  - Elegant LaTeX layout with one bird per page
  - Responsive HTML version for web browsers
  - Consistent design across both formats

## Repository Structure

```
.
├── data/         # Bird data and listings
├── html/         # HTML version and web resources
│   ├── images/   # Optimized images for web
│   └── css/      # Style sheets
├── images/       # Original high-resolution bird images
├── latex/        # LaTeX source files
└── scripts/      # Automation and conversion scripts
```

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd sppu-bird-guide
   ```

2. **View the guide:**
   - Open `html/bird_guide.html` in a web browser for the English version
   - Open `html/bird_guide_marathi.html` for the Marathi version
   - For the LaTeX version, see the build instructions below

## Contributing

1. **Fork and clone:**
   ```bash
   git clone git@github.com:<your-username>/sppu-bird-guide.git
   cd sppu-bird-guide
   ```

2. **Create a new branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes:**
   - Add new bird entries
   - Improve existing content
   - Fix errors or enhance styling
   - Add translations

4. **Submit your changes:**
   ```bash
   git add .
   git commit -m "Description of your changes"
   git push origin feature/your-feature-name
   ```

5. Open a Pull Request on GitHub

## Building the Guide

### Prerequisites
- LaTeX distribution (TeX Live recommended)
- Pandoc (for HTML conversion)
- ImageMagick (for image processing)

### LaTeX to HTML Conversion

1. **Install dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install texlive-full pandoc imagemagick
   ```

2. **Run the conversion:**
   ```bash
   ./scripts/convert_to_html.sh
   ```

## Project Status

- [x] Initial bird catalog
- [x] English guide
- [x] Marathi translation
- [x] Web version
- [ ] Mobile-responsive design
- [ ] Interactive features
- [ ] Seasonal bird information

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).

## Acknowledgments

- Contributing photographers (credits in individual image files) to the Macaulay Library
- e-bird
