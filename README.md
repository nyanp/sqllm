# sqllm - Bringing the Power of LLM to SQL
With this library, you can use LLM to perform queries on your data.
The only LLM function you need to learn is the "AI" function.

- `AI(prompt: str) -> str`: Returns text generated by GPT given the prompt.

Thanks to the cache, if the AI function is called repeatedly with the same arguments, the LLM is called only the first time.

 
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
        AI('Classify the sentiment expressed in the following text. \ntext:' || review)
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
        AI('Classify the sentiment expressed in the following text. \ntext:' || review)
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

The `sqllm.functions` module contains several example implementations of user-defined functions. This implementation can be used out of the box.


```python
import sqllm
from sqllm.functions import sentiment, summarize


sqllm.query(
    conn,
    """
    SELECT
        sentiment(review) as sentiment,
        summarize(review) as review_summary
    FROM
        reviews
    """,
    [sentiment, summarize]
)
```

## Installation
```
pip install sqllm
```

## Important notes
It is not recommended to run this library on large tables from the cost and processing time point of view.