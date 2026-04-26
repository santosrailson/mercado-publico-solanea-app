# 📥 Importação de Cessionários do PDF

Este diretório contém os arquivos necessários para reimportar os cessionários que estavam no PDF de relatório.

## Arquivos

- `importar_cessionarios.py` — Script Python para importar os dados
- `cessionarios_pdf.txt` — Texto extraído do PDF com todos os cessionários

## Como usar no Hostinger

### Passo 1: Copiar os arquivos para o servidor

Envie esses dois arquivos para a pasta do projeto no Hostinger (ex: `~/mercado-publico-solanea-app/backend/scripts/`).

### Passo 2: Copiar para dentro do container Docker

Acesse o servidor via SSH e rode:

```bash
cd ~/mercado-publico-solanea-app/backend/scripts

docker cp importar_cessionarios.py mercado-backend:/app/
docker cp cessionarios_pdf.txt mercado-backend:/app/
```

> Se o nome do container for diferente, descubra com: `docker ps`

### Passo 3: Executar o script de importação

```bash
docker exec mercado-backend python /app/importar_cessionarios.py /app/cessionarios_pdf.txt /app/data/mercado.db
```

### Passo 4: Próximos passos (pelo sistema web)

1. Acesse `http://seu-dominio.com/fiscais` e cadastre os fiscais
2. Acesse `http://seu-dominio.com/cessionarios` e edite cada cessionário para:
   - Adicionar o **telefone**
   - Selecionar o **fiscal responsável**

---

## ⚠️ Importante

- O script **não apaga** dados existentes. Ele apenas insere os que ainda não estão no banco.
- Se rodar o script duas vezes, ele vai pular os duplicados.
- Os cessionários são importados com `periodicidade_referencia = 'Mensal'` por padrão.

## Resultado esperado

```
Total de cessionários encontrados no arquivo: 83
Inseridos: 82
Duplicados (pulados): 1
```
