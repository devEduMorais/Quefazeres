# Especificação do Quefazeres

## 1. Objetivo

Aplicação web acadêmica para uma família organizar tarefas domésticas. O responsável cria contas infantis, publica atividades e define recompensas. A criança registra a conclusão com uma foto; o responsável analisa o envio e, se aprovar, os pontos são creditados.

## 2. Usuários e permissões

### Responsável

- Cria a família e recebe um identificador familiar.
- Cria as contas das crianças e entrega a cada uma seu usuário e senha.
- Cria tarefas, designa a criança e define os pontos.
- Cria recompensas e define seus valores em pontos.
- Consulta envios pendentes e aprova ou reprova cada envio.
- Consulta o saldo de pontos das crianças da família.

### Criança

- Não cria a própria conta.
- Entra com as credenciais criadas pelo responsável.
- Consulta as tarefas disponíveis para ela.
- Envia uma foto como comprovante de conclusão.
- Consulta o resultado da análise e seu saldo.
- Resgata uma recompensa quando tiver pontos suficientes.

Cada usuário pertence a uma família. As telas e ações disponíveis dependem do perfil (responsável ou criança).

## 3. Fluxos principais

### Cadastro e vínculo familiar

1. O responsável cria a família informando o sobrenome.
2. O sistema gera um identificador familiar único.
3. O responsável cria uma conta para cada criança dentro dessa família.
4. A criança usa as credenciais fornecidas para acessar seu painel.

O identificador e o sobrenome servem para reconhecer o vínculo familiar na aplicação. O acesso é feito com credenciais individuais, não apenas com o identificador familiar.

### Tarefa e análise

1. O responsável cadastra uma atividade, informa sua descrição, escolhe uma criança e define pontos inteiros positivos.
2. A atividade aparece no painel da criança designada.
3. A criança envia uma foto para registrar a conclusão; o envio fica pendente.
4. O responsável aprova ou reprova o envio.
5. Na aprovação, a atividade é concluída e os pontos são somados uma única vez.
6. Na reprovação, nenhum ponto é creditado e a atividade volta a ficar disponível para novo envio.

### Resgate de recompensa

1. O responsável cadastra uma recompensa e seu custo em pontos.
2. A criança consulta as recompensas e escolhe uma.
3. O sistema só confirma o resgate se o saldo cobrir o custo; ao confirmar, debita os pontos.

Exemplos para demonstração: arrumar o quarto (5 pontos), lavar a louça (7 pontos), balinha (10 pontos), sorvete (20 pontos) e passeio (30 pontos).

## 4. Regras de negócio

- Uma família tem pelo menos um responsável.
- Uma conta infantil é criada por um responsável e pertence à mesma família.
- Responsáveis só consultam e administram dados de sua própria família.
- Crianças só veem suas tarefas, envios, saldo e recompensas da própria família.
- Apenas o responsável cria/edita tarefas, designa crianças, define pontos e administra recompensas.
- Tarefas e recompensas devem pertencer à família que as criou.
- Os valores de tarefas e recompensas são números inteiros maiores que zero.
- Uma tarefa só concede pontos depois da aprovação do responsável.
- Cada envio aprovado credita os pontos uma única vez.
- Reprovação não altera o saldo e libera a tarefa para novo envio.
- O resgate com saldo insuficiente deve ser bloqueado.
- O débito de pontos ocorre uma única vez quando o resgate é confirmado.

## 5. Telas do MVP

1. **Login** — acesso para responsável e criança.
2. **Painel do responsável** — resumo da família, crianças, tarefas, envios pendentes e recompensas.
3. **Gerenciar crianças** — criar conta infantil e visualizar credenciais iniciais para entrega.
4. **Tarefas** — criar tarefa, escolher criança, definir pontos e consultar estado.
5. **Analisar envio** — visualizar tarefa e foto, aprovar ou reprovar.
6. **Recompensas** — cadastrar recompensa e custo.
7. **Painel da criança** — tarefas disponíveis, envio de foto, saldo e recompensas para resgate.

## 5.1 Interface e navegação

- A prioridade inicial é o funcionamento das regras, não uma identidade visual elaborada.
- A interface será web responsiva, com conteúdo centralizado e margens laterais generosas para facilitar uma futura adaptação a aplicativo. Não será simulada a moldura de um celular.
- As URLs devem permanecer simples, sem parâmetros de formulário, pontos, saldos ou identificadores desnecessários.
- Abrir páginas usa GET. Criar, editar, aprovar, reprovar e resgatar usa formulários POST com proteção CSRF. Após uma ação POST, redirecionar para a página apropriada (padrão Post/Redirect/Get).
- POST evita colocar os dados do formulário na URL; não esconde a rota e não substitui autenticação, autorização ou HTTPS.

## 6. Dados principais (proposta)

- **Família:** identificador único e sobrenome.
- **Usuário:** autenticação Django e perfil (responsável ou criança), ligado à família.
- **Tarefa:** família, título/descrição, criança designada, pontos e estado.
- **Envio:** tarefa, foto, data e resultado da análise.
- **Recompensa:** família, nome e custo em pontos.
- **Resgate:** criança, recompensa, custo no momento do resgate e data.

O saldo pode ser calculado pelos pontos de tarefas aprovadas menos os resgates confirmados, evitando manter dois saldos divergentes. A estrutura final do banco será decidida na implementação aprovada.

## 7. Fora do escopo do MVP

- Recorrência e calendário automático de tarefas.
- Sincronização offline ou aplicativo móvel nativo.
- Notificações, chat e múltiplos níveis de aprovação.
- Regras avançadas de auditoria ou relatórios.
- Fluxo de aprovação de resgate de recompensa.

## 8. Critérios de aceite

- O responsável consegue criar uma família, cadastrar uma criança e entregar credenciais de acesso.
- Uma criança não consegue criar contas nem acessar telas de responsável.
- O responsável consegue criar tarefa para uma criança e definir sua pontuação.
- A criança consegue ver somente suas tarefas e enviar uma foto.
- O envio aparece como pendente para o responsável.
- Aprovar credita os pontos uma única vez; reprovar não credita e permite novo envio.
- O responsável consegue cadastrar recompensas com custo em pontos.
- O resgate é concluído e debitado quando há saldo suficiente, e é bloqueado quando não há.
- Um usuário de uma família não consegue acessar dados de outra família.

## 9. Base técnica acordada

- Django.
- SQLite padrão do Django.
- Aplicação web simples, adequada para demonstração acadêmica.
- Upload local de fotos durante o desenvolvimento.
- Python e Django já estão disponíveis no ambiente verificado.
