# Web Scraping - Estimativas de População IBGE

Automação para coleta de dados de Estimativas de População publicadas no Diário Oficial da União (DOU) pelo IBGE. O script simula a navegação de um usuário no site do IBGE, realiza uma busca, localiza a publicação e faz o download do PDF com os dados populacionais por município.

---

## Pré-requisitos

- Python 3.10 ou superior
- Google Chrome instalado
- ChromeDriver compatível com a versão do seu Chrome

### Criando o ambiente virtual e instalando as dependências

Antes de rodar o projeto, é recomendado criar um ambiente virtual (venv) para isolar as dependências e evitar conflitos com outros projetos Python na sua máquina.

```bash
# Cria o ambiente virtual
python -m venv .venv

# Ativa o ambiente virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instala as dependências dentro da venv
pip install -r requirements.txt
```

Com a venv ativada, todas as bibliotecas serão instaladas de forma isolada. Lembre de sempre ativá-la antes de rodar o script.

### Verificando a versão do Chrome

Acesse `chrome://settings/help` no Chrome e confira a versão. O ChromeDriver deve ser da mesma versão principal.

Download do ChromeDriver: https://googlechromelabs.github.io/chrome-for-testing/

---

## Estrutura do projeto

```
.
├── IBGE.py              # Script principal de web scraping
├── requirements.txt     # Dependências do projeto
├── README.md            # Este arquivo
└── dados_ibge/          # Pasta criada automaticamente para salvar o PDF
```

---

## Como usar

```bash
python IBGE.py
```

O script vai:

1. Abrir o Chrome e acessar `ibge.gov.br`
2. Pesquisar **"DOU"** na barra de busca
3. Clicar no primeiro resultado encontrado
4. Navegar para a aba **Tabelas**
5. Localizar o link do PDF e fazer o download
6. Salvar o arquivo na pasta `dados_ibge/`

---

## Configuração

No topo do arquivo `IBGE.py` há três variáveis configuráveis:

| Variável | Padrão | Descrição |
|---|---|---|
| `PASTA_DESTINO` | `dados_ibge` | Pasta onde o PDF será salvo |
| `URL_IBGE` | `https://www.ibge.gov.br` | URL base do IBGE |
| `TERMO_BUSCA` | `DOU` | Termo pesquisado na barra de busca |

---

## Executar sem abrir janela (modo headless)

Descomente a linha abaixo dentro da função `criar_driver()` no arquivo `IBGE.py`:

```python
# opcoes.add_argument("--headless")
```

---

## Dependências

| Biblioteca | Versão | Uso |
|---|---|---|
| `selenium` | 4.21.0 | Automação do navegador |
| `requests` | 2.32.3 | Download do PDF via HTTP |

---

## Contexto

Este projeto foi desenvolvido como parte de um trabalho acadêmico sobre automação de coleta de dados públicos. Os dados de população municipal publicados no DOU pelo IBGE podem ser utilizados em análises de mercado — por exemplo, no setor de turismo, onde a densidade populacional por estado indica concentração de potenciais clientes e influencia a criação de pacotes e estratégias de precificação.
