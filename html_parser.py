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


def get_docs(url):
    
    url = clean_url(url)
    response = requests.get(url)
    internal_links = []
    docs = []
    # 检查请求是否成功
    if response.status_code == 200:
        # 使用BeautifulSoup解析网页内容
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        docs.append(dict(page_content=text.strip(), metadata={"source": url}))
        
        # 查找所有的<a>标签
        all_links = soup.find_all('a')
        for a in all_links:
            if 'href' in a.attrs:
                if a['href'].startswith(url):
                    internal_links.append(a)
                elif a['href'].startswith("/"):
                    internal_links.append(url+a['href'])
        
        internal_links = list(set(internal_links))
        for link in internal_links:
            target_response = requests.get(link)
            target_content = target_response.content
            target_soup = BeautifulSoup(target_content, 'html.parser')
            target_text = target_soup.get_text()
            docs.append(dict(page_content=target_text.strip(), metadata={"source": link}))
        # 输出所有内部链接
    else:
        print(f"请求失败，状态码：{response.status_code}")

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
        self, page: "AsyncPage", browser: "AsyncBrowser", response: "AsyncResponse"
    ) -> str:
        """Asynchronously process the HTML content of the page."""
        from unstructured.partition.html import partition_html

        for selector in self.remove_selectors or []:
            elements = await page.locator(selector).all()
            for element in elements:
                if await element.is_visible():
                    await element.evaluate("element => element.remove()")

        page_source = await page.content()
        elements = partition_html(text=page_source)
        return "\n\n".join([str(el) for el in elements])


async def aload(urls, remove_selectors=["header", "footer"]):
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
            try:
                page = await browser.new_page()
                response = await page.goto(url)
                if response is None:
                    raise ValueError(
                        f"page.goto() returned None for url {url}")

                text = await evaluator.evaluate_async(page, browser, response)
                metadata = {"source": url}
                docs.append(dict(page_content=text.strip(), metadata=metadata))
            except Exception as e:
                logger.error(
                    f"Error fetching or processing {url}, exception: {e}"
                )
                raise e
        await browser.close()
    return docs
