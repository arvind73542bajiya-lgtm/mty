"""Personal AI chat -- poori tarah aapke PC par, internet ke bina.

Zaroorat: Ollama (https://ollama.com) install aur chalu ho. Python ki koi
extra library nahi chahiye.

    python chat.py                 # Modelfile se bana 'mera-ai' model
    python chat.py --model llama3.2

Chat ke andar commands:
    /yaad <baat>   -- koi baat hamesha ke liye yaad rakhwao (memory.json)
    /bhool         -- saari yaad ki hui baatein mita do
    /reset         -- is baatcheet ka history saaf karo
    /exit          -- band karo
"""

import argparse
import json
import pathlib
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
MEMORY_FILE = HERE / "memory.json"
DATA_DIR = HERE / "my_data"
MAX_DATA_CHARS = 20000  # chhote model ki context limit ke andar rehne ke liye


def load_memory():
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    return []


def save_memory(facts):
    MEMORY_FILE.write_text(json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8")


def load_my_data():
    parts = []
    for path in sorted(DATA_DIR.glob("*")):
        if path.suffix.lower() in (".txt", ".md"):
            parts.append(f"--- {path.name} ---\n{path.read_text(encoding='utf-8', errors='ignore')}")
    return "\n\n".join(parts)[:MAX_DATA_CHARS]


def build_system_prompt(facts):
    prompt = "Tum mera personal assistant ho. Hinglish mein chhote aur kaam ke jawab do."
    data = load_my_data()
    if data:
        prompt += "\n\nMeri apni files (sawal inse related ho to inhi ka use karo):\n" + data
    if facts:
        prompt += "\n\nMere baare mein yaad rakhne wali baatein:\n" + "\n".join(f"- {f}" for f in facts)
    return prompt


def chat(host, model, messages):
    """Ollama se jawab stream karke print karta hai aur poora jawab lautata hai."""
    req = urllib.request.Request(
        f"{host}/api/chat",
        data=json.dumps({"model": model, "messages": messages, "stream": True}).encode(),
        headers={"Content-Type": "application/json"},
    )
    reply = []
    with urllib.request.urlopen(req) as resp:
        for line in resp:
            if not line.strip():
                continue
            chunk = json.loads(line)
            if "error" in chunk:
                raise RuntimeError(chunk["error"])
            piece = chunk.get("message", {}).get("content", "")
            print(piece, end="", flush=True)
            reply.append(piece)
            if chunk.get("done"):
                break
    print()
    return "".join(reply)


def main():
    parser = argparse.ArgumentParser(description="Offline personal AI chat")
    parser.add_argument("--model", default="mera-ai")
    parser.add_argument("--host", default="http://localhost:11434")
    args = parser.parse_args()

    facts = load_memory()
    history = []
    print(f"Personal AI ({args.model}) taiyaar hai. /exit se band karein.\n")

    while True:
        try:
            text = input("Aap: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text == "/exit":
            break
        if text == "/reset":
            history = []
            print("History saaf.\n")
            continue
        if text == "/bhool":
            facts = []
            save_memory(facts)
            print("Saari yaadein mita di.\n")
            continue
        if text.startswith("/yaad "):
            facts.append(text[len("/yaad "):].strip())
            save_memory(facts)
            print("Yaad kar liya.\n")
            continue

        history.append({"role": "user", "content": text})
        messages = [{"role": "system", "content": build_system_prompt(facts)}] + history
        print("AI: ", end="", flush=True)
        try:
            reply = chat(args.host, args.model, messages)
        except urllib.error.URLError:
            print("\nOllama se connect nahi hua. Pehle Ollama chalu karein ('ollama serve').\n")
            history.pop()
            continue
        except RuntimeError as err:
            print(f"\nError: {err}\n(Kya model bana hai? 'ollama create mera-ai -f Modelfile' chalayein.)\n")
            history.pop()
            continue
        history.append({"role": "assistant", "content": reply})
        print()


if __name__ == "__main__":
    main()
