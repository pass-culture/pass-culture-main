import json
import os
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

system_promt = (
    "You are a language expert, your job is to translate a text written in Portuguese into three languages"
    " (English, Italian, French). These translations should be stored in a JSON where the keys"
    " are en for English, it for Italian, and fr for French, "
    "and the values are the translations of each respective language"
)
user_query = "translate this text: "


def translate(text) -> str:
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_promt},
            {"role": "user", "content": user_query + text},
        ],
        model="gpt-4o",
        # response_format={"type": "json_object"},
    )

    response_json = json.loads(chat_completion.model_dump_json(indent=2))
    content = response_json["choices"][0]["message"]["content"]

    return content
