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

En `1-rag/.env` completa:

```bash
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_pt_tu_key_aca
LANGSMITH_PROJECT=rag-pdf-demo
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

`LANGSMITH_PROJECT` es solo un nombre para agrupar las traces en la UI; si no
existe, LangSmith lo crea automaticamente en la primera llamada.

## 3. No hace falta codigo extra

`main.py` ya llama a `load_dotenv()` al principio del archivo, antes de
importar `langchain_*`. Con eso alcanza: LangChain lee `LANGSMITH_TRACING`,
`LANGSMITH_API_KEY`, `LANGSMITH_PROJECT` y `LANGSMITH_ENDPOINT` directamente
de las variables de entorno del proceso y envia las traces solo. No hay que
instanciar ningun cliente ni decorar funciones a mano.

Las lineas que leen esas variables en `main.py` (`LANGSMITH_TRACING = os.getenv(...)`,
etc.) son opcionales — quedan como referencia de que variables existen, pero
no son necesarias para que el tracing funcione.

## 4. Instalar la dependencia

El paquete `langsmith` viene como dependencia transitiva de `langchain_core`,
asi que si ya podes correr `main.py` deberia estar instalado. Si tira
`ModuleNotFoundError: langsmith`, instalalo a mano:

```bash
pip install langsmith
```

(Tambien conviene agregarlo a `requirements.txt`, que hoy no lista ningun
paquete de `langchain`.)

## 5. Ver las traces

Corre `python main.py` normalmente y hace una pregunta. Despues entra a
https://smith.langchain.com, elegi el proyecto (`rag-pdf-demo` u otro nombre
que hayas puesto en `LANGSMITH_PROJECT`) y vas a ver cada llamada al LLM con
el prompt completo, el contexto recuperado y la respuesta generada.

Para apagar el tracing sin borrar la key, poné `LANGSMITH_TRACING=false`.
