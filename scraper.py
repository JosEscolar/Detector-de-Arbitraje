"""
FlipRadar - Scraper de oportunidades de arbitraje
Usa la API oficial de eBay Browse API (gratuita)
"""

import json
import os
import smtplib
import urllib.request
import urllib.parse
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ──────────────────────────────────────────────
# CONFIGURACIÓN — estos valores vienen de los
# "Secrets" de GitHub, no los escribas aquí
# ──────────────────────────────────────────────
EBAY_CLIENT_ID     = os.environ.get("EBAY_CLIENT_ID", "")
EBAY_CLIENT_SECRET = os.environ.get("EBAY_CLIENT_SECRET", "")
GMAIL_USER         = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
ALERT_EMAIL        = os.environ.get("ALERT_EMAIL", "")      # tu email donde recibes alertas
MIN_PROFIT_PCT     = int(os.environ.get("MIN_PROFIT_PCT", "30"))  # alerta si ganancia > 30%

# Categorías y palabras clave a rastrear
# Añade o quita las que quieras
SEARCH_TERMS = [
    {"query": "iPhone 13",             "category": "tech",         "buy_multiplier": 0.55},
    {"query": "iPhone 14",             "category": "tech",         "buy_multiplier": 0.55},
    {"query": "MacBook Air M1",        "category": "tech",         "buy_multiplier": 0.60},
    {"query": "PlayStation 5",         "category": "tech",         "buy_multiplier": 0.72},
    {"query": "Nintendo Switch OLED",  "category": "tech",         "buy_multiplier": 0.70},
    {"query": "AirPods Pro",           "category": "tech",         "buy_multiplier": 0.58},
    {"query": "Air Jordan 1 Retro",    "category": "sneakers",     "buy_multiplier": 0.45},
    {"query": "Yeezy Boost 350",       "category": "sneakers",     "buy_multiplier": 0.50},
    {"query": "Canada Goose jacket",   "category": "fashion",      "buy_multiplier": 0.55},
    {"query": "Lego Technic",          "category": "collectibles", "buy_multiplier": 0.60},
    {"query": "Rolex Submariner",      "category": "watches",      "buy_multiplier": 0.75},
    {"query": "DeLonghi Magnifica",    "category": "home",         "buy_multiplier": 0.52},
    {"query": "Sony Alpha A6000",      "category": "tech",         "buy_multiplier": 0.58},
    {"query": "Dyson V11",             "category": "home",         "buy_multiplier": 0.55},
]


def get_ebay_token():
    """Obtiene token OAuth de eBay"""
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    credentials = f"{EBAY_CLIENT_ID}:{EBAY_CLIENT_SECRET}"
    import base64
    encoded = base64.b64encode(credentials.encode()).decode()
    data = urllib.parse.urlencode({"grant_type": "client_credentials",
                                    "scope": "https://api.ebay.com/oauth/api_scope"}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Basic {encoded}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["access_token"]


def search_ebay(token, query, limit=10):
    """Busca productos en eBay y devuelve los resultados"""
    params = urllib.parse.urlencode({
        "q": query,
        "limit": limit,
        "filter": "conditions:{USED|VERY_GOOD|GOOD|ACCEPTABLE},buyingOptions:{FIXED_PRICE}",
        "sort": "price"
    })
    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?{params}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-EBAY-C-MARKETPLACE-ID", "EBAY_ES")
    req.add_header("X-EBAY-C-ENDUSERCTX", "contextualLocation=country=ES")
    try:
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
            return data.get("itemSummaries", [])
    except Exception as e:
        print(f"  Error buscando '{query}': {e}")
        return []


def find_opportunities(items, search_config):
    """
    Detecta oportunidades de arbitraje.
    Lógica: si el precio de compra estimado (precio eBay * multiplier)
    es significativamente menor que el precio medio de venta en eBay,
    hay margen de beneficio.
    """
    if not items:
        return []

    prices = []
    for item in items:
        try:
            price = float(item.get("price", {}).get("value", 0))
            if price > 0:
                prices.append(price)
        except (ValueError, TypeError):
            continue

    if len(prices) < 3:
        return []

    prices.sort()
    # Precio mediano de venta en eBay (eliminamos outliers)
    trimmed = prices[1:-1] if len(prices) > 4 else prices
    median_sell = sorted(trimmed)[len(trimmed) // 2]

    opportunities = []
    for item in items[:5]:  # analizamos los más baratos
        try:
            price = float(item.get("price", {}).get("value", 0))
            if price <= 0:
                continue

            # Estimación del precio de compra en Wallapop/Milanuncios
            # (suelen tener precios más bajos que eBay)
            estimated_buy_price = round(price * search_config["buy_multiplier"], 2)
            sell_price = round(median_sell, 2)

            if estimated_buy_price <= 0:
                continue

            profit_pct = round(((sell_price - estimated_buy_price) / estimated_buy_price) * 100)
            profit_eur = round(sell_price - estimated_buy_price, 2)

            if profit_pct >= MIN_PROFIT_PCT:
                image_url = ""
                images = item.get("thumbnailImages") or item.get("image")
                if isinstance(images, list) and images:
                    image_url = images[0].get("imageUrl", "")
                elif isinstance(images, dict):
                    image_url = images.get("imageUrl", "")

                opportunities.append({
                    "id": item.get("itemId", ""),
                    "name": item.get("title", "Sin título")[:80],
                    "category": search_config["category"],
                    "origin": "Wallapop/Milanuncios",
                    "destination": "eBay",
                    "buyPrice": estimated_buy_price,
                    "sellPrice": sell_price,
                    "profitPct": profit_pct,
                    "profitEur": profit_eur,
                    "condition": item.get("condition", "Usado"),
                    "ebayUrl": item.get("itemWebUrl", ""),
                    "imageUrl": image_url,
                    "foundAt": datetime.utcnow().isoformat(),
                    "isNew": True
                })
        except Exception as e:
            print(f"  Error procesando item: {e}")
            continue

    return opportunities


def send_alert_email(opportunities):
    """Envía email con las nuevas oportunidades detectadas"""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD or not ALERT_EMAIL:
        print("Email no configurado, saltando alerta.")
        return

    subject = f"FlipRadar — {len(opportunities)} nueva(s) oportunidad(es) detectada(s)"

    html_rows = ""
    for op in opportunities:
        html_rows += f"""
        <tr>
          <td style="padding:10px;border-bottom:1px solid #eee;">
            <strong>{op['name']}</strong><br>
            <span style="color:#888;font-size:13px;">{op['category']}</span>
          </td>
          <td style="padding:10px;border-bottom:1px solid #eee;text-align:center;">
            {op['buyPrice']}€ → {op['sellPrice']}€
          </td>
          <td style="padding:10px;border-bottom:1px solid #eee;text-align:center;">
            <span style="background:#d4edda;color:#155724;padding:3px 8px;border-radius:4px;font-weight:bold;">
              +{op['profitPct']}%
            </span>
          </td>
          <td style="padding:10px;border-bottom:1px solid #eee;text-align:center;">
            <a href="{op['ebayUrl']}" style="color:#0066cc;">Ver en eBay</a>
          </td>
        </tr>
        """

    html = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:700px;margin:auto;">
      <h2 style="color:#1a1a1a;">FlipRadar <span style="color:#22c55e;">·</span> Nuevas oportunidades</h2>
      <p style="color:#666;">{datetime.utcnow().strftime('%d/%m/%Y %H:%M')} UTC</p>
      <table style="width:100%;border-collapse:collapse;">
        <thead>
          <tr style="background:#f5f5f5;">
            <th style="padding:10px;text-align:left;">Producto</th>
            <th style="padding:10px;">Compra → Venta</th>
            <th style="padding:10px;">Ganancia</th>
            <th style="padding:10px;">Enlace</th>
          </tr>
        </thead>
        <tbody>{html_rows}</tbody>
      </table>
      <p style="color:#999;font-size:12px;margin-top:20px;">
        Precios de compra estimados. Verifica siempre antes de comprar.
        Descontando comisiones de eBay (~13%) y PayPal (~3.4%).
      </p>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = ALERT_EMAIL
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, ALERT_EMAIL, msg.as_string())
        print(f"Email enviado a {ALERT_EMAIL}")
    except Exception as e:
        print(f"Error enviando email: {e}")


def main():
    print(f"FlipRadar iniciado — {datetime.utcnow().isoformat()}")

    if not EBAY_CLIENT_ID or not EBAY_CLIENT_SECRET:
        print("ERROR: Faltan las credenciales de eBay (EBAY_CLIENT_ID / EBAY_CLIENT_SECRET)")
        print("Asegúrate de haberlas añadido en Settings > Secrets de tu repositorio GitHub.")
        return

    print("Obteniendo token de eBay...")
    try:
        token = get_ebay_token()
    except Exception as e:
        print(f"ERROR al obtener token: {e}")
        return

    all_opportunities = []
    new_opportunities = []

    # Cargar oportunidades previas para no repetir alertas
    prev_ids = set()
    try:
        with open("data/opportunities.json", "r", encoding="utf-8") as f:
            prev_data = json.load(f)
            prev_ids = {op["id"] for op in prev_data.get("opportunities", [])}
            # Guardamos las oportunidades antiguas (últimas 48h)
            all_opportunities = [
                op for op in prev_data.get("opportunities", [])
                if op.get("isNew") is False
            ]
    except FileNotFoundError:
        pass

    print(f"Rastreando {len(SEARCH_TERMS)} búsquedas...")
    for cfg in SEARCH_TERMS:
        print(f"  Buscando: {cfg['query']}")
        items = search_ebay(token, cfg["query"])
        opps = find_opportunities(items, cfg)
        for op in opps:
            if op["id"] not in prev_ids:
                new_opportunities.append(op)
                all_opportunities.append(op)
            prev_ids.add(op["id"])

    # Limitar a las 50 más recientes
    all_opportunities = sorted(
        all_opportunities,
        key=lambda x: x.get("foundAt", ""),
        reverse=True
    )[:50]

    # Marcar como no nuevas las ya vistas
    for op in all_opportunities:
        if op not in new_opportunities:
            op["isNew"] = False

    output = {
        "lastUpdated": datetime.utcnow().isoformat(),
        "totalFound": len(all_opportunities),
        "newCount": len(new_opportunities),
        "minProfitPct": MIN_PROFIT_PCT,
        "opportunities": all_opportunities
    }

    os.makedirs("data", exist_ok=True)
    with open("data/opportunities.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Guardadas {len(all_opportunities)} oportunidades ({len(new_opportunities)} nuevas)")

    if new_opportunities:
        print(f"Enviando alerta por email con {len(new_opportunities)} oportunidades nuevas...")
        send_alert_email(new_opportunities)
    else:
        print("Sin oportunidades nuevas, no se envía email.")

    print("Hecho.")


if __name__ == "__main__":
    main()
