from django.contrib.auth.models import AbstractUser
from django.db import models
import pyotp

class CustomUser(AbstractUser):
    # Hierarquia de Acesso 
    ROLE_CHOICES = (
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('secretaria', 'Secretaria'),
        ('ceo', 'CEO'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='aluno')

    # Dados Pessoais
    data_nascimento = models.CharField(null=True, blank=True)
    sexo = models.CharField(max_length=30, blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    rg = models.CharField(max_length=20, blank=True, null=True)
    estado_civil = models.CharField(max_length=30, blank=True, null=True)
    profissao = models.CharField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)

    cep = models.CharField(max_length=9, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    complemento = models.CharField(max_length=255, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    uf = models.CharField(max_length=2, blank=True, null=True)

    nome_responsavel = models.CharField(max_length=255, blank=True, null=True)
    telefone_responsavel = models.CharField(max_length=15, blank=True, null=True) 

    PLANO_CHOICES = (
        ('mensal', 'Mensal'),
        ('trimestral', 'Trimestral'),
        ('anual', 'Anual'),
    )
    plano = models.CharField(max_length=20, choices=PLANO_CHOICES, blank=True, null=True)
    
    DIAS_CHOICES = (
        ('1x', '1x na semana'),
        ('2x', '2x na semana'),
        ('3x', '3x na semana'),
    )
    dias_por_semana = models.CharField(max_length=2, choices=DIAS_CHOICES, blank=True, null=True)

    # Informações de Saúde
    possui_doenca = models.BooleanField(default=False)
    qual_doenca = models.CharField(max_length=255, blank=True, null=True)
    fez_cirurgia = models.BooleanField(default=False)
    qual_cirurgia = models.CharField(max_length=255, blank=True, null=True)
    faz_tratamento = models.BooleanField(default=False)
    qual_tratamento = models.CharField(max_length=255, blank=True, null=True)
    dores_frequentes = models.BooleanField(default=False)
    quais_dores = models.CharField(max_length=255, blank=True, null=True)
    problemas_coluna = models.BooleanField(default=False)
    quais_problemas_coluna = models.CharField(max_length=255, blank=True, null=True)
    hernia_disco = models.BooleanField(default=False)
    descricao_hernia = models.CharField(max_length=255, blank=True, null=True)
    problemas_cardiacos = models.BooleanField(default=False)
    descricao_problemas_cardiacos = models.CharField(max_length=255, blank=True, null=True)
    hipertensao = models.BooleanField(default=False)
    qual_hipertensao = models.CharField(max_length=255, blank=True, null=True)
    diabetes = models.BooleanField(default=False)
    qual_diabete = models.CharField(max_length=255, blank=True, null=True)
    osteoporose = models.BooleanField(default=False)
    qual_osteoporose = models.CharField(max_length=255, blank=True, null=True)
    labirintite = models.BooleanField(default=False)
    qual_labirintite = models.CharField(max_length=255, blank=True, null=True)

    # Segurança e LGPD
    totp_secret = models.CharField(max_length=32, blank=True, null=True)
    lgpd_consentimento = models.DateTimeField(blank=True, null=True) 
    codigo_recuperacao = models.CharField(max_length=6, blank=True, null=True)
    codigo_expiracao = models.DateTimeField(blank=True, null=True)
    primeiro_acesso = models.BooleanField(default=True) 

    # 2FA
    def save(self, *args, **kwargs):
        # Se ele ainda não tem uma chave do Microsoft Authenticator (totp_secret), nós geramos uma.
        if not self.totp_secret:
            self.totp_secret = pyotp.random_base32()       
        super().save(*args, **kwargs)

class Aula(models.Model):
    data = models.DateField()
    horario = models.TimeField()
    capacidade_maxima = models.IntegerField(default=4) 
    
    professor = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='aulas_ministradas'
    )
    
    alunos = models.ManyToManyField(
        CustomUser, 
        related_name='aulas_agendadas', 
        blank=True
    )

    def __str__(self):
        return f"Aula: {self.data.strftime('%d/%m/%Y')} às {self.horario.strftime('%H:%M')}"
