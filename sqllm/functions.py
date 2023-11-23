from openai import OpenAI
from functools import lru_cache


def _simple_call(client: OpenAI, system_message: str, source_text: str, model: str = "gpt-3.5-turbo") -> str:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": source_text
            }
        ],
        model=model,
    )
    return chat_completion.choices[0].message.content


@lru_cache
def sentiment(src: str) -> str:
    client = OpenAI()
    return _simple_call(client, "Classify the sentiment expressed in the following text. The output should be one of 'positive', 'negative' or 'neutral'.", src)


@lru_cache
def ai(prompt: str, src: str) -> str:
    client = OpenAI()
    return _simple_call(client, prompt, src)
