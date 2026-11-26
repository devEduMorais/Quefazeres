# Estrutura sugerida do projeto

Estrutura enxuta para organizar a implementação após aprovação. Nenhum código foi iniciado.

```text
quefazeres/
├── manage.py
├── config/                 # Configurações e URLs do projeto Django
├── familia/                # Família, perfis e criação de contas infantis
├── tarefas/                # Tarefas, envios com foto e análise
├── recompensas/            # Catálogo e resgates
├── templates/              # Telas HTML compartilhadas
├── static/                 # CSS e imagens da interface
├── media/                  # Fotos enviadas (desenvolvimento local)
├── docs/
│   ├── spec.md
│   └── estrutura.md
├── README.md
└── requirements.txt
```

## Responsabilidade dos apps

- `familia`: vínculo familiar e telas de responsável/criança.
- `tarefas`: criação, designação, envio da foto e aprovação/reprovação.
- `recompensas`: cadastro e resgate com validação de saldo.
- `config`: configuração Django, rotas principais e ajustes do SQLite.

Esta divisão pode ser reduzida ou ajustada durante a implementação se mantiver o projeto simples para apresentação.

## Rotas implementadas

- `/cadastro/`, `/entrar/`, `/sair/` e `/` para sessão e entrada.
- `/responsavel/`, `/crianca/` e `/criancas/nova/` para os painéis e criação de contas infantis.
- `/tarefas/nova/`, `/tarefas/criar/`, `/tarefas/enviar/`, `/tarefas/analise/`, `/tarefas/aprovar/` e `/tarefas/reprovar/`.
- `/recompensas/nova/`, `/recompensas/criar/` e `/recompensas/resgatar/`.

As rotas de ação aceitam POST; páginas e formulários usam GET. As ações POST requerem CSRF.

## Navegação e formulários

- URLs das páginas são caminhos curtos, como `/`, `/tarefas/` e `/recompensas/`.
- Formulários de alteração usam POST, CSRF do Django e redirecionamento após salvar.
- Identificadores e dados privados não devem ser colocados em query strings quando a ação puder usar a sessão e POST.
- Cada view verifica o perfil e a família antes de ler ou alterar registros.
- Layout simples com largura confortável e espaçamento lateral maior, mantendo uso viável em telas menores sem imitar a interface de um celular.
