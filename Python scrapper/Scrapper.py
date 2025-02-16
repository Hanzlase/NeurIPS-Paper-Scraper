import sys

sys.path.append(r"E:\SEMESTER\Python scrapper\Packages")
import threading
import ssl
from pathlib import Path
import aiofiles
from typing import List, Dict
import time
from bs4 import BeautifulSoup
import random
import os
import csv
import asyncio
import aiohttp
from tkinter import ttk, scrolledtext, messagebox
import tkinter as tk
from lxml import html  # Import lxml for XPath


class NeurIPSScraper(tk.Tk):
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    ]

    def __init__(self):
        super().__init__()
        self.title("NeurIPS Paper Scraper")
        self.configure(bg='#ECF0F1')
        self.state('zoomed')

        # Color Palette
        self.PRIMARY_COLOR = '#2980B9'
        self.SECONDARY_COLOR = '#3498DB'
        self.BACKGROUND_COLOR = '#ECF0F1'
        self.ACCENT_COLOR = '#2ECC71'
        self.TEXT_COLOR = '#2C3E50'

        self.metadata_list = []
        self.create_styles()
        self.initialize_gui()

    def create_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TFrame', background=self.BACKGROUND_COLOR)
        style.configure('TLabelFrame', background=self.BACKGROUND_COLOR,
                        foreground=self.TEXT_COLOR, font=('Arial', 10, 'bold'))

        style.configure('TLabel', background=self.BACKGROUND_COLOR,
                        foreground=self.TEXT_COLOR, font=('Arial', 10))
        style.configure('Header.TLabel', font=(
            'Arial', 24, 'bold'), foreground=self.PRIMARY_COLOR)

        style.configure('TEntry', fieldbackground='white',
                        foreground=self.TEXT_COLOR)

        style.configure('TButton', background=self.PRIMARY_COLOR, foreground='white', font=(
            'Arial', 10, 'bold'), borderwidth=0, focusthickness=3)
        style.map('TButton',
                  background=[('active', self.SECONDARY_COLOR)],
                  foreground=[('active', 'white')])

        style.configure("Treeview",
                        background="white",
                        foreground=self.TEXT_COLOR,
                        fieldbackground="white",
                        font=('Arial', 10))
        style.configure("Treeview.Heading",
                        background=self.PRIMARY_COLOR,
                        foreground="white",
                        font=('Arial', 10, 'bold'))

    def initialize_gui(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        header_frame = self.create_header_frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        content_frame = self.create_content_frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        footer_frame = self.create_footer_frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=(10, 0))

    def create_header_frame(self, parent):
        header_frame = ttk.Frame(parent)

        title_frame = ttk.Frame(header_frame)
        title_frame.pack(fill=tk.X)
        title_label = ttk.Label(
            title_frame,
            text="NeurIPS Paper Scraper",
            style='Header.TLabel'
        )
        title_label.pack(pady=10)

        input_frame = ttk.LabelFrame(header_frame, text="Options", padding=10)
        input_frame.pack(fill=tk.X, pady=5)

        year_frame = ttk.Frame(input_frame)
        year_frame.pack(fill=tk.X, pady=5)

        ttk.Label(year_frame, text="Start Year:").pack(side=tk.LEFT, padx=5)
        self.start_year = ttk.Entry(year_frame, width=10)
        self.start_year.insert(0, "2019")
        self.start_year.pack(side=tk.LEFT, padx=5)

        ttk.Label(year_frame, text="End Year:").pack(side=tk.LEFT, padx=5)
        self.end_year = ttk.Entry(year_frame, width=10)
        self.end_year.insert(0, "2023")
        self.end_year.pack(side=tk.LEFT, padx=5)

        dir_frame = ttk.Frame(input_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dir_frame, text="Download Directory:").pack(
            side=tk.LEFT, padx=5)
        self.download_dir = ttk.Entry(dir_frame)
        self.download_dir.insert(0, "pdfs")
        self.download_dir.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        button_frame = ttk.Frame(header_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.scrape_button = ttk.Button(
            button_frame,
            text="Scrape Metadata",
            command=self.scrape_metadata
        )
        self.scrape_button.pack(side=tk.LEFT, padx=5)

        self.download_button = ttk.Button(
            button_frame,
            text="Download PDFs",
            command=self.download_pdfs,
            state=tk.DISABLED
        )
        self.download_button.pack(side=tk.LEFT, padx=5)

        return header_frame

    def create_content_frame(self, parent):
        content_frame = ttk.Frame(parent)

        columns = ("Title", "Authors", "Year", "Abstract", "PDF Link", "Abstract Link")
        self.tree = ttk.Treeview(content_frame, columns=columns, show='headings')

        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Title":
                self.tree.column(col, width=300)
            elif col == "Authors":
                self.tree.column(col, width=200)
            elif col == "Year":
                self.tree.column(col, width=70)
            elif col == "Abstract":
                self.tree.column(col, width=400)
            else:
                self.tree.column(col, width=200)

        vsb = ttk.Scrollbar(content_frame, orient="vertical",
                           command=self.tree.yview)
        hsb = ttk.Scrollbar(
            content_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')

        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        return content_frame

    def create_footer_frame(self, parent):
        footer_frame = ttk.Frame(parent)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            footer_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.log_area = scrolledtext.ScrolledText(
            footer_frame,
            height=6,
            width=80,
            bg='white',
            fg=self.TEXT_COLOR,
            font=('Arial', 10)
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)

        return footer_frame

    def log(self, message: str):
        self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.see(tk.END)

    async def get_abstract(self, session: aiohttp.ClientSession, abstract_url: str, year: int, max_retries=3) -> str:
        """Fetch abstract text from the given URL using XPath with retry logic."""
        headers = {'User-Agent': random.choice(self.USER_AGENTS)}
        retry_delay = 1  # Initial delay in seconds

        for attempt in range(max_retries):
            try:
                async with session.get(abstract_url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        tree = html.fromstring(html_content)  # Use lxml to parse HTML

                        # Extract abstract using XPath
                        abstract_nodes = tree.xpath('/html/body/div[2]/div/p[6]/text()')  # Use the provided XPath
                        if abstract_nodes:
                            abstract_text = ''.join(abstract_nodes).strip()  # Concatenate nodes in case of multiple matches
                            return abstract_text
                        else:
                            self.log(f"Abstract not found using XPath on page {abstract_url}")
                            return "Abstract not available (XPath not found)"
                    else:
                        self.log(f"Failed to fetch abstract from {abstract_url}: HTTP {response.status}")
                        if response.status == 404:
                            return "Abstract not available (404 Not Found)"
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                        continue

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                self.log(
                    f"Error fetching abstract from {abstract_url} (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    return f"Error fetching abstract (after {max_retries} retries): {str(e)}"

            except Exception as e:
                self.log(f"Unexpected error fetching abstract from {abstract_url}: {str(e)}")
                return f"Error fetching abstract (unexpected error): {str(e)}"

        return "Abstract not available (max retries exceeded)"

    async def download_pdf(self, session: aiohttp.ClientSession, pdf_url: str, destination_path: str) -> bool:
        headers = {'User-Agent': random.choice(self.USER_AGENTS)}
        try:
            async with session.get(pdf_url, headers=headers) as response:
                if response.status == 200:
                    async with aiofiles.open(destination_path, 'wb') as f:
                        await f.write(await response.read())
                    return True
                self.log(f"Failed to download {pdf_url}: HTTP {response.status}")
                return False
        except Exception as e:
            self.log(f"Error downloading {pdf_url}: {str(e)}")
            return False

    async def scrape_year(self, session: aiohttp.ClientSession, year: int) -> List[Dict]:
        if year < 2019:
            base_url = f"https://papers.nips.cc/paper/{year}"
            pdf_base = f"https://papers.nips.cc/paper_files/paper/{year}/file"
        else:
            base_url = f"https://proceedings.neurips.cc/paper/{year}"
            pdf_base = f"https://proceedings.neurips.cc/paper/{year}/file"

        headers = {'User-Agent': random.choice(self.USER_AGENTS)}
        papers = []

        try:
            async with session.get(base_url, headers=headers) as response:
                if response.status != 200:
                    self.log(f"Failed to fetch year {year}: HTTP {response.status}")
                    return papers

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                paper_links = soup.select("a[title='paper title']")

                for paper_link in paper_links:
                    await asyncio.sleep(random.uniform(0.1, 0.3))  # Add a delay between requests
                    try:
                        title = paper_link.text.strip()
                        authors_tag = paper_link.find_next('i')
                        authors = authors_tag.text.strip() if authors_tag else ""

                        abstract_url = paper_link.get('href', '')
                        if 'Abstract' in abstract_url:
                            paper_hash = abstract_url.split('/')[-1].split('-Abstract')[0]

                            if year >= 2021:
                                pdf_link = f"{pdf_base}/{paper_hash}-Paper-Conference.pdf"
                            else:
                                pdf_link = f"{pdf_base}/{paper_hash}-Paper.pdf"

                            # Construct abstract link based on year
                            if year >= 2022:
                                abstract_link = f"https://papers.nips.cc/paper_files/paper/{year}/hash/{paper_hash}-Abstract-Conference.html"
                            else:
                                abstract_link = f"https://papers.nips.cc/paper_files/paper/{year}/hash/{paper_hash}-Abstract.html"

                            # Fetch abstract
                            abstract_text = await self.get_abstract(session, abstract_link, year)

                            papers.append({
                                'title': title,
                                'authors': authors,
                                'year': str(year),
                                'abstract': abstract_text,
                                'pdf_link': pdf_link,
                                'abstract_link': abstract_link
                            })
                    except Exception as e:
                        self.log(f"Error processing paper: {str(e)}")

            self.log(f"Year {year}: {len(papers)} papers saved in metadata.")
        except Exception as e:
            self.log(f"Error scraping year {year}: {str(e)}")

        return papers

    async def scrape_metadata_async(self):
        start_year = int(self.start_year.get())
        end_year = int(self.end_year.get())

        timeout = aiohttp.ClientTimeout(total=60)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_context)

        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            tasks = [self.scrape_year(session, year)
                     for year in range(start_year, end_year + 1)]
            results = await asyncio.gather(*tasks)

            all_papers = []
            for papers in results:
                all_papers.extend(papers)

            csv_path = Path('python_metadata.csv')
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f, fieldnames=['title', 'authors', 'year', 'abstract', 'pdf_link', 'abstract_link'])
                writer.writeheader()
                writer.writerows(all_papers)

            return all_papers

    async def download_pdfs_async(self):
        download_dir = Path(self.download_dir.get())
        download_dir.mkdir(exist_ok=True)

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_context)

        async with aiohttp.ClientSession(connector=connector) as session:
            total = len(self.metadata_list)
            for i, paper in enumerate(self.metadata_list, 1):
                title = ''.join(c if c.isalnum()
                               else '_' for c in paper['title'])
                path = download_dir / f"{title}_{paper['year']}.pdf"

                self.log(f"Downloading: {title}")
                success = await self.download_pdf(session, paper['pdf_link'], str(path))
                self.log(
                    f"{'Downloaded' if success else 'Failed to download'}: {title}")

                progress = (i / total) * 100
                self.progress_var.set(progress)

    def scrape_metadata(self):
        self.scrape_button.config(state=tk.DISABLED)
        self.download_button.config(state=tk.DISABLED)  # Disable download button during scraping
        self.tree.delete(*self.tree.get_children())
        self.progress_var.set(0)
        self.log_area.delete("1.0", tk.END)  # Clear log area

        def run_scrape():
            try:
                start_time = time.time()
                self.metadata_list = asyncio.run(self.scrape_metadata_async())  # Store the result

                # Update the treeview with the scraped data
                for paper in self.metadata_list:
                    self.tree.insert("", tk.END, values=(
                        paper['title'], paper['authors'], paper['year'], paper['abstract'], paper['pdf_link'],
                        paper['abstract_link']))

                end_time = time.time()
                elapsed_time = end_time - start_time
                self.log(f"Scraping complete in {elapsed_time:.2f} seconds.")
                self.download_button.config(state=tk.NORMAL)  # Enable download button after scraping

            except Exception as e:
                self.log(f"An error occurred: {e}")
            finally:
                self.scrape_button.config(state=tk.NORMAL)  # Re-enable the scrape button

        # Start the scraping process in a separate thread
        threading.Thread(target=run_scrape, daemon=True).start()

    def download_pdfs(self):
        self.download_button.config(state=tk.DISABLED)  # Disable the button during download

        def run_download():
            try:
                asyncio.run(self.download_pdfs_async())
                self.log("All PDFs downloaded.")
            except Exception as e:
                self.log(f"Download error: {e}")
            finally:
                self.download_button.config(state=tk.NORMAL)  # Re-enable after completion/error

        threading.Thread(target=run_download, daemon=True).start()


if __name__ == "__main__":
    app = NeurIPSScraper()
    app.mainloop()
