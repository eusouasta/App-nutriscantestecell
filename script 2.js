// NutriScan — frontend
// Captura/seleciona uma foto, envia pra função Python (/api/analyze)
// e renderiza o resultado no bottom sheet.

const cameraBtn = document.getElementById("cameraBtn");
const galleryBtn = document.getElementById("galleryBtn");
const cameraInput = document.getElementById("cameraInput");
const galleryInput = document.getElementById("galleryInput");

const viewfinder = document.getElementById("viewfinder");
const previewImg = document.getElementById("previewImg");
const viewfinderEmpty = document.getElementById("viewfinderEmpty");
const viewfinderLoading = document.getElementById("viewfinderLoading");
const loadingLabel = document.getElementById("loadingLabel");

const sheetBackdrop = document.getElementById("sheetBackdrop");
const resultSheet = document.getElementById("resultSheet");
const closeSheetBtn = document.getElementById("closeSheetBtn");
const scanAgainBtn = document.getElementById("scanAgainBtn");

const totalKcalEl = document.getElementById("totalKcal");
const totalProteinEl = document.getElementById("totalProtein");
const totalCarbsEl = document.getElementById("totalCarbs");
const totalFatEl = document.getElementById("totalFat");
const segProtein = document.getElementById("segProtein");
const segCarbs = document.getElementById("segCarbs");
const segFat = document.getElementById("segFat");
const itemsList = document.getElementById("itemsList");

const errorToast = document.getElementById("errorToast");

const DONUT_CIRC = 314; // 2 * pi * 50 (aprox, raio 50)

const MENSAGENS_LOADING = [
  "Identificando os alimentos…",
  "Calculando as calorias…",
  "Quase lá…",
];

cameraBtn.addEventListener("click", () => cameraInput.click());
galleryBtn.addEventListener("click", () => galleryInput.click());

cameraInput.addEventListener("change", (e) => handleArquivoSelecionado(e.target.files[0]));
galleryInput.addEventListener("change", (e) => handleArquivoSelecionado(e.target.files[0]));

closeSheetBtn.addEventListener("click", fecharSheet);
sheetBackdrop.addEventListener("click", fecharSheet);
scanAgainBtn.addEventListener("click", () => {
  fecharSheet();
  cameraInput.value = "";
  galleryInput.value = "";
});

async function handleArquivoSelecionado(file) {
  if (!file) return;

  const imagemBase64 = await lerComoBase64(file);

  previewImg.src = imagemBase64;
  previewImg.classList.remove("hidden");
  viewfinderEmpty.classList.add("hidden");
  viewfinderLoading.classList.remove("hidden");

  cicloDeMensagens();

  try {
    const resultado = await analisarImagem(imagemBase64);
    viewfinderLoading.classList.add("hidden");
    mostrarResultado(resultado);
  } catch (erro) {
    console.error(erro);
    viewfinderLoading.classList.add("hidden");
    mostrarErro(
      "Não consegui analisar essa foto. Tenta de novo em alguns segundos — o modelo às vezes demora pra 'esquentar'."
    );
  }
}

function lerComoBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

let intervaloMensagens = null;
function cicloDeMensagens() {
  let i = 0;
  loadingLabel.textContent = MENSAGENS_LOADING[0];
  clearInterval(intervaloMensagens);
  intervaloMensagens = setInterval(() => {
    i = (i + 1) % MENSAGENS_LOADING.length;
    loadingLabel.textContent = MENSAGENS_LOADING[i];
  }, 2200);
}

async function analisarImagem(imagemBase64) {
  const resp = await fetch("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ imagem: imagemBase64 }),
  });

  clearInterval(intervaloMensagens);

  const data = await resp.json();
  if (!resp.ok || data.erro) {
    throw new Error(data.erro || "Erro desconhecido");
  }
  return data;
}

function mostrarResultado(resultado) {
  const { itens, total } = resultado;

  totalKcalEl.textContent = "0";
  animarNumero(totalKcalEl, total.kcal);
  totalProteinEl.textContent = `${total.proteina_g}g`;
  totalCarbsEl.textContent = `${total.carboidrato_g}g`;
  totalFatEl.textContent = `${total.gordura_g}g`;

  // Donut: cada macro em gramas vira "peso calórico" pra proporção visual
  const kcalProteina = total.proteina_g * 4;
  const kcalCarbo = total.carboidrato_g * 4;
  const kcalGordura = total.gordura_g * 9;
  const somaKcalMacros = kcalProteina + kcalCarbo + kcalGordura || 1;

  const pctProteina = kcalProteina / somaKcalMacros;
  const pctCarbo = kcalCarbo / somaKcalMacros;
  const pctGordura = kcalGordura / somaKcalMacros;

  const offProteina = DONUT_CIRC * (1 - pctProteina);
  const offCarbo = DONUT_CIRC * (1 - pctCarbo);
  const offGordura = DONUT_CIRC * (1 - pctGordura);

  // posiciona os segmentos em sequência ao redor do círculo
  segProtein.style.strokeDashoffset = String(offProteina);
  segProtein.style.transform = "rotate(0deg)";
  segProtein.style.transformOrigin = "60px 60px";

  segCarbs.style.strokeDashoffset = String(offCarbo);
  segCarbs.style.transform = `rotate(${pctProteina * 360}deg)`;
  segCarbs.style.transformOrigin = "60px 60px";

  segFat.style.strokeDashoffset = String(offGordura);
  segFat.style.transform = `rotate(${(pctProteina + pctCarbo) * 360}deg)`;
  segFat.style.transformOrigin = "60px 60px";

  itemsList.innerHTML = "";
  itens.forEach((item) => {
    const el = document.createElement("div");
    el.className = "food-item";
    el.innerHTML = `
      <div class="food-emoji">${item.emoji}</div>
      <div class="food-info">
        <div class="food-name">${item.nome}</div>
        <div class="food-confidence">${item.confianca}% de confiança</div>
      </div>
      <div class="food-kcal">${item.kcal} kcal</div>
    `;
    itemsList.appendChild(el);
  });

  sheetBackdrop.classList.remove("hidden");
  resultSheet.classList.remove("hidden");
}

function animarNumero(el, valorFinal) {
  const duracao = 700;
  const inicio = performance.now();
  function passo(agora) {
    const progresso = Math.min(1, (agora - inicio) / duracao);
    el.textContent = Math.round(progresso * valorFinal);
    if (progresso < 1) requestAnimationFrame(passo);
  }
  requestAnimationFrame(passo);
}

function fecharSheet() {
  sheetBackdrop.classList.add("hidden");
  resultSheet.classList.add("hidden");
}

function mostrarErro(mensagem) {
  errorToast.textContent = mensagem;
  errorToast.classList.remove("hidden");
  setTimeout(() => errorToast.classList.add("hidden"), 4200);
}
