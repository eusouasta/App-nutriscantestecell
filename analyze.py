"""
api/analyze.py
===============
Função serverless Python rodando na Vercel.

Fluxo:
  1. Recebe uma imagem em base64 do frontend (JS)
  2. Envia pra API de inferência do Hugging Face, que roda um modelo de
     classificação de imagens treinado no dataset Food-101 (101 tipos de
     prato)
  3. Passa o resultado bruto do modelo pra camada de lógica em Python
     (nutrition_data.py), que cruza cada item com calorias/macros e agrega
     o total do prato
  4. Devolve tudo pro frontend em JSON

Variável de ambiente opcional:
  HF_API_TOKEN — token gratuito do Hugging Face (https://huggingface.co/settings/tokens)
  Sem token, a API pública do Hugging Face funciona mas com limite de uso
  bem mais baixo (pode dar erro 429 em uso intenso).
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import base64
import urllib.request
import urllib.error

from nutrition_data import montar_resultado

HF_MODEL_URL = "https://api-inference.huggingface.co/models/nateraw/food"


def classificar_imagem(imagem_bytes: bytes) -> list[dict]:
    """Chama a API de inferência do Hugging Face e retorna a lista de predições."""
    token = os.environ.get("HF_API_TOKEN", "")
    headers = {"Content-Type": "application/octet-stream"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(
        HF_MODEL_URL, data=imagem_bytes, headers=headers, method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            corpo = resp.read()
            resultado = json.loads(corpo)
    except urllib.error.HTTPError as e:
        detalhe = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Erro do modelo ({e.code}): {detalhe}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Falha de conexão com o modelo: {e.reason}")

    # A API pode devolver {"error": "..."} enquanto o modelo ainda está
    # "esquentando" (cold start) — nesse caso repassamos como erro tratável.
    if isinstance(resultado, dict) and "error" in resultado:
        raise RuntimeError(resultado["error"])

    # Formato esperado: [{"label": "pizza", "score": 0.87}, ...]
    return resultado


class handler(BaseHTTPRequestHandler):
    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def do_POST(self):
        try:
            tamanho = int(self.headers.get("Content-Length", 0))
            corpo_bruto = self.rfile.read(tamanho)
            payload = json.loads(corpo_bruto)

            imagem_b64 = payload.get("imagem", "")
            if "," in imagem_b64:
                # remove prefixo tipo "data:image/jpeg;base64,"
                imagem_b64 = imagem_b64.split(",", 1)[1]

            imagem_bytes = base64.b64decode(imagem_b64)

            predicoes = classificar_imagem(imagem_bytes)
            resultado = montar_resultado(predicoes)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(resultado).encode("utf-8"))

        except Exception as erro:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self._cors_headers()
            self.end_headers()
            self.wfile.write(
                json.dumps({"erro": str(erro)}).encode("utf-8")
            )
