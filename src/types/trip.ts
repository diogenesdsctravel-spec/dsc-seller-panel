export interface Trip {
  trip_id: string;
  status: string;
  data: TripData;
}

export interface TripData {
  cliente?: string;
  periodo?: {
    inicio: string;
    fim: string;
  };
  voos?: Flight[];
  hoteis?: Hotel[];
  passeios?: Tour[];
  pacote_base?: BasePackage;
}

export interface Flight {
  origem: string;
  destino: string;
  data: string;
  horario_saida: string;
  horario_chegada: string;
}

export interface Hotel {
  cidade: string;
  nome: string;
  noites: number;
  checkin: string;
  checkout: string;
  regime: string;
}

export interface Tour {
  nome: string;
  valor_por_pessoa: number;
  incluido: boolean;
}

export interface BasePackage {
  descricao: string;
  valor: number;
}
