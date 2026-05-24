from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'), 
    path('painel/', views.dashboard_view, name='dashboard'),
    path('sair/', views.logout_view, name='logout'),
    path('cadastrar-aluno/', views.cadastrar_aluno_view, name='cadastro_aluno'),
    path('esqueci-minha-senha/', views.esqueci_senha_view, name='esqueci_senha'),
    path('inserir-codigo/', views.inserir_codigo_view, name='inserir_codigo'),
    path('redefinir-senha/', views.redefinir_senha_view, name='redefinir_senha'),
    path('editar-aluno/<int:id>/', views.editar_aluno_view, name='editar_aluno'),
    path('excluir-aluno/<int:id>/', views.excluir_aluno_view, name='excluir_aluno'),
    path('primeiro-acesso/', views.primeiro_acesso_view, name='primeiro_acesso'),
    path('verificar-2fa/', views.verificar_2fa_view, name='verificar_2fa'),
    path('aluno/<int:id>/', views.ver_aluno_view, name='ver_aluno'),
    path('aceitar-termos/', views.aceitar_termos_view, name='aceitar_termos'),
]