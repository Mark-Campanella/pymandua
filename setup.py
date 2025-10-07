from setuptools import setup, find_packages

setup(
    name="pymandua",
    version="0.1.2",
    author="Marcos Henrique Maimoni Campanella",
    author_email="mhmcamp@gmail.com",
    description="Uma biblioteca para scraping com lógica fuzzy e conversão de HTML e conteúdos ao seu redor, lidando com reatividade do javascript para Markdown focado em LLMs. Adicionado com um pipeline RAG.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/seuusuario/web-scraper-with-ai",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.14.0,<5.0.0",
        "chromadb>=1.1.0,<2.0.0",
        "gradio>=5.49.0,<6.0.0",
        "langchain>=0.3.27,<0.4.0",
        "langchain-chroma>=0.2.6,<0.3.0",
        "langchain-community>=0.3.30,<0.4.0",
        "langchain-core>=0.3.78,<0.4.0",
        "langchain-google-genai>=2.1.12,<3.0.0",
        "langchain-ollama>=0.3.10,<0.4.0",
        "PyYAML>=6.0.3,<7.0.0",
        "rapidfuzz>=3.14.1,<4.0.0",
        "selenium>=4.36.0,<5.0.0",
        "selenium-stealth>=1.0.6,<2.0.0",
        "setuptools>=80.3.0,<81.0.0",
        "tqdm>=4.67.1,<5.0.0",
        "webdriver-manager>=4.0.2,<5.0.0",  
    ],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    include_package_data=True
)
