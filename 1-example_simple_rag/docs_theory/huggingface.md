# Hugging Face: token de acceso

Este ejercicio usa Hugging Face para dos cosas distintas:

1. **Embeddings (paso 2)**: baja el modelo `EMBEDDING_MODEL` del Hub y lo
   corre **local**, en tu maquina. Sin token funciona, pero con rate limit y
   descargas mas lentas (por eso el warning `You are sending unauthenticated
   requests to the HF Hub`).
2. **Generacion (paso 4)**: llama al modelo `HF_MODEL_ID` por la API de
   Inference Providers. Aca el token **si es obligatorio**; sin el, 401.

## 1. Sacar el token

1. Entra o crea la cuenta en https://huggingface.co
2. Avatar (arriba a la derecha) > **Settings**
3. Menu izquierdo > **Access Tokens**, o directo
   https://huggingface.co/settings/tokens
4. **Create new token**
5. Tipo **Read** (alcanza para inferencia y para bajar modelos). Si elegis
   *Fine-grained*, marca al menos "Make calls to Inference Providers".
6. Nombre, por ejemplo `ai-lab-rag` > **Create token**
7. Copiala ahi mismo: se muestra **una sola vez**. Empieza con `hf_` y son
   ~37 caracteres.

## 2. Configurar las variables de entorno

En `.env`:

```bash
HUGGINGFACEHUB_API_TOKEN="hf_tu_token_real_aca"
HF_TOKEN="hf_tu_token_real_aca"
HF_MODEL_ID="Qwen/Qwen2.5-7B-Instruct"
EMBEDDING_MODEL="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

Conviene definir las dos variables del token con el mismo valor:
`langchain_huggingface` lee `HUGGINGFACEHUB_API_TOKEN`, pero `huggingface_hub`
(el que descarga los embeddings) lee `HF_TOKEN`.

El `.env` esta en `.gitignore`, asi que el token no se commitea. Si alguna vez
se te escapa a un commit, revocala en la misma pagina de Access Tokens y
genera otra.

## 3. Elegir el `HF_MODEL_ID`

No todos los modelos del Hub estan servidos por la API de inferencia. Buscalos
filtrando en https://huggingface.co/models?inference_provider=all y pega el id
exacto, con el formato `organizacion/modelo`.

## 4. Errores tipicos

| Error | Causa |
|---|---|
| `401 Unauthorized` en `router.huggingface.co/v1/chat/completions` | El token falta, esta mal copiado o quedo el placeholder `hf_TF...` del `.env.example` |
| `404` sobre el repo del modelo | El `HF_MODEL_ID` no existe o no esta servido por Inference Providers |
| `Warning: ... unauthenticated requests to the HF Hub` | Falta `HF_TOKEN` (solo afecta la descarga de embeddings, no rompe) |
| `402` / quota | Te quedaste sin credito mensual gratuito de inferencia |

