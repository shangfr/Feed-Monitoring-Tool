# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 16:01:08 2023

@author: shangfr
"""
import requests
from bs4 import BeautifulSoup
import logging
from playwright.async_api import async_playwright
from typing import TYPE_CHECKING, List, Optional
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from playwright.async_api import Browser as AsyncBrowser
    from playwright.async_api import Page as AsyncPage
    from playwright.async_api import Response as AsyncResponse


def clean_url(url):
    # 解析URL
    parsed_url = urlparse(url)
    parsed_url = parsed_url._replace(query='', fragment='')

    if parsed_url.scheme not in ["https", "http"]:
        scheme = 'https'
    else:
        scheme = parsed_url.scheme

    cleaned_url = urljoin(scheme + '://' +
                          parsed_url.netloc, parsed_url.path)
    return cleaned_url.rstrip('/')

def parser_links(url, content):
    
    soup = BeautifulSoup(content, "html.parser")
    #url = soup.find("base")["href"]
    text = soup.get_text()
    all_links = soup.find_all('a')
    # 查找所有的<a>标签
    internal_links = []
    for a in all_links:
        if 'href' in a.attrs:
            if a['href'].startswith(url):
                internal_links.append(a)
            elif a['href'].startswith("/"):
                internal_links.append(url+a['href'])

    return text,list(set(internal_links))

def get_web_content(url):
    url = clean_url(url)
    response = requests.get(url)
    if response.status_code == 200:
        content = response.text
        return parser_links(url, content)
    else:
        print(f"请求失败，状态码：{response.status_code}")
        return None,None
   
    
def get_docs(url,inner=False):
    
    docs = []
    text,internal_links = get_web_content(url)
    if text is not None:
        docs.append(dict(page_content=text.strip(), metadata={"source": url}))
        if inner:
            if len(internal_links)>5:
                internal_links = internal_links[:5]
            for link in internal_links:
                target_text, _ = get_web_content(url)
                docs.append(dict(page_content=target_text.strip(), metadata={"source": link}))

    return docs


class UnstructuredHtmlEvaluator():
    """Evaluates the page HTML content using the `unstructured` library."""

    def __init__(self, remove_selectors: Optional[List[str]] = None):
        """Initialize UnstructuredHtmlEvaluator."""
        try:
            import unstructured  # noqa:F401
        except ImportError:
            raise ImportError(
                "unstructured package not found, please install it with "
                "`pip install unstructured`"
            )

        self.remove_selectors = remove_selectors

    async def evaluate_async(
        self, page: "AsyncPage", browser: "AsyncBrowser", response: "AsyncResponse", url:str) -> (str,list):
        """Asynchronously process the HTML content of the page."""
        from unstructured.partition.html import partition_html

        for selector in self.remove_selectors or []:
            elements = await page.locator(selector).all()
            for element in elements:
                if await element.is_visible():
                    await element.evaluate("element => element.remove()")

        page_source = await page.content()
        return parser_links(url, page_source)
        
        #elements = partition_html(text=page_source)
        #return "\n\n".join([str(el) for el in elements])


async def aload(urls, remove_selectors=[], inner=False):
    """Load the specified URLs with Playwright and create Documents asynchronously.
    Use this function when in a jupyter notebook environment.

    Returns:
        List[Document]: A list of Document instances with loaded content.
    """

    docs = list()
    evaluator = UnstructuredHtmlEvaluator(remove_selectors)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for url in urls:
            url = clean_url(url)
            try:
                page = await browser.new_page()
                response = await page.goto(url)
                if response is None:
                    raise ValueError(
                        f"page.goto() returned None for url {url}")

                text,internal_links = await evaluator.evaluate_async(page, browser, response, url)
                metadata = {"source": url}
                docs.append(dict(page_content=text.strip(), metadata=metadata))
                
                if inner:
                    evaluator = UnstructuredHtmlEvaluator(["header", "footer"])
                    if len(internal_links)>5:
                        internal_links = internal_links[:5]
                    for link in internal_links:
                        response = await page.goto(link)
                        if response is None:
                            raise ValueError(
                                f"page.goto() returned None for url {link }")
    
                        text,_ = await evaluator.evaluate_async(page, browser, response, link)
                        metadata = {"source": link }
                        docs.append(dict(page_content=text.strip(), metadata=metadata))
            except Exception as e:
                logger.error(
                    f"Error fetching or processing {url}, exception: {e}"
                )
                raise e
        await browser.close()
    return docs
