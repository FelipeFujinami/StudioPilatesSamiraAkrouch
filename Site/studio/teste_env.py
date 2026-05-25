import os
from dotenv import load_dotenv

load_dotenv()

secret_key = os.getenv('SECRET_KEY')

if secret:
    print("Sucesso! Variável carregada com sucesso.")
else:
    print("Erro: A variável não foi encontrada. Verifique se o nome está idêntico ao .env.")