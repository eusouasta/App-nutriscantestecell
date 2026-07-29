# 🌿 NutriScan

App mobile-first que tira/recebe uma foto do seu prato ou lanche, identifica
os alimentos e mostra uma estimativa de calorias e macronutrientes — numa
telinha estilo "bottom sheet" com anel de macros.

## Arquitetura

- **Frontend** (`index.html`, `style.css`, `script.js`): puro HTML/CSS/JS,
  sem framework. Cuida da câmera/upload, do visual e da animação dos
  resultados.
- **Backend** (`api/analyze.py` + `api/nutrition_data.py`): função
  serverless em **Python**, rodando na Vercel.
  - `analyze.py` recebe a foto, manda pra API de inferência do Hugging
    Face (modelo treinado no dataset Food-101, que reconhece 101 tipos de
    prato) e devolve o resultado processado.
  - `nutrition_data.py` é a camada de lógica/dados: tem uma base própria
    com calorias e macros (proteína, carboidrato, gordura) por porção
    típica de cada um dos 101 pratos, e a função `montar_resultado()` faz
    a agregação (filtra ruído, remove duplicata, soma o total do "prato").

Fluxo completo: **foto → JS → função Python → modelo de IA → base
nutricional Python → JSON → JS renderiza**.

## Rodar localmente

Esse projeto tem frontend estático **e** uma função Python, então o jeito
mais fácil de testar localmente é com a CLI da Vercel (ela sobe os dois
juntos):

```bash
npm install -g vercel
cd nutriscan
vercel dev
```

Acesse a URL que aparecer no terminal (geralmente `http://localhost:3000`).

> Se preferir não instalar a CLI, dá pra subir só o frontend com
> `python3 -m http.server 8000`, mas aí a análise de foto não vai
> funcionar (precisa da função Python rodando).

## Deploy no Vercel

1. Suba o projeto pro GitHub:
   ```bash
   git init
   git add .
   git commit -m "NutriScan"
   git branch -M main
   git remote add origin https://github.com/SEU-USUARIO/nutriscan.git
   git push -u origin main
   ```
2. Em [vercel.com](https://vercel.com), clique em **Add New → Project** e
   selecione o repositório.
3. A Vercel detecta sozinha o front (estático) e o back (`api/*.py` como
   Python Function) — não precisa configurar build command nem nada.
4. (Recomendado) Adicione a variável de ambiente `HF_API_TOKEN`:
   - Crie uma conta grátis em [huggingface.co](https://huggingface.co)
   - Gere um token em **Settings → Access Tokens** (tipo "Read")
   - No painel do projeto na Vercel: **Settings → Environment Variables**
     → adicione `HF_API_TOKEN` com o valor do token
   - Sem isso o app ainda funciona, mas a API pública do Hugging Face tem
     um limite de requisições bem mais baixo e pode recusar pedidos em
     uso mais intenso.
5. Clique em **Deploy**. Em ~1 minuto você tem uma URL tipo
   `nutriscan.vercel.app`.

## Limitações importantes (seja honesto com quem for usar)

- As calorias e macros são **estimativas por porção típica**, não medições
  reais do prato da pessoa — tamanho da porção, ingredientes extras e modo
  de preparo mudam o valor real.
- O modelo reconhece as 101 categorias do dataset Food-101 (a lista está
  em `api/nutrition_data.py`). Comidas fora dessa lista caem numa
  estimativa genérica.
- Isso é uma ferramenta de referência rápida, não um substituto de
  orientação nutricional profissional.

## Personalizações rápidas

- **Cores**: variáveis no topo do `style.css` (`:root`).
- **Base de calorias**: edite os valores em `api/nutrition_data.py` —
  cada linha da `TABELA_NUTRICIONAL` é `label_do_modelo: (nome, emoji,
  kcal, proteína, carboidrato, gordura)`.
- **Confiança mínima / nº de itens detectados por foto**: constantes
  `CONFIANCA_MINIMA` e `MAX_ITENS` dentro de `montar_resultado()` em
  `nutrition_data.py`.

## Estrutura do projeto

```
nutriscan/
├── index.html
├── style.css
├── script.js
├── vercel.json
├── requirements.txt
├── README.md
└── api/
    ├── analyze.py          # função serverless Python
    └── nutrition_data.py   # base nutricional + lógica de agregação
```
