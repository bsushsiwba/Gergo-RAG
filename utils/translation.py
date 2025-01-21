# This is the translation utility that will be used to translate the questions and answers to different languages.

import os
from constants import MODEL
from groq import Groq

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text from source_lang to target_lang using the GROQ model.
    """
    prompt = f"Translate the following text from {source_lang} to {target_lang} and only give translation in output and nothing else:\n\n{text}"
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
