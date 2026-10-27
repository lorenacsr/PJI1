# Registro de correções e validações — PJI1

Atualizado em 27/10/2026. Registro técnico; não constitui certificação de acessibilidade nem homologação empresarial.

## Escopo e preservação do original

- Original da equipe: https://github.com/flavios-silva/PJI1.
- Cópia de trabalho: https://github.com/lorenacsr/PJI1.
- Branch das melhorias: `melhorias/isolamento-e-diagnostico`.
- Alterações realizadas exclusivamente na cópia. Não foi aberto pedido de alteração no repositório original.
- Os seis setores, 12 modelos e 107 tarefas originais foram comparados e preservados na verificação anterior. Dados de demonstração não representam execução real na pizzaria.
- Render e Neon foram mantidos; estes ajustes não migram nem substituem o armazenamento.

## Histórico rastreável

| Commit no fork | Problema observado | Alteração |
| --- | --- | --- |
| `31999c4` e ajustes de compatibilidade seguintes | Falhas de sessão entre abas e incompatibilidades de controles | Atualização Flet para 0.85.2 e adequação de bordas. |
| `63c62ae`, `c398e7b` | Ausência de ajuste de tamanho de texto | Controle por sessão entre 100% e 200%, aplicado a atualizações e navegação. |
| `42dea19`, `8aa6a40`, `b6fb596`, `aaba9f2`, `b7572e7` | Imagens sem descrição e contraste insuficiente em parte da paleta | Descrições semânticas de avatares/evidências e escurecimento de cores. |
| `8b11bc7`, `0f1a573` | Necessidade de verificar contratos de acessibilidade e isolamento | Testes de contraste, descrição das imagens, ampliação e sessão. |
| `e14a995`, `4866718` | Percentual pouco claro e texto branco translúcido | Percentuais explícitos, retirada do retorno indevido no login e texto branco opaco. |
| `99ddad1` | HTML de resposta 502 exibido na interface | Mensagem legível em falhas de gateway e rejeição de conteúdo HTML como detalhe de erro. |
| `e4a7562` | Configuração ignorava falhas ao salvar departamentos e avançava | Permanência na etapa quando há erro; informações digitadas mantidas na sessão; erro de carregamento informado. |
| `641b33f` | Consultas falhavam durante indisponibilidade transitória | Até três tentativas somente em GET, com limite total de 90 segundos; gravações não são repetidas automaticamente. |
| `50cbee9` | Botões sobrepostos no diálogo em 200% no celular | Botões em coluna dentro do conteúdo rolável; cabeçalho acompanha a ampliação. |
| `80c39f8` | Nome e e-mail espremidos nos cartões e menu de perfil pouco evidente | Dados da equipe em coluna com largura disponível; rótulo Conta e dicas nas opções. |

Os identificadores acima são prefixos dos commits reais na branch. O histórico Git contém os arquivos e diferenças de cada mudança.

## Validações realizadas e seus limites

| Verificação | Resultado e limite |
| --- | --- |
| Testes do backend | 26 testes passaram na execução técnica anterior; banco descartável de teste. Não equivale a testar cada tela publicada. |
| Fluxo pela API publicada | Login dos perfis, checklist, fotos, envio, reprovação, reabertura, reenvio, aprovação, notificações, exportação e estatísticas verificados com dados fictícios. |
| Persistência | Checklist e imagens recuperados após nova implantação da API. Não é teste de restauração de backup. |
| Departamento e perfil | Criação e listagem de setor temporário, vínculo ao perfil de demonstração e conferência do nome retornado passaram. Vínculo original restaurado; setor temporário removido. Nenhum perfil real foi alterado nesse teste. |
| Falhas de configuração | Dois testes locais passaram: HTML 502 não é exposto e falha de salvamento não avança a etapa; a tentativa seguinte consegue salvar. |
| Recuperação de leitura | Três testes locais passaram: recuperação após 502, POST sem repetição e 401 sem repetição. Login e cinco consultas do painel também passaram contra a API publicada. |
| Construção de interface | 20 grupos passaram nas larguras 360 e 1366; controles reais com API simulada. Não são capturas renderizadas de um celular. |
| Contratos de acessibilidade | Quatro testes passaram: contraste da paleta principal, descrições de imagens, tamanho sem acumular ampliação e isolamento por sessão. Não cobrem todas as combinações de cores. |
| Cartões e diálogo em 200% | Construção adicional verificada em 360 e 1366 após os ajustes; textos preservados nos controles. Validação visual final em celular ainda pendente. |
| Evidências da usuária | Capturas confirmaram carregamento das cinco abas gerenciais e vínculo de um perfil à Cozinha–Manhã. Capturas em 200% revelaram sobreposição e quebra excessiva de texto, que motivaram os commits de layout. |
| Disponibilidade | Uma requisição à API levou aproximadamente 57 segundos e a seguinte cerca de 5 segundos; logs mostraram inicialização do processo. Compatível com retomada do serviço, sem prova de que explique todo 502. |

## Pendências explícitas

- Repetir a inspeção visual do diálogo e dos cartões em 200% no celular após a atualização; verificar também computador e navegação por teclado.
- Validar com leitor de tela real (por exemplo TalkBack/NVDA), incluindo foco, ordem de leitura e nomes dos botões.
- Conferir operações de editar perfil, sair e ativar/desativar com os perfis adequados. Existência do controle no código não prova o funcionamento completo na interface.
- Não afirmar disponibilidade contínua do plano gratuito, conformidade integral WCAG ou aprovação em campo apenas com estes testes.
- Testes locais não substituem os resultados do GitHub Actions; conferir o pipeline separadamente.
- Concluir manual com capturas e validação do fluxo antes de apresentá-lo como manual homologado.

## Procedimento para novas alterações

1. Trabalhar somente no fork e na branch de melhorias.
2. Fazer um commit por alteração lógica, com descrição do problema e da correção.
3. Executar verificações proporcionais ao risco; guardar resultado e limitações, sem credenciais ou dados pessoais nos registros públicos.
4. Publicar e conferir o commit implantado no Render; um deploy iniciado não significa versão ativa.
5. Acrescentar a mudança e as validações a este registro, distinguindo implementado, testado tecnicamente e validado em uso.
