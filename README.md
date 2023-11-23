# sqllm
With this library, you can use LLM to perform queries on your data.
The only LLM function you need to learn is the "AI" function.

```python
import os
import sqllm

os.environ["OPENAI_API_KEY"] = "your-api-key"

# query over DB
conn  # any DB connection you have (passed into pd.read_sql)
sqllm.query(
    conn,
    """
    SELECT
        AI('Classify the sentiment expressed in the following text.', review)
    FROM
        reviews
    """
)

# query on pandas dataframe
df  # any dataframe
sqll.query_df(
    df,
    """
    SELECT
        AI('Classify the sentiment expressed in the following text.', review)
    FROM
        df
    """
)

```

In addition, your own Python functions can also be executed in SQL. This allows you to integrate various text processing with LLM into SQL.

```python
from functools import lru_cache
from openai import OpenAI
import sqllm


# To reduce the number of LLM calls, the use of lru_cache is recommended.
@lru_cache
def sentiment(src: str) -> str:
    client = OpenAI(api_key="your-api-key")
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Classify the sentiment expressed in the following text. The output should be one of 'positive', 'negative' or 'neutral'."
            },
            {
                "role": "user",
                "content": src
            }
        ],
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content


sqllm.query(
    conn,
    """
    SELECT
        sentiment(review) as sentiment
    FROM
        reviews
    """,
    [sentiment]
)
```

## Important notes
This library is not recommended for execution on large data.
