import google.generativeai as genai
from core.config import GOOGLE_API_KEY

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def ask_llm(prompt: str) -> str:
    if not GOOGLE_API_KEY:
        return "repo,docker,cicd,security,deploy"
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction="You are an AI software architect evaluating engineering tasks."
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "repo,docker,cicd,security,deploy"