from functools import lru_cache

from openai import OpenAI


def _simple_call(
    client: OpenAI,
    system_message: str | None,
    source_text: str,
    model: str = "gpt-3.5-turbo",
) -> str:
    messages = [{"role": "user", "content": source_text}]

    if system_message:
        messages.insert(0, {"role": "system", "content": system_message})

    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
    )
    return chat_completion.choices[0].message.content


@lru_cache
def sentiment(src: str) -> str:
    client = OpenAI()
    return _simple_call(
        client,
        "Classify the sentiment expressed in the following text. The output should be one of 'positive', 'negative' or 'neutral'.",
        src,
    )


@lru_cache
def ai(src: str, system_prompt: str | None = None) -> str:
    client = OpenAI()
    return _simple_call(client, system_prompt, src)
