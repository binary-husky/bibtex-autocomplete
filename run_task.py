import importlib
import time
import inspect
import re
import os

proxies = {
    "http":  "socks5h://localhost:10084",
    "https": "socks5h://localhost:10084",
}

class ProxyNetworkActivate:
    """
    这段代码定义了一个名为ProxyNetworkActivate的空上下文管理器, 用于给一小段代码上代理
    """

    def __init__(self, task=None) -> None:
        self.task = task
        self.valid = True

    def __enter__(self):
        if not self.valid:
            return self
        if "no_proxy" in os.environ:
            os.environ.pop("no_proxy")
        if proxies is not None:
            if "http" in proxies:
                os.environ["HTTP_PROXY"] = proxies["http"]
            if "https" in proxies:
                os.environ["HTTPS_PROXY"] = proxies["https"]
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        os.environ["no_proxy"] = "*"
        if "HTTP_PROXY" in os.environ:
            os.environ.pop("HTTP_PROXY")
        if "HTTPS_PROXY" in os.environ:
            os.environ.pop("HTTPS_PROXY")
        return



from typing import List
from bibtexautocomplete.core import main

EMPTY_BIB = "main.bib"
with ProxyNetworkActivate():
    main([EMPTY_BIB,
    # "--only-query", "arxiv", # (choose from 'openalex', 'crossref', 'arxiv', 's2', 'unpaywall', 'dblp', 'researchr', 'hep')
    "-v",
    '--remove-fields', "url",
    '--remove-fields', "editor",
    '--remove-fields', "timestamp",
    '--remove-fields', "biburl",
    '--remove-fields', "bibsource",
    '--remove-fields', "publisher",
    '--remove-fields', "note"])

