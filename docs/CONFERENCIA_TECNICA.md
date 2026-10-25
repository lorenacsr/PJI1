# Conferência técnica do código e da aplicação PJI1

Data: 25/10/2026. Registro 1.0.

Registro técnico de apoio à equipe. A revisão identificou falhas reais e produziu correções com testes locais. O atendimento integral das pontuações permanece condicionado à validação em PostgreSQL, à inspeção em navegadores e aparelhos reais e à compatibilização do escopo tecnológico com o material acadêmico.


## 1 Síntese e alcance da conferência

A primeira etapa de isolamento de sessão foi publicada em uma branch do fork da integrante. A conferência ampliada acrescentou correções de API, checklist, revisão, fotos, permissões e compatibilidade com Flet. O pacote ampliado de código e testes foi publicado na branch de melhorias do fork. A implantação desta cópia ainda não foi realizada. Os testes descritos são os executados localmente; não há resultado de integração contínua homologado neste registro.

O repositório original de Flávio permanece preservado. A aplicação Republic anteriormente publicada no Render é outra implementação. Seus testes, sua hospedagem e seus recursos não comprovam o funcionamento desta cópia PJI1.


### 1.1 Fontes e critério de evidência

Foram examinados o código do repositório recebido, suas dependências e o Quadro 7 do documento DOC-20261025-WA0029.pdf, nas páginas impressas 28 a 30. Esse quadro consolida as devolutivas do tutor; não substitui eventuais observações adicionais que não constem nele. O PDF escolhido pelo grupo não foi alterado.

Considera-se verificado somente o comportamento abrangido pelos testes descritos. Inspeção de código, teste de API com banco descartável, construção de controles e uso real em navegador são evidências distintas. Não há declaração de homologação pelo professor, certificação de segurança, conformidade integral de acessibilidade ou aprovação de uso empresarial.


### 1.2 Arquitetura efetivamente identificada

| Componente | Situação desta base |
| --- | --- |
| Backend | Python 3.12, FastAPI, SQLAlchemy assíncrono e JWT |
| Interface | Flet 0.84.0 com Python e serviço web Flet |
| Persistência prevista | PostgreSQL 16 no Docker Compose |
| Dados nos testes HTTP | SQLite descartável com chaves estrangeiras habilitadas |
| Notificações | WebSocket e registros persistidos no banco |
| Java e JavaScript autoral | Não identificados como módulos próprios desta base |


## 1.3 Ferramentas utilizadas e justificativa de escolha

A escolha de cada ferramenta está vinculada à função que ela desempenha nesta implementação. A lista distingue recursos executados nos testes daqueles cuja integração ou hospedagem ainda depende de validação.

| Ferramenta | Função e justificativa |
| --- | --- |
| Python | Linguagem do backend e da interface; concentra regras, integração e testes em uma linguagem. |
| Flet | Constrói a interface web em Python. Sua interação e adaptação em aparelhos reais ainda serão validadas. |
| FastAPI | Expõe a API e valida entradas; separa as regras do sistema da apresentação. |
| SQLAlchemy | Modela tabelas, relações e transações, apoiando a persistência e o carregamento dos registros. |
| PostgreSQL | Banco previsto para persistência relacional. Sua integração completa ainda precisa ser executada. |
| Neon | Branch separada para ensaios de PostgreSQL, preservando a branch principal; banco de teste ainda não criado. |
| JWT e bcrypt | JWT autentica por token; bcrypt armazena hashes de senha. Não se armazenam senhas em texto puro. |
| WebSocket | Envia eventos aos clientes conectados após confirmação dos registros no banco. |
| Pillow | Verifica formato, integridade e dimensões das imagens recebidas. |
| Docker Compose | Descreve os serviços de API, interface e banco para reprodução do ambiente. Build completo ainda pendente. |
| Git e GitHub | Mantêm histórico e rastreabilidade. O fork preserva a origem e as melhorias ficam em branch separada. |
| pytest unittest HTTPX SQLite | Executam regressões e fluxos locais. SQLite é descartável e não substitui o ensaio de PostgreSQL. |
| Uvicorn e Flet web | Servem a API e a interface ASGI. O alinhamento das versões corrigiu a instalação combinada. |

O Render pertence à implantação anterior e ainda não foi validado como hospedagem desta nova cópia. Não se atribuem à base ferramentas ou integrações apenas porque aparecem como tarefas do checklist, como iFood, Neemo ou Eclética.


## 2 Ajustes no backend e nas regras do checklist


### 2.1 Isolamento da autenticação

O estado global foi substituído por uma instância por página. Usuário, token e callbacks deixam de ser compartilhados entre sessões. A regressão verifica duas páginas e logout independente. Arquivos principais: frontend/main.py e app/state.py.


### 2.2 Submissão do checklist

O envio passa a exigir checklist não vazio, todos os itens concluídos e as fotos obrigatórias. A interface e a API aplicam a mesma regra. A alteração elimina a aceitação anterior de apenas 50% e a possibilidade de ignorar fotos.


### 2.3 Estados de itens e da revisão

O colaborador só pode marcar PENDING ou DONE. A revisão aceita apenas APPROVED ou REJECTED. Estados fora desses contratos geram erro de validação, em vez de alterar indevidamente o fluxo.


### 2.4 Motivo da reprovação

A API exige motivo não vazio ao reprovar. A interface orienta seu preenchimento e deixa de oferecer reprovação sem observação. Isso permite ao colaborador compreender a correção solicitada.


### 2.5 Reabertura e conclusão operacional

A reabertura de um checklist reprovado limpa os dados da revisão anterior que poderiam aparecer como atuais. A aprovação encerra o fluxo do checklist; ela não constitui controle de ponto, bloqueio de jornada ou autorização de saída física.


### 2.6 Modelos e histórico

Alterações em modelos e itens já usados por checklists são bloqueadas com resposta 409. Para uma nova rotina, cria-se outro modelo. A exclusão de modelo ainda sem histórico remove corretamente seus itens, sem reescrever evidências passadas.


## 3 Ajustes de proteção e consistência


### 3.1 Fotos e avatares

A leitura do arquivo é limitada antes de sua aceitação. O Pillow verifica formato real e integridade, com limite de dimensões. Foram mantidos os limites de 5 MB para evidências e 3 MB para avatares. Os nomes passam a ser aleatórios, evitando sobrescrita previsível.


### 3.2 Acesso às imagens

A entrega pública irrestrita foi substituída por links assinados com finalidade e arquivo específicos, válidos por 15 minutos. Não se inclui o token de login na URL da imagem. Quem recebe esse link pode utilizá-lo durante a validade; não há revogação individual imediata. Após expiração, a tela precisa ser atualizada.


### 3.3 Permissões e departamentos

Colaborador sem setor não recebe todos os modelos. A consulta a outro departamento é recusada. Um gestor não pode criar ou alterar contas privilegiadas; essa operação fica reservada ao administrador. Departamentos inexistentes e exclusões com vínculos recebem respostas controladas.


### 3.4 Notificações após persistência

Os avisos são enfileirados e enviados após o commit. Uma transação que falha não envia aviso de sucesso. A conexão usada na autenticação do WebSocket é liberada antes da espera por mensagens, e conexões mortas são removidas.


### 3.5 Exportação CSV

A exportação utiliza autenticação Bearer e gravação pelo seletor de arquivos. O token deixa de compor o endereço aberto no navegador. Valores que poderiam iniciar fórmulas de planilha recebem neutralização na saída.


### 3.6 Configuração e entradas inválidas

Em produção, o sistema recusa segredo JWT conhecido ou curto e senhas iniciais fracas. O Compose exige configuração privada. Identificadores JWT inválidos retornam 401; há normalização do e-mail no login e limite explícito de 72 bytes para criação de hash bcrypt.


## 4 Ajustes da interface e da instalação


### 4.1 Seletor de fotos

A interface antiga FilePickerResultEvent e on_result não existe no Flet 0.84.0 instalado. O fluxo foi convertido para serviço FilePicker assíncrono, com with_data para o modo web, e tratamento do retorno dos arquivos.


### 4.2 Sessão e armazenamento

As chamadas inexistentes a client_storage foram substituídas pelo serviço SharedPreferences. Foram ajustados restauração de sessão, último e-mail, estado do assistente inicial e remoção dos dados no logout. A interação real de persistência ainda precisa de teste no navegador.


### 4.3 Compatibilidade de telas

Foram corrigidos argumentos antigos de capitalização, uso de ImageFit, criação de abas da tela de termos e referências a cor de fundo inexistente. As verificações construíram controles reais do Flet, inclusive cartões com dados e imagens simulados.


### 4.4 Contraste e mensagens

As cores centrais de status foram escurecidas, os textos desses indicadores ampliados e os contornos e cores de superfície explicitados. Os estados continuam identificados por texto. O ajuste não equivale a uma auditoria WCAG completa de todas as telas.


### 4.5 Erros e formulários

A exclusão de modelo passa a tratar erros da API. A validação de senha da interface foi alinhada ao mínimo de oito caracteres exigido pelo backend. Os avisos de lembrete passam a atualizar o contador de notificações.


### 4.6 Dependências e execução

Foram incluídos email-validator, bcrypt compatível com Passlib e flet-web, além de alinhamento da versão do Uvicorn. A instalação combinada concluiu e pip check não apontou dependências quebradas. O servidor web respondeu HTTP 200 com o bootstrap Flutter.


## 5 Evidências de teste e limites

| Verificação | Resultado observado | Limite da evidência |
| --- | --- | --- |
| API e contratos de proteção | 26 casos aprovados | HTTPX com transporte ASGI e SQLite descartável; não usa PostgreSQL real. |
| Isolamento de sessão | 1 teste aprovado | Função main real com adaptadores de página; não representa duas janelas reais. |
| Construção da interface | 20 grupos aprovados | Larguras lógicas de 360 e 1366 px; sem renderização Flutter interativa. |
| Instalação das dependências | Concluída | Ambiente Python isolado; não houve build completo dos contêineres. |
| Consistência das dependências | Sem requisitos quebrados | pip check; não constitui análise de vulnerabilidades. |
| Inicialização web | HTTP 200 e bootstrap Flutter | Não comprova login, upload e exportação no navegador. |

Os 26 casos do pytest incluem o ciclo de checklist, permissões e alterações de conta, CRUD de departamentos e modelos, estados inválidos parametrizados, configuração de produção, expiração de JWT, escopo de imagem, CSV, imagens forjadas, leitura limitada e ordenação das notificações em relação ao commit. Os cenários parametrizados contam como casos de teste, não como ferramentas independentes.

O fluxo HTTP exercitou criação, marcação, recusa de envio incompleto, foto falsa e válida, submissão, revisão, motivo da devolução, reabertura, reenvio, aprovação, notificações, histórico, estatísticas e exportação. Os testes de WebSocket verificam o gerenciador de conexões e o envio após commit; não simulam uma rede real entre dois navegadores.

A execução do pytest apresentou avisos de depreciação, incluindo uso legado de datetime.utcnow no código recebido. Os avisos não reprovaram os testes, mas devem ser tratados em manutenção. O resultado não autoriza declarar que todos os cenários de concorrência, tempo, rede ou carga foram cobertos.


## 6 Correspondência com as pontuações do professor

A matriz trata apenas de código e aplicação. Formatação do relatório acadêmico, bibliografia do trabalho original, termos, assinaturas e atividades de campo não foram marcados como resolvidos por esta revisão.

| Pontuação consolidada | Situação e evidência |
| --- | --- |
| Ferramentas e validação do protótipo | Parcial. Dependências identificadas, testes locais e inicialização web. Falta uso interativo real e homologação. |
| Banco modelado e implementado | Parcial. Sete tabelas ORM e relações existentes; fluxos testados com SQLite. Falta execução integrada em PostgreSQL e ensaio de migração. |
| API desenvolvida e integrada | Verificada no alcance local. Rotas HTTP, autenticação, permissões e fluxo exercitados com ORM real em banco descartável. |
| Checklist explicado e verificável | Correção local. Itens por modelo e setor, autoria, conclusão integral, evidências e bloqueios implementados e exercitados. |
| Validação do gestor | Correção local. Aprovar, reprovar com motivo, devolver, reabrir e reenviar foram exercitados. |
| Encerramento do expediente | Delimitação técnica. Aprovação conclui o checklist; não há controle da jornada ou da saída física. |
| Notificação em tempo real | Parcial. WebSocket existente e consistência após commit testada. Falta entrega entre clientes reais e comportamento de reconexão. |
| Testes e melhorias posteriores | Evidência local. Falhas observadas geraram mudanças e regressões documentadas. Não há feedback de trabalhadores coletado nesta etapa. |
| Acessibilidade além de portabilidade | Parcial. Ajuste de contraste e rótulos de estado. Falta teclado, foco, leitor de tela, zoom e medições completas. |
| Nuvem e demonstração funcional | Pendente nesta cópia. O Render do projeto anterior não comprova a publicação do PJI1. |
| Java Python Flet e JavaScript | Divergência de escopo. Esta base não implementa módulo Java nem desenvolvimento JavaScript autoral. A equipe precisa compatibilizar a exigência e a descrição. |
| Versionamento organizado | Código e testes ampliados publicados na branch do fork. Conferência remota dos arquivos e histórico preservado; implantação ainda pendente. |


## 7 Roteiro de validação pela equipe

Cada execução deve registrar data, versão ou commit, aparelho, sistema, navegador, perfil utilizado, resultado esperado e observado, imagem quando pertinente e nome de quem validou. Usar contas e dados fictícios; não carregar imagens de pessoas ou informações comerciais reais para demonstrar o sistema.

| Cenário | Critério para considerar aprovado |
| --- | --- |
| Instalação em PostgreSQL | Instalar em banco de teste autorizado; iniciar e reiniciar API; confirmar tabelas, dados persistidos e ausência de erros de migração. |
| Login e duas sessões | Abrir duas janelas ou aparelhos com contas diferentes; confirmar isolamento, perfil correto, erro de senha e logout sem afetar a outra sessão. |
| Persistência de acesso | Entrar, atualizar e fechar a página; reabrir, verificar restauração e expiração; sair e confirmar que a sessão não reaparece. |
| Fotos em celular e computador | Selecionar imagem real, cancelar seleção, recusar formato falso e excesso de tamanho; abrir evidência e renovar tela após expiração do link. |
| Checklist completo | Tentar enviar incompleto e sem foto; concluir todos os itens; submeter e confirmar bloqueio de edição posterior. |
| Revisão do gestor | Reprovar sem motivo deve falhar; reprovar com motivo, reabrir, reenviar e aprovar; verificar autoria, datas e estado final. |
| Notificações entre clientes | Gestor e colaborador conectados em aparelhos diferentes; executar submissão e revisão; verificar lista, contador, leitura e reconexão. |
| Modelos e departamentos | Criar, editar, ordenar e excluir em dados fictícios; confirmar bloqueio de modelo com histórico e de departamento com vínculos. |
| Painel e CSV | Comparar indicadores com registros de teste, aplicar filtros e exportar; abrir arquivo e conferir conteúdo, acentos e fórmulas neutralizadas. |
| Acessibilidade e adaptação | Usar teclado, foco visível, zoom de 200%, leitor de tela e largura de 360 px; verificar conteúdo, botões e formulários sem cortes ou sobreposição. |


## 8 Pendências e decisões para concluir a validação


### 8.1 Banco de teste na nuvem

Foi criada no Neon uma branch separada denominada audit-pji1-20261025. Nenhuma alteração foi aplicada à branch principal da aplicação anterior. A tentativa de criar o banco pji1_audit nessa branch foi rejeitada pela revisão automática, que exigiu autorização específica por se tratar de recurso persistente com possível consumo de cota. O banco não foi criado; não há ensaio integrado em PostgreSQL aprovado nesta etapa.

O ambiente local também não permitiu iniciar PostgreSQL e não resolveu a conexão direta ao host Neon. Por isso, a conferência utilizou SQLite nos testes HTTP, sem apresentar esse resultado como equivalente ao teste do driver, do esquema e da concorrência em PostgreSQL. Após a autorização, será necessário um caminho de execução compatível para rodar o backend contra o banco de teste.


### 8.2 Escopo e publicação

É necessário confirmar se Java, JavaScript e gestão de insumos são exigências do código a entregar. O relatório escolhido pelo grupo descreve uma arquitetura e recursos do projeto anterior; esta base PJI1 contém outro backend e não apresenta módulo de estoque equivalente. O documento acadêmico continua intacto, mas essa divergência não pode ser dada como resolvida apenas com testes.

A branch principal e o repositório de Flávio permanecem preservados. O pacote ampliado foi publicado na branch de melhorias. Os arquivos de código e testes foram comparados com a cópia local; ainda é necessário implantar e validar em ambiente de teste. Depois da validação, a equipe decide a integração. Não foi enviado pull request ao repositório original.


### 8.3 Limites para uso empresarial

Ainda são necessários testes de carga e concorrência, backup e restauração, revisão de permissões operacionais, recuperação de acesso, política de retenção de imagens e monitoramento. Imagens antigas são mantidas sem sobrescrita e ainda não há rotina de expurgo. O gerenciador WebSocket em memória pressupõe um processo; múltiplos processos exigem coordenação externa. A revisão não constitui homologação para dados empresariais reais.


## 9 Reprodução e fontes consultadas


### 9.1 Comandos de verificação

Os comandos abaixo são executados na raiz do repositório, em ambiente virtual separado. No Windows, adaptar o prefixo de variáveis e o caminho do interpretador. Nenhum comando deve apontar para banco real de produção durante os testes.


### 9.2 Referências técnicas

FLET. FilePicker. Documentação oficial. [S. l.], [s. d.]. Disponível em: https://flet.dev/docs/services/filepicker/. Acesso em: 25 out. 2026.

FASTAPI. Testes assíncronos. Documentação oficial. [S. l.], [s. d.]. Disponível em: https://fastapi.tiangolo.com/pt/advanced/async-tests/. Acesso em: 25 out. 2026.

SQLALCHEMY. Asynchronous I/O asyncio. SQLAlchemy 2.0 Documentation. [S. l.], [s. d.]. Disponível em: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html. Acesso em: 25 out. 2026.

SQLALCHEMY. Relationships API. SQLAlchemy 2.0 Documentation. [S. l.], [s. d.]. Disponível em: https://docs.sqlalchemy.org/en/20/orm/relationship_api.html. Acesso em: 25 out. 2026.

FLAVIOS-SILVA. PJI1. Repositório de código. GitHub, 2026. Base examinada: commit 7135ce38582f7640d73a94ad883ff22be8478270. Disponível em: https://github.com/flavios-silva/PJI1. Acesso em: 25 out. 2026.

DOC-20261025-WA0029.pdf. Documento fornecido pelo grupo. 2026. Quadro 7, p. 28-30. Fonte interna das observações consolidadas do tutor. Autoria bibliográfica completa não confirmada neste registro.

As fontes fundamentam o uso de serviços Flet, testes assíncronos e relações ORM. As conclusões de funcionamento derivam dos testes e do código examinados. A documentação online pode corresponder a versões posteriores; a compatibilidade dos ajustes foi conferida também no pacote Flet 0.84.0 instalado.

A contribuição de IA foi utilizada como apoio técnico. A equipe deve revisar, compreender e validar os ajustes, manter as evidências e observar as regras da instituição sobre sua declaração de uso.
