📘 RUNBOOK – DSC Travel Seller Panel (v1)
1. Visão Geral

Sistema de apresentação de viagens para vendedores da DSC Travel.

Objetivo

Exibir viagens (voos, hotéis, passeios, orçamento)

Consumir dados via API própria

Operar em produção com alta previsibilidade

2. Arquitetura (Produção)
Usuário (Browser)
  ↓ HTTPS
painel.dsctravel.com.br  (Vercel / Frontend React)
  ↓ HTTPS
api.dsctravel.com.br     (Nginx)
  ↓
FastAPI (systemd service)
  ↓
Dados locais (JSON)  [fase atual]

3. Frontend
Stack

React 19

TypeScript

Vite

Tailwind CSS

shadcn/ui

Plataforma

Vercel

Repositório
https://github.com/diogenesdsctravel-spec/dsc-seller-panel

Variável de Ambiente CRÍTICA
VITE_API_BASE_URL=https://api.dsctravel.com.br


Sem essa variável, o frontend tentará acessar localhost e falhará.

Deploy

Deploy automático via Vercel

Build gerado a partir da branch main

URLs

Produção temporária:

https://dsc-seller-panel-eta.vercel.app


Produção canônica (DNS em propagação):

https://painel.dsctravel.com.br

4. Backend
Stack

Python 3

FastAPI

Uvicorn

Nginx (Reverse Proxy)

systemd (gerenciamento do serviço)

Servidor

Provedor: DigitalOcean

SO: Ubuntu 24.04 LTS

IP:

147.182.227.31

Diretório do Projeto
/var/www/dsc-seller-api

Serviço systemd

Nome do serviço:

dsc-seller-api

Comandos essenciais
systemctl status dsc-seller-api
systemctl restart dsc-seller-api
systemctl stop dsc-seller-api

Logs
journalctl -u dsc-seller-api -f

5. Endpoints
Health Check
GET https://api.dsctravel.com.br/ping


Resposta esperada:

{
  "status": "ok",
  "message": "mini-sistema-dsc online"
}

Trip Demo
GET https://api.dsctravel.com.br/trips/demo


Usado para:

teste

ambiente demo

bootstrap do frontend

6. CORS (Configuração Crítica)
Origens permitidas no backend

https://dsc-seller-panel.vercel.app

https://dsc-seller-panel-eta.vercel.app

http://localhost:5173

http://localhost:5174

Qualquer novo domínio do frontend exige inclusão explícita no CORS.

7. DNS
API
api.dsctravel.com.br
A → 147.182.227.31

Painel
painel.dsctravel.com.br
CNAME → *.vercel-dns.com

Verificação Vercel (temporária)
_vercel.dsctravel.com.br
TXT → vc-domain-verify=...


Após validação do domínio pelo Vercel, o TXT _vercel pode ser removido.

8. SSL
Backend

Let’s Encrypt

Certbot

Auto-renovação ativa

Frontend

Gerenciado automaticamente pelo Vercel

9. Checklist de Saúde (Produção)

Executar em caso de dúvida:

Backend responde?

https://api.dsctravel.com.br/ping


Dados retornam?

https://api.dsctravel.com.br/trips/demo


Frontend carrega dados?

https://painel.dsctravel.com.br


Console sem erros de:

CORS

404 / 500

Mixed Content

10. Regras Operacionais (Big Tech)
O que NÃO fazer

Não alterar DNS sem runbook

Não mexer em CORS “por tentativa”

Não subir frontend sem env vars

Não editar arquivos direto sem saber reiniciar o serviço

O que fazer

Sempre testar /ping

Sempre observar logs do systemd

Sempre versionar mudanças de frontend

Infra só muda com checklist

✅ STATUS ATUAL

✅ Sistema funcional fim-a-fim

✅ Infra estável

✅ Deploy previsível

✅ Domínio em finalização

✅ Base pronta para evolução de produto