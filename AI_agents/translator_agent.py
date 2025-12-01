import ollama
from langdetect import detect
import PyPDF2
import os

def read_pdf(path):
    text = ""
    with open(path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def classify_intent(user_input):
    lower = user_input.lower()

    if user_input.endswith(".pdf") and os.path.exists(user_input):
        return "pdf"

    if any(word in lower for word in ["translate", "translation"]):
        return "translate"

    if len(user_input.split()) > 60:
        return "summarize"

    return "chat"

def ai_response(prompt, system_msg="You are a helpful assistant."):
    full_prompt = f"{system_msg}\n\nUser: {prompt}"
    response = ollama.generate(
        model="llama3.2",
        prompt=full_prompt
    )
    return response["response"]

def agent(user_input):
    intent = classify_intent(user_input)

    if intent == "pdf":
        pdf_text = read_pdf(user_input)
        return ai_response(
            f"Summarize this PDF:\n\n{pdf_text}",
            system_msg="You are a PDF summarisation assistant."
        )

    if intent == "translate":
        lang = detect(user_input)
        target = "en" if lang == "he" else "he"
        return ai_response(
            f"Translate this to {target}:\n\n{user_input}",
            system_msg="You are a professional translator. Respond only with the translation."
        )

    if intent == "summarize":
        return ai_response(
            f"Summarize the following text:\n\n{user_input}",
            system_msg="You are a concise summarisation assistant."
        )

    return ai_response(user_input)

if __name__ == "__main__":
    print("Local AI Agent (Ollama – Translation + Summary + Q&A)")
    print("Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "quit":
            break

        answer = agent(user_input)
        print("\nAssistant:", answer, "\n")
