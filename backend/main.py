from image_search import get_hero_image_for_trip, get_images_for_all_cities

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import uuid
from typing import Any, Dict, List
from pydantic import BaseModel
import shutil

app = FastAPI(
    title="DSC Travel API",
    description="API para gerenciamento de viagens e extrações",
    version="0.1.0"
)

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
UPLOADS_DIR = BASE_DIR / "uploads"
EXTRACAO_DIR = BASE_DIR / "extracao"

UPLOADS_DIR.mkdir(exist_ok=True)
EXTRACAO_DIR.mkdir(exist_ok=True)


class TripResponse(BaseModel):
    trip_id: str
    status: str
    data: Dict[str, Any]


class UploadResponse(BaseModel):
    trip_id: str
    status: str
    message: str
    files: List[str]


def extract_cities_from_trip(trip: Dict[str, Any]) -> List[str]:
    """Extrai lista de cidades de um objeto de viagem."""
    cidades = []

    # Tenta extrair de "destinations"
    destinos = trip.get("destinations") or trip.get("destinos") or []
    if isinstance(destinos, list):
        for d in destinos:
            if isinstance(d, dict):
                nome = d.get("city") or d.get("cidade") or d.get("name") or d.get("nome")
                if nome and nome not in cidades:
                    cidades.append(str(nome))
        if cidades:
            return cidades

    # Tenta extrair de "days"
    dias = trip.get("days") or trip.get("dias") or []
    if isinstance(dias, list):
        for dia in dias:
            if isinstance(dia, dict):
                cidade = dia.get("city") or dia.get("cidade")
                if cidade and cidade not in cidades:
                    cidades.append(str(cidade))

    # Cidade única no root
    unica = trip.get("city") or trip.get("cidade")
    if unica:
        cidades.append(str(unica))

    return cidades


@app.get("/")
def root():
    return {"message": "DSC Seller API - Online", "status": "ok", "version": "0.1.0"}


@app.get("/ping")
def ping():
    return {"status": "ok", "message": "mini-sistema-dsc online"}


@app.post("/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    trip_id = f"trip_{uuid.uuid4().hex[:12]}"
    trip_folder = UPLOADS_DIR / trip_id
    trip_folder.mkdir(exist_ok=True)

    saved_files = []

    try:
        for file in files:
            file_path = trip_folder / file.filename
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(file.filename)

        return UploadResponse(
            trip_id=trip_id,
            status="uploaded",
            message=f"{len(saved_files)} arquivo(s) enviado(s) com sucesso",
            files=saved_files
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer upload: {str(e)}")


@app.get("/trips/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: str):
    """
    Retorna dados de uma viagem.
    Automaticamente busca imagens hero e por cidade.
    """
    if trip_id == "demo":
        try:
            with open(EXTRACAO_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Erro ao ler JSON")
    else:
        extracao_file = EXTRACAO_DIR / f"{trip_id}.json"

        if not extracao_file.exists():
            raise HTTPException(status_code=404, detail=f"Viagem {trip_id} não encontrada")

        try:
            with open(extracao_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Erro ao ler dados")

    # Extrair cidades e buscar imagens
    cidades = extract_cities_from_trip(data)

    if cidades:
        hero = get_hero_image_for_trip(cidades)
        imagens_por_cidade = get_images_for_all_cities(cidades)
        data["heroImage"] = hero
        data["cityImages"] = imagens_por_cidade
    else:
        data["heroImage"] = None
        data["cityImages"] = {}

    return TripResponse(trip_id=trip_id, status="ok", data=data)


@app.post("/extract/{trip_id}")
async def extract_trip_data(trip_id: str):
    """Extrai dados dos arquivos enviados usando IA."""
    from extract_with_ai import extract_travel_data

    trip_folder = UPLOADS_DIR / trip_id

    if not trip_folder.exists():
        raise HTTPException(status_code=404, detail=f"Trip {trip_id} não encontrado")

    try:
        extracted_data = extract_travel_data(trip_folder)

        extracao_file = EXTRACAO_DIR / f"{trip_id}.json"
        with extracao_file.open("w", encoding="utf-8") as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)

        return {
            "trip_id": trip_id,
            "status": "extracted",
            "message": "Dados extraídos com sucesso"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na extração: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)