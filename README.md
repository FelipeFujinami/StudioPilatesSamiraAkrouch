# Sistema Web Seguro para Gestão de Studio de Pilates 🧘‍♀️💻

[![Status do Projeto](https://img.shields.io/badge/Status-Em%20Desenvolvimento-blue.svg)](#)
[![Linguagem Backend](https://img.shields.io/badge/Backend-Python%20%7C%20Django-092E20.svg?logo=django&logoColor=white)](#)
[![Linguagem Frontend](https://img.shields.io/badge/Frontend-HTML%20%7C%20Bootstrap-563D7C.svg?logo=bootstrap&logoColor=white)](#)

Desenvolvimento de uma aplicação web integrada para o **Studio de Pilates Samira Akrouch**. O sistema une uma interface pública minimalista para atração de alunos com um painel administrativo seguro para a gestão do negócio, desenvolvido com o framework Django.

## 📌 Visão Geral do Projeto

O objetivo desta aplicação é digitalizar a presença do studio e automatizar processos de atendimento e gestão, sem abrir mão da privacidade e segurança dos dados dos alunos. A arquitetura foi dividida em duas frentes:
1. **Vitrine Digital:** Uma *landing page* responsiva, com estética sóbria e direta, focada na conversão de novos clientes.
2. **Painel Administrativo:** Um ambiente de acesso restrito para o gerenciamento de alunos.

## 🚀 Principais Funcionalidades

### 🌐 Módulo Público (Front-end)
* **Interface Responsiva:** Construída com Bootstrap, garantindo compatibilidade com dispositivos móveis e desktops.
* **Design Minimalista:** Uso de paleta de cores focada em transmitir tranquilidade e foco, alinhadas à filosofia do Pilates.
* **Redirecionamento Direto:** Botões de *Call to Action* (CTA) otimizados para iniciar o atendimento de forma ágil.

### 🔒 Módulo Administrativo e Segurança (Back-end)
* **Acesso Restrito:** Área administrativa protegida, acessível via link discreto para minimizar tentativas de acesso indevido ("Security by Obscurity").
* **Segurança Nativa do Django:** Implementação de proteções integradas do framework contra ataques CSRF (Cross-Site Request Forgery), XSS (Cross-Site Scripting) e Clickjacking.
* **Gestão de Alunos (CRUD):** Cadastro seguro, incluindo armazenamento de informações sensíveis (observações de saúde e histórico físico).
* **Sanitização de Dados (ORM):** Uso do ORM do Django para evitar vulnerabilidades críticas, como SQL Injection, garantindo a integridade do banco de dados.

## 🛠️ Tecnologias Utilizadas

**Front-end:**
* HTML5, CSS3, JavaScript
* [Bootstrap](https://getbootstrap.com/) (Componentes e Sistema de Grid)

**Back-end:**
* [Python 3.x](https://www.python.org/)
* [Django](https://www.djangoproject.com/) 

**Banco de Dados:**
* *PostgreSQL*

## ⚙️ Como Executar o Projeto Localmente

### Pré-requisitos
Certifique-se de ter o Python 3.x e o Git instalados em sua máquina.

### Passos de Instalação

1. **Clone o repositório:**
```bash
   git clone [https://github.com/FelipeFujinami/StudioPilatesSamiraAkrouch.git](https://github.com/FelipeFujinami/StudioPilatesSamiraAkrouch.git)
   cd StudioPilatesSamiraAkrouch
