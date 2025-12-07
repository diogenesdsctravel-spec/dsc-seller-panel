from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from datetime import datetime
import json
from typing import Any, Dict
from pydantic import BaseModel

app = FastAPI()

# CORS para frontends conhecidos
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dsc-seller-panel.vercel.app",
        "https://dsc-seller-panel-eta.vercel.app",
        "https://painel.dsctravel.com.br",
        "http://localhost:5173",
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
EXTRACAO_PATH = BASE_DIR / "extracao" / "extracao_simulada.json"


class TripResponse(BaseModel):
    trip_id: str
    status: str
    data: Dict[str, Any]


# Modelos do /trips/simulate (contrato v1)
class TripSimulationRequest(BaseModel):
    cliente: Dict[str, Any] | None = None
    origem: str
    destino: str
    data_ida: str
    data_volta: str
    flexibilidade_datas: bool | None = None
    classe: str | None = None
    observacoes: str | None = None


class TripResumo(BaseModel):
    destino: str
    dias: int
    tipo: str


class TripSimulationDetailAereo(BaseModel):
    companhia: str
    classe: str
    preco_estimado: float


class TripSimulationDetailHospedagem(BaseModel):
    tipo: str
    noites: int
    preco_estimado: float


class TripSimulationData(BaseModel):
    aereo: TripSimulationDetailAereo
    hospedagem: TripSimulationDetailHospedagem


class TripSimulationResponse(BaseModel):
    trip_id: str
    status: str
    resumo: TripResumo
    simulacao: TripSimulationData


@app.get("/")
def root():
    return {"message": "DSC Seller API - Online", "status": "ok"}


@app.get("/ping")
def ping():
    return {"status": "ok", "message": "mini-sistema-dsc online"}


@app.get("/trips/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: str):
    if trip_id == "demo":
        try:
            with open(EXTRACAO_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return TripResponse(trip_id="demo", status="ok", data=data)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Arquivo de extração não encontrado")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Erro ao ler arquivo JSON")

    return TripResponse(
        trip_id=trip_id,
        status="stub",
        data={"message": f"Trip {trip_id} não implementado ainda"}
    )


def _calcular_dias(data_ida: str, data_volta: str) -> int:
    try:
        d1 = datetime.fromisoformat(data_ida)
        d2 = datetime.fromisoformat(data_volta)
        return max((d2 - d1).days, 0)
    except Exception:
        return 0


@app.post("/trips/simulate", response_model=TripSimulationResponse)
def simulate_trip(payload: TripSimulationRequest):
    dias = _calcular_dias(payload.data_ida, payload.data_volta)
    tipo = "Internacional" if payload.destino not in {"GIG", "GRU", "CNF", "SSA"} else "Nacional"

    trip_id = f"sim_{payload.origem.lower()}_{payload.destino.lower()}"

    aereo = TripSimulationDetailAereo(
        companhia="Companhia Demo",
        classe=(payload.classe or "economica").capitalize(),
        preco_estimado=4200.0,
    )

    hospedagem = TripSimulationDetailHospedagem(
        tipo="Hotel 4 estrelas",
        noites=dias if dias > 0 else 5,
        preco_estimado=3800.0,
    )

    resumo = TripResumo(
        destino=payload.destino,
        dias=dias if dias > 0 else 5,
        tipo=tipo,
    )

    simulacao = TripSimulationData(
        aereo=aereo,
        hospedagem=hospedagem,
    )

    return TripSimulationResponse(
        trip_id=trip_id,
        status="simulated",
        resumo=resumo,
        simulacao=simulacao,
    )
