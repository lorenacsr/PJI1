# Plano de aprimoramento da cópia PJI1

Origem: https://github.com/flavios-silva/PJI1, main no commit 7135ce3. Autoria e histórico preservados.

## Evolução da conferência

A primeira etapa isolou AppState por sessão e acrescentou regressão para duas páginas. A etapa ampliada corrigiu regras de submissão, revisão, fotos, permissões, preservação do histórico, notificações após commit, CSV, configuração e compatibilidade com Flet 0.84.0.

A relação detalhada das observações, ferramentas e justificativas, mudanças e critérios de validação está em [CONFERENCIA_TECNICA.md](CONFERENCIA_TECNICA.md). As saídas locais estão em [RESULTADOS_TESTES.txt](RESULTADOS_TESTES.txt).

## Pendências de validação

1. Integração real com PostgreSQL e ensaios de concorrência/migração.
2. Build de contêineres e publicação desta cópia, sem confundir com a aplicação Java/Flet anterior.
3. Login, restauração de sessão, seleção de fotos, exportação e notificações em navegadores e aparelhos reais.
4. Auditoria de teclado, foco, leitor de tela, zoom e contraste de todas as telas.
5. Revisão do escopo Java/JavaScript/insumos em relação às exigências e ao documento escolhido pelo grupo.
6. Backup/restauração, retenção de imagens, recuperação de acesso e avaliação com responsáveis do estabelecimento.

Nenhuma aprovação do professor ou validação de campo foi presumida. Não foi enviado pull request ao autor original.
