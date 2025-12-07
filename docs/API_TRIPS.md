Perfeito. **Aqui está o documento ÚNICO**, pronto para **copiar e colar inteiro** em
`docs/API_TRIPS.md`.
Sem quebras, sem comentários, sem instruções extras.

---

````md
# Trips API

API responsável por orquestrar o fluxo de criação, simulação e retorno de viagens
no Mini Sistema DSC.

Este documento define o CONTRATO da API.  
Tudo que está aqui é considerado estável para o frontend.

---

## Informações Gerais

Base URL (produção):
https://painel.dsctravel.com.br/api

Formato:
JSON

Autenticação:
Não obrigatória (MVP)

---

## Visão Geral

A Trips API permite:

- Criar uma requisição de viagem
- Normalizar requisitos do cliente
- Gerar uma simulação estruturada de viagem
- Retornar dados prontos para apresentação

Consumidores desta API:
- Seller Panel (Frontend)
- Simuladores internos
- Futuras automações

---

## POST /trips/simulate

Cria uma simulação de viagem com base nos dados informados.

### Request

```json
{
  "cliente": {
    "nome": "João Silva",
    "perfil": "casal"
  },
  "origem": "GRU",
  "destino": "LIS",
  "data_ida": "2025-03-10",
  "data_volta": "2025-03-20",
  "flexibilidade_datas": true,
  "classe": "economica",
  "observacoes": "Viagem de aniversário"
}
````

### Regras de entrada

* Datas no formato ISO 8601 (YYYY-MM-DD)
* Campos desconhecidos são ignorados
* Campos opcionais podem ser omitidos
* Valores ausentes utilizam defaults do sistema

---

### Response 200 – Simulação criada

```json
{
  "trip_id": "trip_8f29a",
  "status": "simulated",
  "resumo": {
    "destino": "Lisboa",
    "dias": 10,
    "tipo": "Internacional"
  },
  "simulacao": {
    "aereo": {
      "companhia": "TAP",
      "classe": "Economica",
      "preco_estimado": 4200
    },
    "hospedagem": {
      "tipo": "Hotel 4 estrelas",
      "noites": 10,
      "preco_estimado": 3800
    }
  }
}
```

---

## GET /trips/{trip_id}

Retorna os dados de uma viagem previamente criada.

### Response 200

```json
{
  "trip_id": "trip_8f29a",
  "status": "simulated",
  "data": {
    "mensagem": "Trip disponível para revisão"
  }
}
```

---

## Status da Trip

Os estados possíveis de uma viagem são:

* `draft` – criada, dados incompletos
* `simulated` – simulação gerada
* `reviewed` – revisada pelo vendedor
* `sent` – enviada ao cliente
* `archived` – finalizada ou descartada

---

## Erros

### Response 400 – Dados inválidos

```json
{
  "error": "invalid_request",
  "message": "Campos obrigatórios ausentes"
}
```

### Response 404 – Trip não encontrada

```json
{
  "error": "not_found",
  "message": "Trip não encontrada"
}
```

---

## Garantias do Contrato

* Campos documentados não serão removidos sem versionamento
* Quebra de contrato exige nova versão da API
* O frontend pode confiar neste documento como fonte única da verdade

---

## Versionamento

Versão atual:
v1 (MVP)

Evoluções futuras manterão compatibilidade retroativa sempre que possível.

```

---

✅ **Isso é padrão Big Tech.**  
✅ **Isso é contrato.**  
✅ **Frontend pode seguir sem medo.**

Se quiser, o próximo passo correto é:
- versionar (`/v1/trips`)
- gerar testes de contrato
- ou desenhar a V2

Você decide.
```

