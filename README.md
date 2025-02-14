# Birds of SPPU Campus

This project aims to create a bird guide for the birds of the Savitribai Phule Pune University (SPPU) campus, available in both LaTeX and HTML formats.

## Project Overview

The guide includes:

*   **High-Quality Images:** A photograph of each bird species.
*   **Detailed Descriptions:** Text descriptions similar to those found in classic Indian bird guides.
*   **Elegant LaTeX Design:** A visually appealing layout with one bird per page, text on the left, and the bird's photo on the right.
*   **Single-File HTML Version:** A comprehensive, accessible HTML guide that mirrors the LaTeX content.

## Repository Structure

*   `latex/`: LaTeX source files, images, and style files.
*   `html/`: HTML output and related resources (CSS, images).
*   `scripts/`: Conversion and automation scripts.
*   `images/`: Bird images used in both LaTeX and HTML versions.
*   `README.md`: This file.

## Instructions for Contributors

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd sppu-bird-guide
    ```
2.  **Create a new branch:**

    ```bash
    git checkout -b feature/new-bird-entry
    ```
3.  **Make changes:** Add content, correct errors, improve styling, etc.
4.  **Commit your changes:**

    ```bash
    git add .
    git commit -m "Add new bird entry: <Bird Name>"
    ```
5.  **Push to your branch:**

    ```bash
    git push origin feature/new-bird-entry
    ```
6.  **Submit a pull request:** On GitHub, create a pull request from your branch to the `main` branch.

## Conversion Process (LaTeX to HTML)

The `scripts/convert_to_html.sh` script automates the conversion from LaTeX to HTML using Pandoc.

1.  **Install Pandoc:** Follow the instructions at [https://pandoc.org/installing.html](https://pandoc.org/installing.html).
2.  **Run the conversion script:**

    ```bash
    ./scripts/convert_to_html.sh
    ```

This script:

*   Copies images to the `html/images` directory.
*   Executes Pandoc with the necessary options to generate the HTML output.

## Key Technologies

*   **LaTeX:** Typesetting and document preparation.
*   **Pandoc:** Document conversion.
*   **Lua:** Scripting for Pandoc filters.
*   **HTML/CSS:** Web presentation.

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).
