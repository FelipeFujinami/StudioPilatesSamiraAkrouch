from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import pyotp
import string, secrets
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        email_digitado = request.POST.get('email')
        senha_digitada = request.POST.get('senha')

        try:
            usuario_db = User.objects.get(email=email_digitado)            
            user = authenticate(request, username=usuario_db.username, password=senha_digitada)
            
            if user is not None:
                request.session['awaiting_2fa_user_id'] = user.id
                return redirect('verificar_2fa')
            else:
                messages.error(request, 'Senha incorreta. Tente novamente.')
                
        except User.DoesNotExist:
            messages.error(request, 'E-mail não encontrado no sistema.')

    return render(request, 'studio/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    if request.user.primeiro_acesso:
        return redirect('primeiro_acesso')

    if not request.user.lgpd_consentimento:
        return redirect('aceitar_termos')

    alunos = User.objects.filter(role='aluno', is_superuser=False, is_staff=False).order_by('-date_joined')
    
    for aluno in alunos:
        cpf_limpo = ''.join(filter(str.isdigit, str(aluno.cpf))) if aluno.cpf else ''
        if len(cpf_limpo) >= 11:
            aluno.cpf_protegido = f"***.***.***-{cpf_limpo[-2:]}"
        else:
            aluno.cpf_protegido = "Não informado"

    return render(request, 'studio/dashboard.html', {'alunos': alunos})

@login_required
def aceitar_termos_view(request):
    if request.user.lgpd_consentimento:
        return redirect('dashboard')

    if request.method == 'POST':
        acao = request.POST.get('acao')
        
        if acao == 'aceitar':
            usuario = request.user
            usuario.lgpd_consentimento = timezone.now() 
            usuario.save()
            messages.success(request, 'Termos aceitos com sucesso! Bem-vindo(a) ao sistema.')
            return redirect('dashboard')
        else:
            logout(request)
            messages.error(request, 'Você precisa aceitar os termos de privacidade para poder utilizar o sistema.')
            return redirect('login')

    return render(request, 'studio/aceitar_termos.html')

from datetime import datetime

@login_required
def cadastrar_aluno_view(request):
    if request.user.role not in ['ceo', 'secretaria'] and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar esta área.')
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado no sistema.')
            return redirect('cadastro_aluno')

        novo_aluno = User()
        novo_aluno.email = email
        novo_aluno.username = email
        novo_aluno.role = 'aluno'

        nome_completo = request.POST.get('nome_completo', '').strip()
        partes_nome = nome_completo.split()
        if partes_nome:
            novo_aluno.first_name = partes_nome[0]
            novo_aluno.last_name = " ".join(partes_nome[1:]) if len(partes_nome) > 1 else ""
            sobrenome_senha = partes_nome[-1].lower() if len(partes_nome) > 1 else "aluno"
        else:
            sobrenome_senha = "aluno"

        # Captura de Dados Pessoais
        data_nasc_raw = request.POST.get('data_nascimento', '')
        if data_nasc_raw:
            try:
                novo_aluno.data_nascimento = datetime.strptime(data_nasc_raw, '%d/%m/%Y').date()
            except ValueError:
                pass

        novo_aluno.sexo = request.POST.get('sexo', '')
        novo_aluno.cpf = request.POST.get('cpf', '')
        novo_aluno.rg = request.POST.get('rg', '')
        novo_aluno.estado_civil = request.POST.get('estado_civil', '')
        novo_aluno.profissao = request.POST.get('profissao', '')
        novo_aluno.telefone = request.POST.get('telefone', '')
        
        # Endereço
        novo_aluno.cep = request.POST.get('cep', '')
        novo_aluno.logradouro = request.POST.get('logradouro', '')
        novo_aluno.numero = request.POST.get('numero', '')
        novo_aluno.complemento = request.POST.get('complemento', '')
        novo_aluno.bairro = request.POST.get('bairro', '')
        novo_aluno.cidade = request.POST.get('cidade', '')
        novo_aluno.uf = request.POST.get('uf', '')

        # Responsáveis (se preenchido que é menor de idade)
        novo_aluno.nome_responsavel = request.POST.get('nome_responsavel', '')
        novo_aluno.telefone_responsavel = request.POST.get('telefone_responsavel', '')

        # Contrato
        novo_aluno.plano = request.POST.get('plano', '')
        novo_aluno.dias_por_semana = request.POST.get('dias_por_semana', '')

        # Captura das Informações de Saúde (Anamnese)
        perguntas_saude = {
            'possui_doenca': 'qual_doenca',
            'fez_cirurgia': 'qual_cirurgia',
            'faz_tratamento': 'qual_tratamento',
            'dores_frequentes': 'quais_dores',
            'problemas_coluna': 'quais_problemas_coluna',
            'hernia_disco': 'descricao_hernia',
            'problemas_cardiacos': 'descricao_problemas_cardiacos',
            'hipertensao': 'qual_hipertensao',
            'diabetes': 'qual_diabete',
            'osteoporose': 'qual_osteoporose',
            'labirintite': 'qual_labirintite'
        }
        
        for campo_bool, campo_texto in perguntas_saude.items():
            valor_booleano = request.POST.get(campo_bool) == 'sim'
            setattr(novo_aluno, campo_bool, valor_booleano)
            
            if valor_booleano:
                desc_texto = request.POST.get(campo_texto, '')
                setattr(novo_aluno, campo_texto, desc_texto)

        # Configura a senha provisória criptografada usando o sobrenome isolado pelo split
        caracteres = string.digits
        num_aleatorios = ''.join(secrets.choice(caracteres) for _ in range(4))
        senha_provisoria = f"{sobrenome_senha}@{num_aleatorios}"
        novo_aluno.set_password(senha_provisoria)

        novo_aluno.save()

        messages.success(request, f'Aluno(a) cadastrado(a) com sucesso! Senha provisória: {senha_provisoria}')
        return redirect('dashboard')

    return render(request, 'studio/cadastro.html')

def esqueci_senha_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        try:
            usuario = User.objects.get(email=email)

            codigo = ''.join(secrets.choice(string.digits) for _ in range(6))
            usuario.codigo_recuperacao = codigo
            usuario.codigo_expiracao = timezone.now() + timedelta(minutes=15)
            usuario.save()

            send_mail(
                'Código de Recuperação - Studio Pilates',
                f'Seu código de recuperação é: {codigo}',
                'nao-responda@studiopilates.com', 
                [usuario.email],
                fail_silently=True 
            )
        except User.DoesNotExist:
            pass

        messages.success(request, 'Código de 6 dígitos enviado para o seu e-mail!')
        return redirect('esqueci_senha')

    return render(request, 'studio/esqueci_senha.html')

def inserir_codigo_view(request):
    # Verifica se a pessoa passou pela tela anterior
    email = request.session.get('email_recuperacao')
    if not email:
        return redirect('esqueci_senha')
        
    if request.method == 'POST':
        codigo_digitado = "".join([request.POST.get(f'digit{i}', '') for i in range(1, 7)])
        
        try:
            usuario = User.objects.get(email=email)
            if usuario.codigo_recuperacao == codigo_digitado and usuario.codigo_expiracao > timezone.now():
                request.session['codigo_validado'] = True 
                return redirect('redefinir_senha')
            else:
                messages.error(request, 'Código inválido ou expirado.')
        except User.DoesNotExist:
            messages.error(request, 'Erro de validação.')
            
    return render(request, 'studio/inserir_codigo.html', {'email': email})

def redefinir_senha_view(request):
    if not request.session.get('codigo_validado'):
        return redirect('login')
        
    if request.method == 'POST':
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if nova_senha == confirmar_senha:
            email = request.session.get('email_recuperacao')
            usuario = User.objects.get(email=email)
            
            usuario.set_password(nova_senha) # Criptografa a nova senha
            usuario.codigo_recuperacao = None # Apaga o código usado
            usuario.codigo_expiracao = None
            usuario.save()
            
            request.session.flush() # Limpa a memória temporária
            
            # Aviso pedindo para logar com a nova senha
            messages.success(request, 'Senha alterada com sucesso! Por favor, faça login com sua nova senha.')
            return redirect('login')
        else:
            messages.error(request, 'As senhas não coincidem. Tente novamente.')
            
    return render(request, 'studio/redefinir_senha.html')

@login_required
def editar_aluno_view(request, id):
    if request.user.role not in ['ceo', 'secretaria'] and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar esta área.')
        return redirect('dashboard')

    aluno = get_object_or_404(User, id=id, role='aluno')

    if request.method == 'POST':
        nome_completo = request.POST.get('nome_completo', '').strip()
        partes_nome = nome_completo.split()
        if partes_nome:
            aluno.first_name = partes_nome[0]
            aluno.last_name = " ".join(partes_nome[1:]) if len(partes_nome) > 1 else ""

        data_nasc_raw = request.POST.get('data_nascimento', '')
        if data_nasc_raw:
            try:
                aluno.data_nascimento = datetime.strptime(data_nasc_raw, '%d/%m/%Y').date()
            except ValueError:
                pass

        aluno.sexo = request.POST.get('sexo', '')
        aluno.cpf = request.POST.get('cpf', '')
        aluno.rg = request.POST.get('rg', '')
        aluno.estado_civil = request.POST.get('estado_civil', '')
        aluno.profissao = request.POST.get('profissao', '')
        aluno.telefone = request.POST.get('telefone', '')
        aluno.cep = request.POST.get('cep', '')
        aluno.logradouro = request.POST.get('logradouro', '')
        aluno.numero = request.POST.get('numero', '')
        aluno.complemento = request.POST.get('complemento', '')
        aluno.bairro = request.POST.get('bairro', '')
        aluno.cidade = request.POST.get('cidade', '')
        aluno.uf = request.POST.get('uf', '')
        aluno.nome_responsavel = request.POST.get('nome_responsavel', '')
        aluno.telefone_responsavel = request.POST.get('telefone_responsavel', '')
        aluno.plano = request.POST.get('plano', '')
        aluno.dias_por_semana = request.POST.get('dias_por_semana', '')

        perguntas_saude = {
            'possui_doenca': 'qual_doenca',
            'fez_cirurgia': 'qual_cirurgia',
            'faz_tratamento': 'qual_tratamento',
            'dores_frequentes': 'quais_dores',
            'problemas_coluna': 'quais_problemas_coluna',
            'hernia_disco': 'descricao_hernia',
            'problemas_cardiacos': 'descricao_problemas_cardiacos',
            'hipertensao': 'qual_hipertensao',
            'diabetes': 'qual_diabete',
            'osteoporose': 'qual_osteoporose',
            'labirintite': 'qual_labirintite'
        }
        
        for campo_bool, campo_texto in perguntas_saude.items():
            valor_booleano = request.POST.get(campo_bool) == 'sim'
            setattr(aluno, campo_bool, valor_booleano)
            if valor_booleano:
                setattr(aluno, campo_texto, request.POST.get(campo_texto, ''))
            else:
                setattr(aluno, campo_texto, '')

        aluno.save()
        messages.success(request, 'Ficha do(a) aluno(a) atualizada com sucesso!')
        return redirect('dashboard')

    data_nascimento_formatada = ''
    if aluno.data_nascimento:
        if isinstance(aluno.data_nascimento, str):
            try:
               
                from datetime import datetime
                data_obj = datetime.strptime(aluno.data_nascimento, '%Y-%m-%d').date()
                data_nascimento_formatada = data_obj.strftime('%d/%m/%Y')
            except ValueError:
                data_nascimento_formatada = aluno.data_nascimento
        else:
            data_nascimento_formatada = aluno.data_nascimento.strftime('%d/%m/%Y')

    return render(request, 'studio/editar_aluno.html', {
        'aluno': aluno,
        'data_nascimento_formatada': data_nascimento_formatada
    })

@login_required
def ver_aluno_view(request, id):
    if request.user.role not in ['ceo', 'secretaria'] and not request.user.is_superuser:
        messages.error(request, 'Acesso restrito.')
        return redirect('dashboard')
    
    aluno = get_object_or_404(User, id=id, role='aluno')
    return render(request, 'studio/ver_aluno.html', {'aluno': aluno})

@login_required
def excluir_aluno_view(request, id):
    if request.user.role not in ['ceo', 'secretaria'] and not request.user.is_superuser:
        messages.error(request, 'Sem permissão.')
        return redirect('dashboard')

    aluno = get_object_or_404(User, id=id, role='aluno')
    aluno.delete() 
    
    messages.success(request, 'Registro excluído com sucesso.')
    return redirect('dashboard')

@login_required
def primeiro_acesso_view(request):
    if not request.user.primeiro_acesso:
        return redirect('dashboard')

    if request.method == 'POST':
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if nova_senha == confirmar_senha:
            usuario = request.user
            usuario.set_password(nova_senha) 
            usuario.primeiro_acesso = False  
            usuario.save()

            update_session_auth_hash(request, usuario)

            if not usuario.lgpd_consentimento:
                return redirect('aceitar_termos')

            messages.success(request, 'Senha definitiva cadastrada com sucesso! Bem-vindo(a) ao site.')
            return redirect('dashboard')
        else:
            messages.error(request, 'As senhas não coincidem. Tente novamente.')

    return render(request, 'studio/primeiro_acesso.html')

def verificar_2fa_view(request):
    # Pega o ID do usuário que está na sala de espera
    user_id = request.session.get('awaiting_2fa_user_id')
    if not user_id:
        return redirect('login')

    usuario = User.objects.get(id=user_id)
    
    provisioning_uri = pyotp.TOTP(usuario.totp_secret).provisioning_uri(
        name=usuario.email, 
        issuer_name="Studio Pilates Samira Akrouch"
    )
    
    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={provisioning_uri}"

    if request.method == 'POST':
        token_digitado = request.POST.get('token')
        totp = pyotp.TOTP(usuario.totp_secret)
        
        if totp.verify(token_digitado):
            login(request, usuario)
            del request.session['awaiting_2fa_user_id'] 
            
            return redirect('dashboard')
        else:
            messages.error(request, 'Código inválido ou expirado. Verifique o seu aplicativo.')

    contexto = {
        'qr_code_url': qr_code_url,
        'chave_manual': usuario.totp_secret
    }
    return render(request, 'studio/verificar_2fa.html', contexto)