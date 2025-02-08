# This is the translation utility that will be used to translate the questions and answers to different languages.

import os
from constants import *
from groq import Groq
from openai import OpenAI
from google import genai

# Track which API is active
ACTIVE_API = None

# USE client based on the API KEY and MODEL
if os.environ.get("GROQ_API_KEY") != None:
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    ACTIVE_API = "groq"
    print("GROQ Instance Created")
elif os.environ.get("OPENAI_API_KEY") != None:
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    ACTIVE_API = "openai"
    print("OpenAI Instance Created")
elif os.environ.get("GOOGLE_API_KEY") != None:
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
    ACTIVE_API = "google"
    print("Google Generative AI Instance Created")
else:
    print(f"LLM Error: API Key not found")


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text from source_lang to target_lang using the language model.
    """
    prompt = f"Translate the following text from {source_lang} to {target_lang} and only give translation in output and nothing else:\n\n{text}"

    if ACTIVE_API == "google":
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text.strip()

    # Default behavior for OpenAI and Groq
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=MODEL,
    )
    return chat_completion.choices[0].message.content.strip()


def translate_to_all_languages(data: dict) -> dict:
    languages = ["en", "hu", "de"]
    translated = {}

    # Identify the source language
    source_lang = next(
        (
            lang
            for lang in languages
            if data.get(f"question_{lang}") and data.get(f"answer_{lang}")
        ),
        None,
    )
    if not source_lang:
        raise ValueError(
            "At least one pair of question and answer must be provided in the same language."
        )

    for lang in languages:
        translated[f"{lang}_question"] = data.get(f"question_{lang}") or translate_text(
            data[f"question_{source_lang}"], source_lang, lang
        )
        translated[f"{lang}_answer"] = data.get(f"answer_{lang}") or translate_text(
            data[f"answer_{source_lang}"], source_lang, lang
        )

    return translated
