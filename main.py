import os
from decouple import config

from langchain_openai import OpenAI

api: str ='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'

model:any = OpenAI(api_key=api)

question: str = input("O que você quer curiar")

response: str = model.invoke(input = question)

print(response)