# Quefazeres

Projeto acadêmico de aplicação web para organizar tarefas domésticas em família e trocar pontos por recompensas.

## Escopo

O responsável cria o vínculo familiar, contas das crianças, atividades com pontuação e recompensas. A criança acessa as tarefas designadas, envia uma foto como comprovante e acompanha a análise. Os pontos só são creditados após aprovação; recompensas são resgatadas conforme o saldo.

## Documentação

- [Especificação do MVP](docs/spec.md)
- [Estrutura sugerida](docs/estrutura.md)

## Tecnologias previstas

- Python 3.14
- Django 5.2.8
- SQLite padrão do Django

## Estado

MVP web funcional em desenvolvimento: cadastro do responsável e família, criação de contas infantis, tarefas com envio e análise de foto, pontuação e resgate de recompensas.

## Executar localmente

```powershell
python manage.py migrate
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`, crie o usuário do responsável e, pelo painel, cadastre uma criança, atividade e recompensa. A criança usa o login criado pelo responsável.

Fotos ficam em `media/` durante o desenvolvimento. A aplicação usa SQLite padrão do Django.
