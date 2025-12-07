import { Trip } from "../types/trip";

const API_BASE_URL = import.meta.env.VITE_API_URL || "https://api.dsctravel.com.br";

export async function getTrip(tripId: string): Promise<Trip> {
  try {
    const response = await fetch(`${API_BASE_URL}/trips/${tripId}`);

    if (!response.ok) {
      throw new Error(`Erro ao buscar viagem. Status ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Erro em getTrip:", error);
    throw error;
  }
}
