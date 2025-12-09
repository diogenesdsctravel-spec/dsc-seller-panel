import { useState, useEffect } from "react";
import { getTrip } from "../services/tripService";
import type { Trip } from "../types/trip";

export function useTrip(tripId: string) {
  const [trip, setTrip] = useState<Trip | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTrip = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getTrip(tripId);
      setTrip(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrip();
  }, [tripId]);

  return { trip, loading, error, refetch: fetchTrip };
}