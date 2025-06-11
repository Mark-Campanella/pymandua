# Web Scraper with AI — HTML to Markdown for LLMs

Este projeto é uma biblioteca Python que realiza Web Scraping inteligente com lógica fuzzy e converte páginas HTML em Markdown simplificado, ideal para Large Language Models (LLMs) e análises posteriores.

---

## 🚀 Funcionalidades

- Web scraping automatizado com Selenium e suporte a páginas dinâmicas
- Conversão precisa de HTML para Markdown limpo com suporte a:
  - Títulos, parágrafos, listas, links, tabelas, blocos de código, entre outros
- Lógica de busca fuzzy para identificar se o conteúdo da página e páginas ao seu redor está relacionado às palavras-chave desejadas
- Mecanismo de retorno automático de páginas visitadas
- Pode ser utilizado como biblioteca ou como script principal

---

## 🧠 Como Funciona

### 🔍 Web Scraping com Selenium

O módulo utiliza o `undetected-chromedriver` e `selenium-stealth` com o ``selenium`` para navegar por páginas web, extrair conteúdos e retroceder após a coleta. O conteúdo das páginas é tratado pelo `BeautifulSoup` e convertido em Markdown por um parser customizado.

### 🧪 Lógica Fuzzy

A comparação entre o conteúdo da página e as palavras-chave fornecidas é feita com `RapidFuzz`, utilizando similaridade textual (ex: token_sort_ratio). Isso permite validar se a página realmente trata do tema buscado, mesmo que o texto não seja exatamente igual.

---

## 🖼️ Fluxo do Processo


<img src="midia/flowchart.png"></img>


### 🧪 Instalação

**Com pip**
```bash
pip install pymandua
```


**Ou alternativamente**
1. **Clone o repositório:**
```bash
git clone https://github.com/Mark-Campanella/pymandua.git
cd pymandua
```

2. **Crie um ambiente virtual e ative:**
```bash
python -m venv env
source env/bin/activate  # Linux/macOS
env\Scripts\activate     # Windows
```

3. **Instale as dependências:**
``` bash
pip install -r requirements.txt
```


### 🔧 Uso como script
```python
from pymandua import to_mkd

result = to_mkd(
    urls="https://pt.wikipedia.org/wiki/Luís_XIV_de_França",
    keywords=["Luís XIV", "França", "Rei Sol"],
    output_path=r"projeto/output",
    wait=2,
    threshold=90
)
print(result)

```

**Uso como CLI**
```bash
to-mkd --urls "https://exemplo.com" --keywords "palavra1,palavra2" --output "saida.md" --wait 2 --threshold 95
```

### 🧩 Estrutura do Projeto
```
├── pymandua/              # Módulo principal
│   ├── interface.py       # Interface principal do conversor
│   ├── converter.py       # Conversor de HTML para Markdown
│   ├── gatherer.py        # Web scraper e parser de conteúdo
│   ├── driver.py          # Inicializador de driver para o selenium
│   ├── crawler.py         # Web crawler e parser de conteúdo
│   ├── treater.py         # Prepara para o cleaner
│   ├── aggregator.py      # Agrega os diversos HTMLs resultantes em um para ser convertido
│   ├── cleaner.py         # Parser e limpador de conteúdo não necessário
├── output/                # Arquivos .mkd gerados
├── requirements.txt       # Dependências
├── main.py                # Exemplo de uso
```

**📚 Referências**
- [Selenium Docs](https://selenium-python.readthedocs.io)
- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [RapidFuzz Docs](maxbachmann.github.io/RapidFuzz/)
- [RapidFuzz Examples](https://github.com/rapidfuzz/RapidFuzz#examples)
