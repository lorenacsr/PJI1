# Persistência das imagens na demonstração acadêmica

## Problema e solução
O disco de um serviço gratuito do Render é temporário. Fotos de checklist e avatares novos passam a ser armazenados na tabela `media_assets` do PostgreSQL, em vez desse disco. O conteúdo e sua referência são gravados na mesma transação: se ela falhar, ambos são revertidos. A inicialização cria a nova tabela sem apagar tabelas existentes.

A aplicação continua verificando o formato real, o tamanho e as dimensões das imagens. Mantêm-se os limites de 5 MB por foto de checklist e 3 MB por avatar. A leitura exige o link assinado temporário já implementado. Nenhuma credencial é adicionada ao GitHub.

## Alcance e limites
Reiniciar ou republicar o Render não apaga as imagens armazenadas no banco externo. Isso não protege de exclusão do banco, perda da conta, esgotamento da cota, incidente do provedor ou exclusão administrativa. Não há garantia de disponibilidade permanente. Imagens e registros consomem a mesma cota do Neon; use apenas dados fictícios e poucas imagens na demonstração.

Arquivos de instalações antigas que estejam somente no disco não são migrados automaticamente. A leitura local foi preservada por compatibilidade; esses arquivos precisam ser copiados/migrados antes de uma nova publicação. O banco isolado desta cópia foi criado vazio; não se deve copiar dados da aplicação anterior sem necessidade.

## Cópia de segurança
O backup lógico completo com `pg_dump` inclui a tabela de imagens e as demais tabelas. A equipe deve guardar a cópia em local privado, separado do serviço, e testar a restauração em outro banco. Não publicar dumps no GitHub, pois podem conter informações e hashes de senha. Não foi configurada uma rotina automática de backup nem validada a restauração nesta etapa. Persistência não substitui backup.

## Justificativa da escolha
Para uma demonstração acadêmica de pequeno volume, usar o PostgreSQL já disponível reduz dependências e dispensa contratar disco persistente. Para uso empresarial ou maior volume, recomenda-se avaliar armazenamento de objetos privado, política de retenção, cópias de segurança, recuperação, disponibilidade e custo total. Não se afirma que o armazenamento de imagens no banco seja a melhor opção para qualquer escala.

## Verificação
O teste HTTP do fluxo completo verifica gravação dos bytes no banco, ausência de arquivo local, descarte da conexão anterior e recuperação da mesma imagem com nova conexão. A suíte local com SQLite passou (26 casos); isso não equivale a uma reinicialização real no Render. A validação após publicação continua pendente.

Referências oficiais consultadas em 25 out. 2026:
- RENDER. Deploy for Free. https://render.com/docs/free
- NEON. Pricing. https://neon.com/pricing
- POSTGRESQL GLOBAL DEVELOPMENT GROUP. pg_dump. https://www.postgresql.org/docs/current/app-pgdump.html
