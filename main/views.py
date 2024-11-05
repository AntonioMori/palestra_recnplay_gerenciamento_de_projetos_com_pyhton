from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from .forms import ProcedimentoForm
from .models import Procedimento
from django.contrib.auth.decorators import login_required


# Importações do LangChain
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from decouple import config
from langchain_core.exceptions import OutputParserException


# Configura a chave de API
os.environ['OPENAI_API_KEY'] = config('OPENAI_API_KEY')

# Configura o modelo, banco de dados e agente
model = ChatOpenAI(model='gpt-4o')
db = SQLDatabase.from_uri('sqlite:///pop_database.db')
toolkit = SQLDatabaseToolkit(db=db, llm=model)
system_message = hub.pull('hwchase17/react')
agent = create_react_agent(llm=model, tools=toolkit.get_tools(), prompt=system_message)
agent_executor = AgentExecutor(agent=agent, tools=toolkit.get_tools(), verbose=True)

# Prompt para o agente
prompt = '''
Você é um analista de processos e sempre irá tomar como base os procedimentos cadastrados no banco de dados,
para isso use as ferramentas necessárias para responder as perguntas relacionadas aos procedimentos padrões operacionais da empresa,
caso não tenha as informações no banco de dados, informe ao usuário que ainda não tem o procedimento criado na base de dados.
E sempre responda as perguntas passo a passo em português do Brasil.
Perguntas: {q}
'''
prompt_template = PromptTemplate.from_template(prompt)

# Funções de visualização
@login_required
@csrf_exempt
def index(request):
    return render(request, 'main/chat.html')

@login_required
@csrf_exempt
def chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question', '')

        try:
            output = agent_executor.invoke({
                'input': prompt_template.format(q=question),
                'handle_parsing_errors': True  # Mantendo o tratamento de erros
            })

            # Obtendo a resposta
            response = output.get('output', 'Desculpe, não consegui encontrar uma resposta para sua pergunta.')

            # Filtrando a resposta
            start_str = "Os procedimentos operacionais padrão registrados no banco de dados são os seguintes:"
            start_index = response.find(start_str)

            if start_index != -1:  # Verifica se a string de início foi encontrada
                response = response[start_index:].strip()  # Extrai a parte relevante e remove espaços

        except OutputParserException as e:
            response = f'Ocorreu um erro ao processar sua pergunta: {str(e)}'
        except Exception as e:
            response = f'Ocorreu um erro inesperado: {str(e)}'

        return JsonResponse({'response': response})

    return render(request, 'main/chat.html')



@login_required
def procedimento_list(request):
    procedimentos = Procedimento.objects.all()
    return render(request, 'main/procedimento_list.html', {'procedimentos': procedimentos})

@login_required
def procedimento_create(request):
    if request.method == "POST":
        form = ProcedimentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('procedimento_list')
    else:
        form = ProcedimentoForm()
    return render(request, 'main/procedimento_form.html', {'form': form})

@login_required
def procedimento_update(request, pk):
    procedimento = get_object_or_404(Procedimento, pk=pk)
    if request.method == "POST":
        form = ProcedimentoForm(request.POST, instance=procedimento)
        if form.is_valid():
            form.save()
            return redirect('procedimento_list')
    else:
        form = ProcedimentoForm(instance=procedimento)
    return render(request, 'main/procedimento_form.html', {'form': form})


@login_required
def procedimento_delete(request, pk):
    procedimento = get_object_or_404(Procedimento, pk=pk)
    if request.method == "POST":
        procedimento.delete()
        return redirect('procedimento_list')
    return render(request, 'main/procedimento_confirm_delete.html', {'procedimento': procedimento})
