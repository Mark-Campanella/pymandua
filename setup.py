from setuptools import setup, find_packages

setup(
    name="pymandua",
    version="0.1.0",
    author="Marcos Henrique Maimoni Campanella",
    author_email="mhmcamp@gmail.com",
    description="Uma biblioteca para scraping com lógica fuzzy e conversão de HTML e conteúdos ao seu redor, lidando com reatividade do javascript para Markdown focado em LLMs.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/seuusuario/web-scraper-with-ai",
    packages=find_packages(),
    install_requires=[
    "attrs==25.3.0",
    "beautifulsoup4==4.13.4",
    "bs4==0.0.2",
    "certifi==2025.1.31",
    "cffi==1.17.1",
    "charset-normalizer==3.4.1",
    "dotenv==0.9.9",
    "h11==0.14.0",
    "idna==3.10",
    "logger==1.4",
    "numpy==2.2.5",
    "outcome==1.3.0.post0",
    "packaging==25.0",
    "pandas==2.2.3",
    "pycparser==2.22",
    "PySocks==1.7.1",
    "python-dateutil==2.9.0.post0",
    "python-dotenv==1.1.0",
    "pytz==2025.2",
    "RapidFuzz==3.13.0",
    "requests==2.32.3",
    "selenium==4.31.0",
    "selenium-stealth==1.0.6",
    "setuptools==80.3.0",
    "six==1.17.0",
    "sniffio==1.3.1",
    "sortedcontainers==2.4.0",
    "soupsieve==2.7",
    "trio==0.30.0",
    "trio-websocket==0.12.2",
    "typing_extensions==4.13.2",
    "tzdata==2025.2",
    "undetected-chromedriver==3.5.5",
    "urllib3==2.4.0",
    "webdriver-manager==4.0.2",
    "websocket-client==1.8.0",
    "websockets==15.0.1",
    "wsproto==1.2.0"
],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    include_package_data=True
)
