# Mera Personal AI — sirf aapke PC par, sirf aapke liye

Ye AI poori tarah aapke computer par chalta hai. Internet ki zaroorat nahi,
koi data bahar nahi jaata, aur ye sirf aapki baatein aur aapki files jaanta hai.

## PC kaisa chahiye
| RAM | Model | Speed |
|-----|-------|-------|
| 8 GB | `llama3.2` (3B) | theek-thaak |
| 16 GB | `llama3.1:8b`, `qwen2.5:7b` | achha |
| Nvidia GPU (6 GB+) | 7B–8B models | kaafi tez |

## Step 1 — Ollama install karein
https://ollama.com/download se Windows / Mac / Linux ke liye install karein.
Terminal (Windows par PowerShell) kholkar check karein:

```
ollama --version
```

## Step 2 — Base model download karein (ek baar, ~2 GB)
```
ollama pull llama3.2
```

## Step 3 — Apna personal model banayein
`Modelfile` kholkar `SYSTEM` wale hisse mein apne baare mein likhein
(naam, kaam, kis bhasha mein jawab chahiye). Phir is folder mein:

```
ollama create mera-ai -f Modelfile
ollama run mera-ai
```

Bas — ab aapka apna AI chal raha hai.

## Step 4 — Apni files aur memory ke saath chat (optional)
`my_data/` folder mein apni `.txt` / `.md` files daal dijiye (farm ki details,
rates, notes). Phir:

```
python chat.py
```

Chat ke andar:
- `/yaad Mera dairy Jaipur mein hai` — baat hamesha ke liye yaad (`memory.json` mein)
- `/bhool` — saari yaadein mitao
- `/reset` — baatcheet ka history saaf
- `/exit` — band karo

## Aage kya kar sakte hain
- **Bahut saari files / PDFs se sawal-jawab:** [Open WebUI](https://github.com/open-webui/open-webui)
  ya [AnythingLLM](https://anythingllm.com) install karein — ye Ollama se judkar
  ChatGPT jaisa interface aur document upload dete hain, sab offline.
- **Model ko apni tarah train (fine-tune) karna:** apne 500–1000 sawal-jawab ke
  examples banakar [Unsloth](https://github.com/unslothai/unsloth) se LoRA
  fine-tune karein (Google Colab ka free GPU chal jaata hai), phir GGUF file ko
  `FROM ./mera-model.gguf` se Modelfile mein use karein. Zyadatar kaam ke liye
  iski zaroorat nahi padti — upar wala tareeka (system prompt + apni files)
  kaafi hai.

## Privacy
- Ollama sirf `localhost` par sunta hai, isliye doosre log ise use nahi kar sakte.
- `memory.json` aur `my_data/` sirf aapke PC par rehte hain. `memory.json` git
  mein commit nahi hota (`.gitignore`). `my_data/` mein personal files daalein
  to unhe bhi GitHub par push na karein.
