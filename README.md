# NeurIPS-Paper-Scraper
This repository contains web scraping scripts for extracting research paper details from the NeurIPS conference website. It includes a Java implementation with a Swing GUI and a Python version using aiohttp and Tkinter for asynchronous scraping.
## Java Setup

1. **Install Eclipse**: Download from [Eclipse IDE](https://www.eclipse.org/downloads/).
2. **Create a New Java Project**.
3. **Add Jsoup Library**:
   - Download Jsoup from [jsoup.org](https://jsoup.org/download).
   - Add the JAR to your project:
     - Right-click on the project > `Build Path` > `Configure Build Path` > `Add External JARs`.
4. **Run the Scraper**: Copy `Scraper.java` to the `src` folder and run it as a Java Application.

## Python Setup

1. **Install Python**: Download from [python.org](https://www.python.org/downloads/).
2. **Install Visual Studio Code**: Download from [VS Code](https://code.visualstudio.com/).
3. **Open Terminal in VS Code** and run:
   ```bash
   py -m pip install aiohttp aiofiles beautifulsoup4 tk
   py Scraper.py
