# LangSmith: tracing de las llamadas al LLM

LangSmith es la herramienta de observabilidad de LangChain. Registra cada
llamada al LLM (prompt, contexto inyectado, respuesta, latencia, tokens) para
poder inspeccionarla despues en una UI web. Sirve para debuggear el RAG: ver
que contexto se recupero realmente y que le llego al modelo.

## 1. Crear cuenta y API key

1. Anda a https://smith.langchain.com y crea una cuenta (podes usar tu cuenta
   de Google/GitHub).
2. En **Settings > API Keys** genera una nueva key (empieza con `lsv2_pt_...`).

## 2. Configurar las variables de entorno

En `.env` completa:

```bash
LANGSMITH_TRACING=true
LANGSMITH_API_KEY="lsv2_pt_tu_key_aca"
LANGSMITH_PROJECT="rag-pdf-demo"
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
```

`LANGSMITH_PROJECT` es solo un nombre para agrupar las traces en la UI; si no
existe, LangSmith lo crea automaticamente en la primera llamada.

Si dejas el placeholder del `.env.example` vas a ver este error en cada
pregunta (la respuesta igual se genera, el que falla es el envio de traces):

```
Failed to multipart ingest runs: ... 403 Client Error: Forbidden
```

## 3. No hace falta codigo extra

`shared/config.py` llama a `load_dotenv()` al importarse, y tanto `main.py`
como `rag_services.py` lo importan antes de usar `langchain_*`. Con eso
alcanza: LangChain lee `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`,
`LANGSMITH_PROJECT` y `LANGSMITH_ENDPOINT` directamente de las variables de
entorno del proceso y envia las traces solo. No hay que instanciar ningun
cliente ni decorar funciones a mano.

Las constantes `LANGSMITH_*` que expone `shared/config.py` son opcionales —
quedan como referencia de que variables existen, pero el tracing funciona
igual sin leerlas desde el codigo.

## 4. Instalar la dependencia

El paquete `langsmith` viene como dependencia transitiva de `langchain-core`,
que si esta en `requirements.txt`, asi que se instala solo con el resto. Si
alguna vez tira `ModuleNotFoundError: langsmith`:

```bash
./.venv/bin/pip install langsmith
```

## 5. Ver las traces

Corre `./run.sh` y hace una pregunta. Despues entra a
https://smith.langchain.com, elegi el proyecto (`rag-pdf-demo` o el nombre que
hayas puesto en `LANGSMITH_PROJECT`) y vas a ver cada llamada al LLM con el
prompt completo, el contexto recuperado y la respuesta generada.

Para apagar el tracing sin borrar la key, pone `LANGSMITH_TRACING=false`.
