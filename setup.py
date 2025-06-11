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
    install_requires=open("requirements.txt").read().splitlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    include_package_data=True
)
