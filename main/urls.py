from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', views.chat, name='chat_page'),

    path('procedimentos/lista', views.procedimento_list, name='procedimento_list'),
    path('procedimentos/novo/', views.procedimento_create, name='procedimento_create'),
    path('procedimentos/<int:pk>/editar/', views.procedimento_update, name='procedimento_update'),
    path('procedimentos/<int:pk>/deletar/', views.procedimento_delete, name='procedimento_delete'),

]
