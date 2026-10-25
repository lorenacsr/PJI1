# Plano de aprimoramento da cópia PJI1

Origem: https://github.com/flavios-silva/PJI1, main no commit 7135ce3.
Autor e histórico originais preservados. Esta branch não altera o repositório de origem.

## Primeira etapa: isolamento de sessão

- Estado AppState criado dentro de main(page), isolando token, usuário e callbacks por sessão Flet.
- Removida a instância global de estado.
- Regressão executa a função main real com páginas adaptadas, verifica sessões independentes e logout isolado.
- .gitignore evita adicionar ambientes, arquivos de configuração privados, uploads e bancos locais.

O teste não é uma validação completa de navegador ou API. Executar com:

```sh
python -m unittest discover -s tests -v
```

## Próximas prioridades da revisão

1. Configuração de produção: o Compose usa um segredo padrão diferente do único valor bloqueado por Settings. Revisar validação e exigir configuração privada.
2. Inicialização: contas privilegiadas possuem senhas padrão e são criadas quando ausentes. Preparar primeiro acesso seguro, sem alterar contas existentes automaticamente.
3. Fotos: uploads são servidos por StaticFiles sem autenticação. Planejar entrega protegida, retenção e limites de leitura; o upload atual lê o arquivo inteiro antes de verificar 5 MB.
4. Validação: o backend permite envio com 50% dos itens e não confere as fotos obrigatórias no método de submissão. Comparar com o requisito aprovado antes de mudar a regra.
5. Dependências: EmailStr aparece nos schemas, mas email-validator não consta nos requirements. Confirmar instalação limpa e compatibilidade Flet 0.84.0.
6. Fluxos: testes de API com PostgreSQL isolado, persistência de modelos, revisão e notificações depois de commit, exportação CSV e tratamento de falhas.
7. Interface: contraste, formulários, sessão e fotos em navegador de computador e celular real.
8. Documentação: atualizar metodologia e manual para FastAPI/Flet/SQLAlchemy/PostgreSQL após validar o que estiver efetivamente funcionando.

## Correspondência com os outros materiais

Este projeto usa backend Python/FastAPI, ORM SQLAlchemy, JWT, Flet e WebSocket. Não é a aplicação Java/Python/Flet desenvolvida anteriormente. Não atribuir Java, estoque ou recursos de outro projeto a esta base sem implementação e evidência.

O index.html do GitHub Pages é distinto da execução dinâmica de backend e frontend. Confirmar funcionamento por instalação e testes, sem usar a presença da página estática como prova da API.

Nenhum deploy, alteração de banco do estabelecimento ou envio de pull request ao autor foi realizado nesta etapa. Melhorias ficarão na conta da integrante, com identificação de origem e histórico.

## Rastreabilidade das pontuações técnicas do professor

Esta tabela distingue a primeira entrega das verificações ainda necessárias. Não representa conclusão de todas as pontuações.

| Pontuação técnica | Tratamento nesta cópia | Evidência / situação |
| --- | --- | --- |
| Testes e validação da solução | Teste automatizado para duas páginas com login e logout independentes | `tests/test_session_isolation.py`; aprovado localmente com adaptadores, sem navegador real |
| Versionamento e descrição das melhorias | Branch própria, origem preservada e commits descritivos | `melhorias/isolamento-e-diagnostico` |
| Funcionamento do sistema com múltiplos usuários | Estado de autenticação criado por sessão | `frontend/main.py` e `frontend/app/state.py` |
| API e banco implementados e integrados | FastAPI e modelos SQLAlchemy já existem na base recebida | Integração com PostgreSQL ainda precisa de teste em ambiente isolado |
| Detalhamento do checklist, revisão e encerramento | Fluxos existentes serão conferidos quanto a permissões, estados e evidências | Pendente; não mudar a regra de submissão sem conferir o requisito |
| Notificações em tempo real | WebSocket existe na base; conferir entrega e consistência transacional | Pendente de teste integrado |
| Acessibilidade | Conferir contraste, rótulos, teclado e responsividade | Pendente; funcionamento em celular não prova acessibilidade |
| Hospedagem e demonstração funcional | Separar página estática da aplicação com API e banco | Deploy desta cópia ainda não realizado |
| Articulação com tecnologias exigidas na disciplina | Registrar as tecnologias realmente usadas | Esta base não implementa Java; não declarar requisito atendido sem implementação |

Itens de formatação acadêmica, referências e termos ficam a cargo da equipe, conforme o escopo solicitado. A relação deve ser confrontada com a devolutiva integral para identificar eventuais exigências adicionais.
