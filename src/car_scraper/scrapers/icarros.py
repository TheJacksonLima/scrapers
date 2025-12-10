import requests

API_URL = "https://www.icarros.com.br/comprar/ache/listaanuncios.ajax"


def get_page(brand, page):
    payload = {
        "pag": page,
        "qt": 24,
        "marca1": brand.lower(),
        "modelo1": "",
        "versao1": "",
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/javascript, */*",
        "X-Requested-With": "XMLHttpRequest"
    }

    r = requests.post(API_URL, data=payload, headers=headers)
    r.raise_for_status()
    return r.json()


# exemplo: listar todos os anúncios da Fiat
page = 1
while True:
    data = get_page("Fiat", page)
    anuncios = data.get("anuncios", [])

    if not anuncios:
        break

    for a in anuncios:
        print(a["codigo"], a["marca"], a["modelo"], a["preco"])

    if page >= data["totalPaginas"]:
        break

    page += 1
