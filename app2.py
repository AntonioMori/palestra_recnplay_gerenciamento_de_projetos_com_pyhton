
import os
#from decouple import config

from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase


#os.environ['OPENAI_API_KEY'] = config('OPENAI_API_KEY')

model = ChatOpenAI(
    model ='gpt-4o'
)

db = SQLDatabase.from_uri('sqlite:///pop_database.db')

toolkit = SQLDatabaseToolkit(
    db=db,
    llm=model
)

system_message = hub.pull('hwchase17/react')

agent = create_react_agent(
    llm=model,
    tools=toolkit.get_tools(),
    prompt=system_message
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=toolkit.get_tools(),
    verbose=True
)

prompt = '''
Você é um analista de processos e sempre irá tomar como base os procedimentos cadastrados no banco de dados,
para isso use as ferramentas necessárias para responder as perguntas relacionadas aos procedimentos padrões operacionais da empresa,
caso não tenha as informações no banco de dados, informa ao usuário que ainda não tem o procedimento criado na base de dados.

E sempre responda as perguntas passo a passo em português do Brasil.

Perguntas: {q}
'''

prompt_template = PromptTemplate.from_template(prompt)

question = input("Qual o procedimento você deseja saber ?")

output = agent_executor.invoke({
    'input': prompt_template.format(q=question),
})

print(type(output.get('output')))