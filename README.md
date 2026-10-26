# Pizzaria Check In revisão técnica

Fork de [flavios-silva/PJI1](https://github.com/flavios-silva/PJI1), com autoria e histórico preservados. As correções ficam na branch `melhorias/isolamento-e-diagnostico`; a `main` e o repositório original não foram alterados.

Esta aplicação usa Python, FastAPI, SQLAlchemy, PostgreSQL e Flet 0.84.0. Não é a aplicação Republic Java/Flet publicada anteriormente.

## Conferência das pontuações do professor

- [Achados, ferramentas, justificativas, ajustes, evidências e validações pendentes](docs/CONFERENCIA_TECNICA.md)
- [Resumo da primeira etapa e evolução](docs/PLANO_DE_APRIMORAMENTO.md)
- [Registro dos testes locais](docs/RESULTADOS_TESTES.txt)

O ciclo do checklist exige todos os itens e fotos obrigatórias antes do envio. O gestor aprova ou reprova com motivo; um checklist reprovado pode ser reaberto e reenviado. Modelos com histórico não são editados: crie outro modelo para novas rotinas.

## Executar em ambiente de teste

Copie `.env.example` para `.env` e configure valores privados. Gere um segredo aleatório; use senhas iniciais próprias, diferentes das contas pessoais. O Compose recusa configurações ausentes. Os administradores existentes não têm suas senhas automaticamente alteradas pela inicialização.

```sh
docker compose up --build
```

Interface local: http://localhost:8082. API local: http://localhost:8001. A API `/health` informa processo ativo; esse sinal sozinho não comprova login e banco.

O Compose prevê PostgreSQL 16 e volumes para banco e arquivos. O build completo, a integração em PostgreSQL e a implantação desta cópia ainda precisam ser validados. Configure HTTPS, endereços externos, backups e permissões antes de qualquer uso com dados reais.

## Reproduzir os testes locais

Em Python 3.12 e ambiente virtual:

```sh
python -m pip install -r backend/requirements.txt -r frontend/requirements.txt -r requirements-dev.txt
PYTHONPATH=backend python -m pytest tests/test_api_workflow.py tests/test_security_contracts.py -q
python -m unittest discover -s tests -p test_session_isolation.py -v
PYTHONPATH=frontend python tests/check_frontend_controls.py
python -m pip check
```

No Windows, adapte a definição de `PYTHONPATH` ao terminal. Backend e frontend têm pacotes com o mesmo nome `app`; execute seus testes em processos separados.

Os testes HTTP usam SQLite descartável, com chaves estrangeiras; o teste da interface constrói controles Flet com adaptadores e larguras lógicas. Isso não substitui PostgreSQL real, navegador, celular, leitor de tela ou validação com trabalhadores. Os limites e critérios para a validação estão no registro técnico.

## Proteção e limites

- Fotos e avatares são verificados com Pillow e entregues por links assinados de arquivo, válidos por 15 minutos. Recarregue a tela após expiração. O link pode ser usado por quem o receber durante a validade.
- Notificações são enviadas após commit. O gerenciador em memória pressupõe um processo; múltiplos processos exigem coordenação externa.
- Há bloqueios de perfil, configuração de produção e neutralização de fórmulas no CSV. Não há certificação de segurança ou conformidade integral de acessibilidade.
- Imagens antigas não são sobrescritas; a política de retenção e expurgo deve ser definida antes do uso real.
- Java, JavaScript autoral e um módulo equivalente de estoque não foram implementados nesta base. A equipe deve compatibilizar o relatório e as exigências da disciplina com o código efetivamente entregue.

## Persistência de fotos na demonstração
Novas fotos e avatares são armazenados no PostgreSQL (`media_assets`), sem depender do disco temporário do Render. Consomem a cota do banco e precisam entrar no backup. Leia [a solução, os limites e a validação](docs/PERSISTENCIA_DAS_IMAGENS.md). Arquivos antigos apenas no disco não são migrados automaticamente.
