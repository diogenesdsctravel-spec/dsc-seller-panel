# DSC Travel - Seller Panel

Painel profissional para vendedores criarem apresentações de viagens personalizadas.

## �� Visão Geral

Sistema interno da DSC Travel que permite vendedores transformarem orçamentos crus (PDFs, prints) em apresentações premium para clientes, com extração automática via IA.

**Status:** ✅ MVP Funcional - Arquitetura Big Tech

---

## 🚀 Stack Tecnológica

- **React 19** - UI Library
- **TypeScript 5** - Type Safety
- **Vite 7** - Build Tool
- **Tailwind CSS 3** - Styling
- **shadcn/ui** - Component Library
- **lucide-react** - Icons
- **FastAPI** - Backend (Python)

---

## 📁 Estrutura do Projeto
```
seller-panel/
├── src/
│   ├── components/          # Componentes React
│   │   ├── ui/             # shadcn/ui components
│   │   ├── products/       # Product cards (Flight, Hotel, Tour)
│   │   ├── LoadingState.tsx
│   │   ├── ErrorState.tsx
│   │   ├── EmptyState.tsx
│   │   ├── TripHeader.tsx
│   │   ├── TripSummary.tsx
│   │   ├── BudgetSection.tsx
│   │   ├── ProductsSection.tsx
│   │   └── RawDataPanel.tsx
│   ├── hooks/              # Custom React hooks
│   │   └── useTrip.ts
│   ├── services/           # API communication
│   │   └── tripService.ts
│   ├── types/              # TypeScript interfaces
│   │   └── trip.ts
│   ├── utils/              # Utility functions
│   │   └── formatters.ts
│   ├── lib/                # Third-party configs
│   │   └── utils.ts
│   ├── App.tsx             # Main component
│   └── main.tsx            # Entry point
```

---

## 🏃 Como Rodar

### Pré-requisitos

- Node.js 18+
- npm ou yarn
- Backend rodando em `http://127.0.0.1:8000`

### Instalação
```bash
# Instalar dependências
npm install

# Rodar em desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview da build
npm run preview
```

O painel estará disponível em `http://localhost:5173`

---

## 🏗️ Arquitetura

### Separação de Responsabilidades

- **Components:** UI pura, recebe props, sem lógica de negócio
- **Hooks:** Gerenciamento de estado e efeitos colaterais
- **Services:** Comunicação com APIs externas
- **Types:** Contratos de dados TypeScript
- **Utils:** Funções puras reutilizáveis

### Fluxo de Dados
```
API (Backend) → tripService → useTrip → Components → UI
```

### Componentes Principais

- `App.tsx` - Orquestração principal (28 linhas)
- `ProductsSection` - Exibe voos, hotéis, passeios
- `BudgetSection` - Mostra pacote base + opcionais
- `TripSummary` - Resumo da viagem
- `RawDataPanel` - Debug view dos dados

---

## 🎨 Padrões de Código

### TypeScript
```typescript
// ✅ Bom - Props tipadas
interface TripHeaderProps {
  tripId: string;
  clientName: string;
}

// ❌ Evitar - any
const data: any = {}
```

### Componentes
```typescript
// ✅ Bom - Componente funcional com props tipadas
export function FlightCard({ flight }: FlightCardProps) {
  return <Card>...</Card>
}

// ❌ Evitar - Inline styles
<div style={{ color: 'red' }}>...</div>
```

### Tailwind
```typescript
// ✅ Bom - Classes utilitárias
<div className="flex items-center gap-3">

// ❌ Evitar - Inline styles
<div style={{ display: 'flex' }}>
```

---

## 📦 API Integration

### Endpoint
```
GET http://127.0.0.1:8000/trips/{trip_id}
```

### Response Format
```typescript
{
  trip_id: "demo",
  status: "ok",
  data: {
    cliente: "Kennedy",
    periodo: { inicio: "15/02", fim: "22/02" },
    voos: [...],
    hoteis: [...],
    passeios: [...],
    pacote_base: { descricao: "...", valor: 6656 }
  }
}
```

---

## 🔄 Próximos Passos

- [ ] Upload de arquivos (PDFs, prints)
- [ ] Extração com IA
- [ ] Edição manual dos dados
- [ ] Simulador de iPhone
- [ ] Geração de link público
- [ ] Testes automatizados

---

## 👨‍💻 Desenvolvimento

### Adicionar novo componente
```bash
# Criar arquivo
touch src/components/NomeDoComponente.tsx

# Template
import { Card } from "./ui/card";

interface NomeDoComponenteProps {
  // props aqui
}

export function NomeDoComponente({ }: NomeDoComponenteProps) {
  return <Card>...</Card>
}
```

### Adicionar nova rota de API
```typescript
// src/services/tripService.ts
export async function novaFuncao(id: string) {
  const response = await fetch(`${API_BASE_URL}/nova-rota/${id}`);
  return response.json();
}
```

---

## 📝 Licença

Propriedade da DSC Travel. Uso interno apenas.

---

**Desenvolvido com ❤️ por DSC Travel**
