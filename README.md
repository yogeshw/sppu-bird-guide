# Birds of the University of Pune

This project aims to create a bird guide for the Birds of the University of Pune in both LaTeX and HTML formats. The guide will include a photo of each bird and accompanying text similar to the content in the book of Indian birds available at [Book of Indian Birds](https://archive.org/download/BookOfIndianBirds/BookIndianBirds.pdf). The LaTeX version will have an elegant design in terms of fonts and layout, with one bird per page, text on the left, and the bird photo on the right. The HTML version will always track the LaTeX version in content but will be a single file.

## Repository Structure

- `latex/`: Contains all LaTeX-related files, including the main LaTeX document and additional resources such as images and style files.
- `html/`: Contains all HTML-related files, including the main HTML document and additional resources such as images and stylesheets.
- `scripts/`: Contains scripts used for converting LaTeX to HTML or other automation tasks.
- `data/`: Contains data files, such as the list of birds and their descriptions.
- `docs/`: Contains documentation related to the project, such as instructions for contributors and usage guidelines.
- `images/`: Contains images of the birds. Both the LaTeX and HTML versions will use the same images.

## Instructions for Contributors

1. Clone the repository:
   ```
   git clone https://github.com/githubnext/workspace-blank.git
   cd workspace-blank
   ```

2. Create a new branch for your changes:
   ```
   git checkout -b your-branch-name
   ```

3. Make your changes and commit them:
   ```
   git add .
   git commit -m "Description of your changes"
   ```

4. Push your changes to the remote repository:
   ```
   git push origin your-branch-name
   ```

5. Create a pull request on GitHub.

## Converting LaTeX to HTML

To convert the LaTeX document to HTML, use the `pandoc` tool. Follow these steps:

1. Install `pandoc` if you haven't already. You can find installation instructions at [Pandoc Installation](https://pandoc.org/installing.html).

2. Run the conversion script:
   ```
   ./scripts/convert_to_html.sh
   ```

The script will generate an HTML file from the LaTeX source file, ensuring that the HTML version always tracks the LaTeX version in content.
