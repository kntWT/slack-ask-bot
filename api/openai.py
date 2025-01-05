from openai import OpenAI
from pydantic import BaseModel
import os

prompt = ""
file_name = "prompt.md"
if not os.path.exists(file_name):
    file_name = "prompt.txt"
with open(file_name, "r") as f:
    prompt = f.read()


class Tags(BaseModel):
    tags: list[str]


client = OpenAI()


def get_tags(question: str) -> Tags:
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": prompt},
            {"role": question}
        ],
        response_format=Tags,
    )
    return response.choices[0].message.parsed
