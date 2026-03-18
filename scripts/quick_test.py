"""Teste rápido: na raiz do projeto → python scripts/quick_test.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from llm_config import setup_llm
from backend import normalize_dados_estruturados, validate_file


def main():
    print("1. Imports OK")

    llm = setup_llm()
    r = llm.invoke("Responda uma palavra: ok")
    text = r.content if hasattr(r, "content") else str(r)
    print(f"2. LLM: {text[:80]!r}")

    v = validate_file(b"hello" * 100, "x.pdf")
    assert v["valid"], v
    v2 = validate_file(b"", "x.pdf")
    assert not v2["valid"]
    print("3. validate_file OK")

    d = normalize_dados_estruturados({"Nome": "João", "email": "a@b.com"})
    assert d["nome"] == "João" and d["email"] == "a@b.com"
    print("4. normalize_dados_estruturados OK")

    print("--- OK ---")


if __name__ == "__main__":
    main()
