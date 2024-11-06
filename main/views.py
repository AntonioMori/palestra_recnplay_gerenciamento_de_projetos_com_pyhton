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
agent_executor = AgentExecutor(agent=agent, tools=toolkit.get_tools(), handle_parsing_errors=False, verbose=True)

# Prompt para o agente
prompt = '''
Você é um analista de processos e sempre irá tomar como base os procedimentos cadastrados no banco de dados.
Para isso, use as ferramentas necessárias para responder perguntas relacionadas aos procedimentos padrões operacionais da empresa.
Caso não tenha as informações no banco de dados, informe ao usuário que o procedimento ainda não foi criado.
Sempre responda as perguntas passo a passo em português do Brasil.
Pergunta: {q}
'''
prompt_template = PromptTemplate.from_template(prompt)

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
            # Executa o agente com o template configurado
            output = agent_executor.invoke({
                'input': prompt_template.format(q=question),
            })

            # Extrai a resposta ou mostra uma mensagem padrão
            response = output.get('output', 'Desculpe, não consegui encontrar uma resposta para sua pergunta.')
        except OutputParserException as e:
            # Extrai o conteúdo após "Could not parse LLM output: "
            error_message = str(e)
            start_index = error_message.find("Could not parse LLM output: ") + len("Could not parse LLM output: ")
            response = error_message[start_index:].strip() or 'Ocorreu um erro ao processar sua pergunta.'
            print(f"Erro de parsing ao processar a pergunta: {response}")  # Log do erro
        except Exception as e:
            # Captura outros erros
                    
            error_message = str(e)
            start_index = error_message.find("Could not parse LLM output: ") + len("Could not parse LLM output: ")
            response = error_message[start_index:].strip() or 'Ocorreu um erro ao processar sua pergunta.'
            print(f"Erro inesperado: {str(e)}")  # Log do erro

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
