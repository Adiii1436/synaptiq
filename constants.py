from pathlib import Path

MODEL_DIR = Path("models")
EMBED_MODEL_NAME = "all-MiniLM-L6-v2" 
CHAT_MODEL_FILENAME = "Llama-3.2-3B-Instruct-Q4_K_M.gguf"
CHAT_MODEL_URL = "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
CHAT_MODEL_PATH = MODEL_DIR / CHAT_MODEL_FILENAME