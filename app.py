import os
from decouple import config


from langchain.agents import create_react_agent, AgentExecutor # Função de criação de um agente. 
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit # Todas as ferramentas que tratam o SQL.
from langchain_community.utilities.sql_database import SQLDatabase # Classe de conexão com o banco de dados
from langchain_openai import ChatOpenAI
from langchain import hub # armazenamento de prompts prontos da comunidade.
from langchain.prompts import PromptTemplate

# Configuração da API Key
os.environ['OPENAI_API_KEY'] = config('OPENAI_API_KEY')

# Configurar o modelo
model = ChatOpenAI(
    model_name='gpt-3.5-turbo',
)

# Fazendo a conexão com o banco de dados
db = SQLDatabase.from_uri('sqlite:///pop_database.db')

toolkit = SQLDatabaseToolkit(
    db=db,
    llm=model
) 

system_message = hub.pull('hwchase17/react') # Um prompt pronto de um usuário de langchain que vai ajudar a IA se localizar nas ferramentas.
#print(system_message)

# Criando o Agente:
agent = create_react_agent(
    llm = model,
    tools= toolkit.get_tools(),
    prompt = system_message,
)

# Executando o Agente:
agent_execut = AgentExecutor(
    agent=agent,
    tools=toolkit.get_tools(),
    verbose=True,
)

prompt = '''
Use as ferramentas necessárias para responder perguntas relacionadas aos procedimentos que estão armazenados no banco de dados,
pergunta {q}
'''

prompt_template = PromptTemplate.from_template(prompt)

print("Digite 'Sair' para encerrar o chat . \n")

while True:
    question = input('O que deseja saber ?')
    
    if question.lower() == 'sair':
        print("Chat encerrado!")
        break
    
    

    output = agent_execut.invoke(
        {
            'input':prompt_template.format(q=question),
        }
    )

    print(output.get('output'))
