# Quefazeres

O Quefazeres é uma aplicação web acadêmica para organizar tarefas domésticas em família. Um responsável cadastra crianças, distribui tarefas com pontuação e cria prêmios. A criança acompanha suas tarefas, envia uma foto como comprovante e pode trocar pontos por prêmios depois que um responsável aprova suas tarefas.

Este guia explica o projeto para quem vai usá-lo, estudá-lo ou continuar seu desenvolvimento, incluindo pessoas e agentes de IA.

## O que a aplicação faz

Cada conta tem um perfil associado a uma família e um papel: **responsável** ou **criança**. O servidor verifica esse papel e o vínculo familiar antes de permitir acesso a dados e ações.

### Fluxo do responsável

1. Cria uma conta e uma família. A família recebe um identificador único.
2. No painel, usa o menu inferior para acessar **Tarefas**, **Prêmios**, **Família** e **Análises**. Essas áreas trocam de conteúdo sem recarregar a página.
3. Em **Tarefas**, cria atividades, escolhe uma criança e define os pontos. A lista mostra os estados atuais.
4. Em **Prêmios**, cadastra prêmios e seus custos em pontos, além de consultar resgates recentes.
5. Em **Família**, consulta e altera o nome da família e gerencia as contas infantis. Crianças podem ser desativadas sem apagar os registros e reativadas depois.
6. Em **Análises**, os envios pendentes aparecem primeiro. O responsável pode ver a foto e aprovar ou reprovar. O histórico de tarefas aparece abaixo das pendências.

### Fluxo da criança

1. Entra com o usuário e a senha criados pelo responsável.
2. Usa o menu inferior para alternar entre **Lojinha**, **Tarefas** e **Perfil**. A seleção acompanha o fragmento da URL e o histórico do navegador.
3. Em **Tarefas**, consulta as tarefas designadas e envia uma foto como comprovante. A tarefa fica pendente para análise.
4. Quando o responsável aprova, os pontos da tarefa passam a compor o saldo. Se reprovar, a tarefa volta a ficar disponível para nova tentativa sem creditar pontos.
5. Em **Lojinha**, pode resgatar prêmios quando o saldo for suficiente. O custo é registrado no resgate.

> O envio de formulários usa POST, proteção CSRF e redirecionamento após a ação. A troca entre painéis do menu acontece no próprio documento, sem abrir outra aba do navegador.

## Organização do código

| Caminho | Responsabilidade |
| --- | --- |
| `config/` | Configurações Django, URLs principais e arquivos de inicialização do projeto. |
| `familia/` | Famílias, perfis, autenticação, regras por papel e painéis. |
| `tarefas/` | Tarefas, comprovantes enviados e decisões de aprovação/reprovação. |
| `recompensas/` | Prêmios, cálculo de saldo e resgates. |
| `templates/familia/` | Páginas e painéis HTML. |
| `static/familia/` | Estilos, navegação das abas do responsável, ícones e ilustrações. |
| `media/` | Arquivos enviados, como fotos de comprovação. |
| `docs/` | Especificação do MVP e notas sobre estrutura. |
| `.agents/skills/quefazeres/` | Skill reutilizável com os padrões específicos do projeto. |

### Dados principais

- **Família:** identificador UUID e sobrenome/nome familiar.
- **Perfil:** liga o usuário Django à família e define o papel; contas infantis também podem ser ativadas ou desativadas.
- **Tarefa:** família, criança designada, descrição, pontos e estado (`disponível`, `pendente` ou `concluída`).
- **Envio:** comprovante da tarefa, estado da análise e datas de envio/análise.
- **Recompensa:** prêmio da família, custo em pontos e estado ativo.
- **Resgate:** criança, prêmio, custo registrado e data.

O saldo é calculado a partir das tarefas aprovadas e dos resgates. Desativar uma criança bloqueia seu acesso sem apagar tarefas, comprovantes ou resgates existentes.

## Rotas principais

| Rota | Uso |
| --- | --- |
| `/` | Encaminha a pessoa autenticada ao painel do seu papel. |
| `/cadastro/`, `/entrar/`, `/sair/` | Cadastro, entrada e saída. |
| `/responsavel/`, `/crianca/` | Painéis dos dois papéis. |
| `/criancas/nova/`, `/criancas/<id>/editar/` | Criação e edição de contas infantis. |
| `/criancas/<id>/alternar/`, `/familia/editar/` | Ativar/desativar criança e alterar dados da família. |
| `/tarefas/nova/`, `/tarefas/criar/`, `/tarefas/enviar/` | Formulários e ações de tarefas. |
| `/tarefas/analise/`, `/tarefas/aprovar/`, `/tarefas/reprovar/` | Análise de comprovantes. |
| `/recompensas/nova/`, `/recompensas/criar/`, `/recompensas/resgatar/` | Criação e resgate de prêmios. |

As rotas de alteração aceitam POST e verificam o papel e a família relacionados. A interface principal atual usa formulários dentro dos painéis; as rotas de formulário dedicadas continuam disponíveis para os fluxos existentes.

## Tecnologias

- Python 3.14
- Django 5.2.8
- SQLite
- HTML, CSS e JavaScript sem framework adicional

As dependências Python estão em `requirements.txt`. As mídias são armazenadas localmente durante o desenvolvimento. O projeto serve essas mídias pelo Django quando `DEBUG` está ligado; isso não configura armazenamento de produção.

## Preparar e executar localmente

Use PowerShell a partir da pasta do projeto:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Abra `.env` e preencha os valores. Para desenvolvimento local:

```dotenv
DJANGO_SECRET_KEY=uma-chave-privada-para-este-ambiente
DJANGO_DEBUG=true
SQLITE_NAME=db.sqlite3
```

Mantenha `.env` privado; ele é ignorado pelo Git. `SQLITE_NAME` aceita caminho relativo à pasta do projeto ou caminho absoluto. O banco é criado/aplicado pelas migrações.

```powershell
python manage.py migrate
python manage.py runserver
```

Abra `http://127.0.0.1:8000/`, crie a família e a conta do responsável. Depois cadastre uma criança, uma tarefa e um prêmio para experimentar os dois painéis.

## Verificações

```powershell
python manage.py check
python manage.py test familia tarefas recompensas
```

## Agentes, skills e padrões para contribuições

Não há agentes autônomos configurados neste repositório. Para trabalho com pessoas ou agentes de IA, use os papéis recomendados abaixo. Uma mesma pessoa/agente pode assumir mais de um papel em mudanças pequenas.

| Papel recomendado | Responsabilidade |
| --- | --- |
| Implementação Django | Alterar views, forms, models e rotas no app dono do fluxo; manter verificações de papel e família no servidor. |
| Interface | Ajustar templates e `static/familia/`; manter a paleta, cartões, cantos arredondados e barra inferior. Não usar emojis como ícones. |
| Testes e revisão | Conferir fluxos dos dois papéis, permissões entre famílias, estados de tarefas e saldo; executar as verificações acima. |

Carregue a skill **Quefazeres** em `.agents/skills/quefazeres/SKILL.md` quando um agente compatível com skills for trabalhar neste projeto. Ela registra os padrões específicos, mas não substitui a leitura do código nem as verificações.

### Regras práticas do projeto

- Preserve os fluxos de responsável e criança ao alterar templates ou estilos compartilhados.
- Mantenha a troca de painéis no próprio documento, com fragmento da URL e voltar/avançar sincronizados.
- Use os ícones existentes e mantenha consistência com a tela infantil.
- Restrinja consultas e alterações do responsável à família autenticada; a criança só pode acessar seus próprios dados e os dados da própria família permitidos pelo fluxo.
- Use POST e proteção CSRF para alterações. Após salvar, volte ao painel e à seção correspondente.
- Não apague histórico de uma criança ao desativar sua conta.
- Antes de concluir uma mudança Django, rode `python manage.py check` e os testes relevantes.
- Não adicione `.env`, `db.sqlite3`, senhas, chaves ou outros valores locais ao Git. Mídias do projeto ficam em `media/` e são versionadas conforme solicitado para este repositório.

## Documentação adicional

- [Especificação do MVP](docs/spec.md)
- [Estrutura e responsabilidades dos apps](docs/estrutura.md)
