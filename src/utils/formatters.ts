import { TripData } from '../types/trip';

export function getClientName(data: TripData): string {
  return data.cliente || "Cliente";
}

export function getTripSummary(data: TripData): string {
  return data.resumo || data.descricao || data.descricaoGeral || "";
}
