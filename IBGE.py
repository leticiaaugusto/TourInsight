"""
Web Scraping - Estimativas de População IBGE
Coleta dados do DOU publicados pelo IBGE e baixa o PDF de população dos municípios.

Fluxo:
  1. Acessa o site do IBGE
  2. Pesquisa "DOU" na barra de busca
  3. Clica no primeiro link dos resultados
  4. Navega direto para a aba Tabelas (?t=resultados)
  5. Clica no link do PDF e faz o download
  6. Salva o PDF na pasta de destino configurável
"""

import time
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# CONFIGURAÇÃO
PASTA_DESTINO = Path("dados_ibge")
URL_IBGE      = "https://www.ibge.gov.br"
TERMO_BUSCA   = "DOU"

# SETUP DO DRIVER
def criar_driver() -> webdriver.Chrome:
    opcoes = Options()
    #tirar esse comentário se quiser rodar sem abrir o navegador
    # opcoes.add_argument("--headless")
    opcoes.add_argument("--no-sandbox")
    opcoes.add_argument("--disable-dev-shm-usage")
    opcoes.add_argument("--disable-gpu")
    opcoes.add_argument("--window-size=1280,900")
    opcoes.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=opcoes)


# FUNÇÕES AUXILIARES
def aguardar_clicavel(driver, by, seletor, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, seletor))
    )

def aguardar_elemento(driver, by, seletor, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, seletor))
    )

def aguardar_resultados_busca(driver, timeout=20):
    """Aguarda a URL de busca e os resultados renderizarem via JS."""
    print("  Aguardando URL de busca...")
    WebDriverWait(driver, timeout).until(EC.url_contains("busca.html"))

    print("  Aguardando resultados renderizarem...")
    IGNORAR = {
        "GOVBR", "ACESSO À INFORMAÇÃO", "PARTICIPE", "LEGISLAÇÃO",
        "ÓRGÃOS DO GOVERNO", "Mudar para o modo de alto contraste", "Outros idiomas",
    }
    WebDriverWait(driver, timeout).until(
        lambda d: len([
            a for a in d.find_elements(By.TAG_NAME, "a")
            if a.text.strip()
            and a.text.strip() not in IGNORAR
            and "ibge.gov.br" in (a.get_attribute("href") or "")
            and "ibge.gov.br/#" not in (a.get_attribute("href") or "")
        ]) > 0
    )

def primeiro_link_resultado(driver):
    """Retorna o primeiro link de resultado ignorando links do cabeçalho."""
    IGNORAR = {
        "GOVBR", "ACESSO À INFORMAÇÃO", "PARTICIPE", "LEGISLAÇÃO",
        "ÓRGÃOS DO GOVERNO", "Mudar para o modo de alto contraste", "Outros idiomas",
    }
    for a in driver.find_elements(By.TAG_NAME, "a"):
        txt  = a.text.strip()
        href = a.get_attribute("href") or ""
        if (
            txt
            and txt not in IGNORAR
            and "ibge.gov.br" in href
            and "ibge.gov.br/#" not in href
            and href.rstrip("/") != URL_IBGE
        ):
            return a
    raise RuntimeError("Nenhum link de resultado encontrado.")

def url_para_tabelas(url_pagina: str) -> str:
    """
    Converte a URL da página principal para a URL da aba Tabelas.
    Ex: ...?edicao=37735  ->  ...?edicao=37735&t=resultados
    """
    if "t=resultados" in url_pagina:
        return url_pagina
    separador = "&" if "?" in url_pagina else "?"
    return url_pagina + separador + "t=resultados"

def baixar_pdf(url: str, destino: Path) -> Path:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    print(f"  Baixando: {url}")
    resposta = requests.get(url, headers=headers, timeout=60)
    resposta.raise_for_status()

    nome_arquivo = url.split("/")[-1]
    caminho = destino / nome_arquivo
    with open(caminho, "wb") as f:
        f.write(resposta.content)
    return caminho


# FLUXO PRINCIPAL DO WEB SCRAPING
def executar_scraping():
    PASTA_DESTINO.mkdir(parents=True, exist_ok=True)
    print(f"Pasta de destino: {PASTA_DESTINO.resolve()}\n")

    driver = criar_driver()

    try:
        # ── PASSO 1: Abre o site do IBGE 
        print("[1/5] Acessando o site do IBGE...")
        driver.get(URL_IBGE)
        time.sleep(3)

        # ── PASSO 2: Pesquisa "DOU" na barra de busca 
        print(f"[2/5] Pesquisando '{TERMO_BUSCA}' na barra de busca...")
        campo_busca = aguardar_clicavel(driver, By.ID, "mod-search-searchword")
        campo_busca.click()
        campo_busca.clear()
        campo_busca.send_keys(TERMO_BUSCA)
        time.sleep(1)
        campo_busca.send_keys(Keys.ENTER)

        # ── PASSO 3: Aguarda resultados e clica no primeiro link 
        print("[3/5] Aguardando e clicando no primeiro resultado...")
        aguardar_resultados_busca(driver, timeout=20)

        primeiro = primeiro_link_resultado(driver)
        url_resultado = primeiro.get_attribute("href")
        print(f"  Clicando em: '{primeiro.text.strip()[:30]}'")
        print(f"  URL: {url_resultado}")
        primeiro.click()
        time.sleep(3)

        # ── PASSO 4: Navega direto para a aba Tabelas 
        print("[4/5] Navegando para a aba 'Tabelas'...")

        # Pega a URL atual (pode ter aberto em nova aba)
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            print("  Trocou para nova aba.")
            time.sleep(2)

        url_atual = driver.current_url
        url_tabelas = url_para_tabelas(url_atual)
        print(f"  Acessando: {url_tabelas}")
        driver.get(url_tabelas)
        time.sleep(3)

        # ── PASSO 5: Captura o link do PDF e faz o download 
        print("[5/5] Localizando o link do PDF...")
        link_pdf_el = aguardar_elemento(
            driver, By.XPATH,
            "//a[contains(@href,'.pdf') and normalize-space(text())='PDF']"
        )
        url_pdf = link_pdf_el.get_attribute("href")
        print(f"  URL do PDF: {url_pdf}")

        arquivo = baixar_pdf(url_pdf, PASTA_DESTINO)
        print(f"\n✔ PDF salvo em: {arquivo.resolve()}")

    except Exception as erro:
        print(f"\n✘ Erro: {erro}")
        raise

    finally:
        driver.quit()
        print("Driver encerrado.")


# ─────────────────────────────────────────────
if __name__ == "__main__":
    executar_scraping()